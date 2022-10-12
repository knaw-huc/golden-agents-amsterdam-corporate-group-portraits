import os
import uuid
import datetime
import json
import re
from itertools import count, product
from collections import defaultdict

import pandas as pd

from dateutil import parser as dateParser

import rdflib
from rdflib import Graph, URIRef, Literal, XSD, Namespace, BNode, OWL
from rdfalchemy import rdfSubject, rdfMultiple, rdfSingle

from ga import *

ns = Namespace("https://data.goldenagents.org/datasets/corporatiestukken/")
gaPersonName = Namespace("https://data.goldenagents.org/datasets/personname/")

rdflib.graph.DATASET_DEFAULT_GRAPH_ID = ns

nsArtwork = Namespace(
    "https://data.goldenagents.org/datasets/corporatiestukken/artwork/")

afkortingen = {
    "Amh": "Aalmoezeniershuis",
    "Awh": "Aalmoezeniershuis",  #Check?
    "Amwh": "Aalmoezeniersweeshuis",
    "Bwh": "Burgerweeshuis",
    "CM": "Collegium Medicum",
    "Dh": "Dolhuis",
    "Gh": "Gasthuizen",
    "Lh": "Leprozenhuis",
    "NZHh": "Nieuwezijds Huiszittenhuis",
    "No.K.": "Noorderkerk",
    "Nz.K.": "Nieuwezijds Kapel",
    "Oz.K.": "Oudezijds Kapel",
    "E.K.": "Eilandskerk",
    "A.K.": "Amstelkerk",
    "N.K.": "Nieuwe Kerk",
    "O.K.": "Oude Kerk",
    "Z.K.": "Zuiderkerk",
    "W.K.": "Westerkerk",
    "Oo.K.": "Oosterkerk",
    "N.W.K.": "Nieuwe Walenkerk",
    "OZHh": "Oudezijds Huiszittenhuis",
    "OMVGh": "Oude Mannen- en Vrouwengasthuis",
    "Rh": "Rasphuis",
    "SJh": "Sint Jorishof",
    "Sph": "Spinhuis",
    "SphNWh": "Spin- en Nieuwe Werkhuis",
    "Wwh": "Walenweeshuis",
    "Wwh.A.": "Walenweeshuis",  # TODO
    "Wwh.D.": "Walenweeshuis",  # TODO
    "Zwh": "Zijdewindhuis",
    "A.A.": "Admiraliteit te Amsterdam",
    "CM": "Collegium Medicum",
    "H.Stede": "Heilige Stede",
    "RCAk": "Rooms-Catholijck Armenkantoor",
    "Vd": "Voetboogdoelen",
    "Hd": "Handboogdoelen",
    "Kd": "Kloveniersdoelen",
    "stadssoldaten": "Stadssoldaten"
}

functies = {
    "doct.med.": "medisch doctor",
    "havenm.": "havenmeester",
    "insp.": "inspecteur",
    "kap.": "kapitein",
    "kapluit.": "kapitein luitenant",
    "k.": "keurmeester",
    "km.": "kerkmeester",
    "kol.": "kolonel",
    "kolgen.": "kolonel generaal",
    "luit.": "luitenant",
    "luitkol.": "luitenant kolonel",
    "ov.": "overman",
    "serg.": "sergeant",
    "vaand.": "vaandrig",
    "tamboer": "tamboer",
    "overm.": "overman",
    "schout": "schout",
    "kastelein": "kastelein",
    "maj.": "majoor",
    "provoost": "provoost",
    "hopman": "hopman",
}

bestuursfuncties = {
    "Sch.": "Schepen",
    "R.": "Raad",
    "C.": "Commissaris",
    "C100p.": "Commissaris 100ste penning",
    "B.": "Burgemeester",
    "Secr.": "Secretaris",
    "C.H.": "Commissaris Huwelijkse Zaken",
    "C.K.Z.": "Commissaris Kleine Zaken",
    "S.": "Schout",
    "Onderschout": "Onderschout",
    "Pens.": "Pensionaris",
    "C.E.": "Commissaris Grooten Excijs",
    "C.Z.": "Commissaris Zeezaken",
    "Wm.": "Weesmeester",
    "C.D.B.": "Commissaris Desolate Boedelskamer",
    "C.B.L.": "Commissaris Bank van Lening",
    "Th.E.": "Thesaurier Extraordinaris",
    "Th.": "Thesaurier Ordinaris",
    "Am.": "Assurantiemeester",
    "C.Wb.": "Commissaris Wisselbank",
    "G.R.": "Gecommitteerde Raad",
    "Gecomm.Raad": "Gecommitteerde Raad",
    "G.R.K.": "Gedeputeerde ter Generaliteits Rekenkamer",
    "HSchout": "Hoofdschout",
    "Subst.scht.extr.": "Substituut-schout Extraordinaris",
    "Ordinaris": "Raad Ordinaris",
    "Gedep.TerStaten": "Gedeputeerde ter Staten",
    "Gedep.TerStatenGeneraal": "Gedeputeerde ter Staten Generaal",
    "Raad.ter.admir.": "Raad ter Admiraliteit",
    "A.N.": "Raad ter Admiraliteit in ‘t Noorderkwartier",
    "ov.": "Overman",
    "Rm.": "Rekenmeester",
    "R.H.":
    "Gecommitteerde ter Rekenkamer ter Auditie van Holland in het Zuiderkwartier",
    "ov.WKG": "Overman Wijnkopersgilde",
    "Secr.Z.": "Secretaris Zeezaken",
    "Secr.Th.E.": "Secretaris-thesaurier Extraordinaris",
    "Boekh200p.": "Boekhouder 200ste penning",
    "OCW": "Oppercommissaris der Walen"
}

# abbreviations = {
# Hd = "Handboogdoelen"
# Kd = "Kloveniersdoelen"
# Vd = "Voetboogdoelen"
# kap. = "kapitein"
# luit. = "luitenant"
# vaand. = "vaandrig"
# kol. = "kolonel"
# serg. = "sergeant"
# W. = "Wijk"
# reg. = "regent / regentes"
# ov. = "overman (-n. = onvervulde nominatie)"
# insp. = "inspecteur"
# doct. med. = "medisch doctor"
# m.p. = "jaar van meesterproef"
# d. = "deken"
# k. = "keurmeester"
# comm. = "oppercommissaris"
# havenm. = "havenmeester"
# OZ = "Oude Zijde / Oudezijds"
# NZ = "Nieuwe Zijde / Nieuwezijds",
# }


def unique(*args, sep="", ns=None):
    """Function to generate a unique BNode based on a series of arguments.

    Uses the uuid5 function to generate a uuid from one or multiple ordered
    arguments. This way, the BNode function of rdflib can be used, without the
    need to filter strange characters or spaces that will break the serialization.

    Returns:
        BNode: Blank node with identifier that is based on the function's input.
    """

    identifier = "".join(str(i) for i in args)  # order matters

    unique_id = uuid.uuid5(uuid.NAMESPACE_X500, identifier)

    if ns:
        return ns.term(str(unique_id))
    else:
        return BNode(unique_id)


def main(loadData=None):

    #######
    # RDF #
    #######

    # Poorters
    df1 = pd.read_csv(
        'data/Middelkoop diss. dl. 2 - bijlage 4a - mannelijke poorters.csv')
    df1 = df1.where((pd.notnull(df1)), None)

    toRDF(
        df1.to_dict(orient='records'),
        uri=ns.term('poorters/'),
        name=Literal("Mannelijke poorters", lang='nl'),
        description=Literal(
            "Lijst van mannelijke poorters in functies als instellingsregent, kerkmeester, officier der schutterij en/of ten stadhuize, ca. 1500 – ca. 1795",
            lang='nl'),
        filename=
        "Middelkoop diss. dl. 2 - bijlage 4a - mannelijke poorters.csv",
        target='trig/poorters.trig')

    # Regentessen
    df2 = pd.read_csv(
        'data/Middelkoop diss. dl. 2 - bijlage 4b - regentessen.csv')
    df2 = df2.where((pd.notnull(df2)), None)
    toRDF(
        df2.to_dict(orient='records'),
        uri=ns.term('regentessen/'),
        name=Literal("Regentessen", lang='nl'),
        description=Literal(
            "Lijst van regentessen van zorg- en tuchtinstellingen, ca. 1578 – ca. 1795",
            lang='nl'),
        filename="Middelkoop diss. dl. 2 - bijlage 4b - regentessen.csv",
        target='trig/regentessen.trig')

    # Regenten
    df3 = pd.read_csv(
        'data/Middelkoop diss. dl. 2 - bijlage 4c - regenten Walenweeshuis.csv'
    )
    df3 = df3.where((pd.notnull(df3)), None)
    toRDF(df3.to_dict(orient='records'),
          uri=ns.term('regenten/'),
          name=Literal("Regenten Walenweeshuis", lang='nl'),
          description=Literal(
              "Lijst van regenten van het Walenweeshuis, 1631 – 1800",
              lang='nl'),
          filename=
          "Middelkoop diss. dl. 2 - bijlage 4c - regenten Walenweeshuis.csv",
          target='trig/regenten.trig')

    # Gildeleden
    df4 = pd.read_csv(
        'data/Middelkoop diss. dl. 2 - bijlage 4d - geportretteerde gildenleden.csv'
    )
    df4 = df4.where((pd.notnull(df4)), None)
    toRDF(
        df4.to_dict(orient='records'),
        uri=ns.term('gildenleden/'),
        name=Literal("Geportretteerde gildenleden", lang='nl'),
        description=Literal(
            "Lijst van geportretteerde leden van ambachtsgilden, inspecteurs van het Collegium Medicum en Oppercommissarissen der Walen, 1599 – 1795",
            lang='nl'),
        filename=
        "Middelkoop diss. dl. 2 - bijlage 4d - geportretteerde gildenleden.csv",
        target='trig/gildenleden.trig')

    # Artwork dataset
    df5 = pd.read_csv('data/corporatiestukken.csv')
    df5 = df5.where((pd.notnull(df5)), None)
    toRDF(df5.to_dict(orient='records'),
          uri=ns.term('corporatiestukken/'),
          name=Literal("Overzicht van Amsterdamse corporatiestukken",
                       lang='nl'),
          description="Overgenomen uit appendix 3 (Middelkoop 2019).",
          filename="corporatiestukken.csv",
          target='trig/corporatiestukken.trig')


def getPersonName(d):

    # surnamePrefixes = ['de', 'van', 'la', 'der', 'du']
    surnamePrefixes = ['van', 'de', 'den', 'des', 'der', 'ten', "l'", "d'"]
    pns = []
    labels = []

    prefixes = d['Titel'].split(
        ' / ') if d['Titel'] and d['Titel'] != "*" else [None]
    givenNames = d['Voornaam'].split(' / ') if d['Voornaam'] else [None]
    patronyms = d['Patroniem en tussenvoegsel'].split(
        ' / ') if d['Patroniem en tussenvoegsel'] else [None]
    baseSurnames = d['Achternaam'].split(' / ') if d['Achternaam'] else [None]

    for prefix, givenName, patronymSurnamePrefix, baseSurname in product(
            prefixes, givenNames, patronyms, baseSurnames):

        if prefix:
            prefix = prefix.strip()
        if givenName:
            givenName = givenName.strip()
        if patronymSurnamePrefix:
            patronym = " ".join([
                i for i in patronymSurnamePrefix.split(' ')
                if i not in surnamePrefixes
            ]).strip()

            surnamePrefix = " ".join([
                i for i in patronymSurnamePrefix.split(' ')
                if i in surnamePrefixes
            ]).strip()

            if surnamePrefix == "":
                surnamePrefix = None
            if patronym == "":
                patronym = None
        else:
            patronym = None
            surnamePrefix = None

        if ', ' in baseSurname:
            baseSurname, disambiguatingDescription = baseSurname.split(', ', 1)
            disambiguatingDescription = disambiguatingDescription.strip()
        else:
            disambiguatingDescription = None

        literalName = " ".join([
            i for i in [
                prefix, givenName, patronym, surnamePrefix, baseSurname,
                disambiguatingDescription
            ] if i is not None
        ])
        labels.append(literalName)

        identifier = unique(prefix,
                            givenName,
                            patronym,
                            surnamePrefix,
                            baseSurname,
                            disambiguatingDescription,
                            literalName,
                            sep='@ga@',
                            ns=gaPersonName)

        pn = PersonName(identifier,
                        prefix=prefix,
                        givenName=givenName,
                        patronym=patronym,
                        surnamePrefix=surnamePrefix,
                        baseSurname=baseSurname,
                        disambiguatingDescription=disambiguatingDescription,
                        literalName=literalName,
                        label=[literalName])

        pns.append(pn)

    return pns, labels


def parsePersonName(nameString, identifier=None):
    """
    Parse a capitalised Notary Name from the notorial acts to pnv format.

    Args:
        full_name (str): Capitalised string

    Returns:
        PersonName: according to pnv
    """

    pns = []
    labels = []

    for full_name in nameString.split(' / '):

        # Some static lists
        dets = ['van', 'de', 'den', 'des', 'der', 'ten', "l'", "d'"]
        prefixes = ['Mr.']
        suffixes = ['Jr.', 'Sr.']
        patronymfix = ('sz', 'sz.', 'szoon', 'dr.', 'dr')

        # Correcting syntax errors
        full_name = full_name.replace('.', '. ')
        full_name = full_name.replace("'", "' ")
        full_name = full_name.replace('  ', ' ')

        # Tokenise
        tokens = full_name.split(' ')
        tokens = [i.lower() for i in tokens]
        tokens = [i.title() if i not in dets else i for i in tokens]
        full_name = " ".join(
            tokens
        )  # ALL CAPS to normal name format (e.g. Mr. Jan van Tatenhove)
        full_name = full_name.replace(
            "' ", "'")  # clunk back the apostrophe to the name

        # -fixes
        infix = " ".join(i for i in tokens if i in dets).strip()
        prefix = " ".join(i for i in tokens if i in prefixes).strip()
        suffix = " ".join(i for i in tokens if i in suffixes).strip()

        name_removed_fix = " ".join(i for i in tokens
                                    if i not in prefixes and i not in suffixes)

        if infix and infix in name_removed_fix:
            name = name_removed_fix.split(" " + infix, 1)  # would be nicer with regex word boundary
            first_name = name[0].strip()
            family_name = name[1].strip()

        else:
            name = name_removed_fix.split(' ', 1)
            first_name = name[0]
            family_name = name[1]

        family_name_split = family_name.split(' ')
        first_name_split = first_name.split(' ')

        # build first name, family name, patronym and ignore -fixes
        first_name = " ".join(i for i in first_name_split
                              if not i.endswith(patronymfix)).strip()
        family_name = " ".join(i for i in family_name_split
                               if not i.endswith(patronymfix)).strip()
        patronym = " ".join(i for i in first_name_split + family_name_split
                            if i.endswith(patronymfix)).strip()

        full_name = " ".join(tokens).strip(
        )  # ALL CAPS to normal name format (e.g. Mr. Jan van Tatenhove)

        literalName = full_name.strip() if full_name is not None else "Unknown"
        disambiguatingDescription = suffix if suffix != "" else None
        patronym = patronym if patronym != "" else None
        prefix = prefix if prefix != "" else None
        givenName = first_name if first_name != "" else None
        surnamePrefix = infix if infix != "" else None
        baseSurname = family_name if family_name != "" else None

        if identifier is None:
            identifier = unique(prefix,
                                givenName,
                                patronym,
                                surnamePrefix,
                                baseSurname,
                                disambiguatingDescription,
                                literalName,
                                sep='@ga@',
                                ns=gaPersonName)

        pn = PersonName(identifier,
                        literalName=literalName,
                        prefix=prefix,
                        givenName=givenName,
                        surnamePrefix=surnamePrefix,
                        baseSurname=baseSurname,
                        patronym=patronym,
                        disambiguatingDescription=disambiguatingDescription)

        pn.label = [pn.literalName]

        pns.append(pn)
        labels.append(pn.literalName)

    return pns, labels


def parseDate(dateString):
    """
    Parse a date notation from the CSV data to XSD literals.

    Args:
        dateString (str): Date string from CSV data

    Returns:
        tuple: (earliestDate, latestDate, timeStamp)

    """

    if dateString is None:
        return None, None, None

    timeStamp = None

    if '/' in dateString:

        earliestDate, latestDate = dateString.split('/')

        if earliestDate != "?":
            earliestDate = dateParser.parse(earliestDate)
        else:
            earliestDate = None

        if latestDate != "?":
            latestDate = dateParser.parse(latestDate)
        else:
            latestDate = None

    else:

        date = dateParser.parse(dateString)

        earliestDate = date
        latestDate = date
        timeStamp = Literal(date.date(), datatype=XSD.date)

    if earliestDate:
        earliestDate = Literal(earliestDate.date(), datatype=XSD.date)
    if latestDate:
        latestDate = Literal(latestDate.date(), datatype=XSD.date)

    return earliestDate, latestDate, timeStamp


def yearToDate(yearString):
    """
    Convert a year string to a XSD date literal.

    Args:
        yearString (str): Year string from CSV data

    Returns:
        Literal: XSD date literal

    """

    if yearString is None or yearString == "?":
        return None, None

    return Literal(f"{yearString}-01-01",
                   datatype=XSD.date), Literal(f"{yearString}-12-31",
                                               datatype=XSD.date)


def parseOccupationInfo(occupationInfo, roleTypePerson, person,
                        roleTypeOrganization, organizationSubEventDict,
                        nsEvent, pid, eventCounter, nsRole, roleCounter):
    """
    Parse occupation information.

    """

    organizationString, years = occupationInfo.split(' ', 1)

    begin, end = years.split('/')

    earliestBeginTimeStamp, latestBeginTimeStamp = begin.split('|')
    earliestEndTimeStamp, latestEndTimeStamp = end.split('|')

    beginYearLabel = datetime.datetime.fromisoformat(
        earliestBeginTimeStamp).year if earliestBeginTimeStamp != "?" else "?"
    endYearLabel = datetime.datetime.fromisoformat(
        latestEndTimeStamp).year if latestEndTimeStamp != "?" else "?"

    earliestBeginTimeStamp = Literal(
        earliestBeginTimeStamp,
        datatype=XSD.date) if earliestBeginTimeStamp != "?" else None
    latestBeginTimeStamp = Literal(
        latestBeginTimeStamp,
        datatype=XSD.date) if latestBeginTimeStamp != "?" else None
    earliestEndTimeStamp = Literal(
        earliestEndTimeStamp,
        datatype=XSD.date) if earliestEndTimeStamp != "?" else None
    latestEndTimeStamp = Literal(
        latestEndTimeStamp,
        datatype=XSD.date) if latestEndTimeStamp != "?" else None

    organization = Organization(
        gaOrganization.term(organizationString.replace('.', '')),
        label=[Literal(afkortingen[organizationString], lang='nl')])

    occupationEvent = Event(
        nsEvent.term(f"{pid}-event-{next(eventCounter)}"),
        label=[
            Literal(
                f"{person.label[0]} als {roleTypePerson.label[0]} bij {afkortingen[organizationString]} ({beginYearLabel}-{endYearLabel})",
                lang='nl'),
            Literal(
                f"{person.label[0]} as {roleTypePerson.label[0]} at {afkortingen[organizationString]} ({beginYearLabel}-{endYearLabel})",
                lang='en')
        ],
        participationOf=[person, organization],
        hasEarliestBeginTimeStamp=earliestBeginTimeStamp,
        hasLatestBeginTimeStamp=latestBeginTimeStamp,
        hasEarliestEndTimeStamp=earliestEndTimeStamp,
        hasLatestEndTimeStamp=latestEndTimeStamp)

    roleCount = next(roleCounter)

    rolePerson = SpecificRoleType(
        nsRole.term(f"{pid}-role-{roleCount}"),
        type=roleTypePerson,
        carriedIn=occupationEvent,
        carriedBy=person,
        label=[
            Literal(
                f"{person.label[0]} in de rol van {roleTypePerson.label[0]}",
                lang='nl'),
            Literal(
                f"{person.label[0]} in the role of  {roleTypePerson.label[0]}",
                lang='en')
        ])

    roleTypeOrganization = SpecificRoleType(
        nsRole.term(f"{pid}-org-{roleCount}"),
        type=roleTypeOrganization,
        carriedIn=occupationEvent,
        carriedBy=organization,
        label=[
            Literal(
                f"{afkortingen[organizationString]} in de rol van {roleTypeOrganization.label[0]}",
                lang='nl'),
            Literal(
                f"{afkortingen[organizationString]} in the role of {roleTypeOrganization.label[0]}",
                lang='en')
        ])

    organizationSubEventDict[organization].append(occupationEvent)

    return occupationEvent, organizationSubEventDict


def parseFunctionInfo(functionInfo, person, roleTypeOrganization,
                      organizationSubEventDict, nsEvent, pid, eventCounter,
                      nsRole, roleCounter):

    if 'W.' in functionInfo:
        # kap. W. XXIV 1793-01-01|1793-12-31/1795-01-01|1795-12-31
        function, _, wijk, years = functionInfo.split(' ')
        doelen, unknownOrganization, stadssoldaten = None, None, None
        organizationLiteral = "Schutterij van wijk " + wijk
    elif 'stadssoldaten' in functionInfo:
        function, stadssoldaten, years = functionInfo.split(' ')
        wijk, doelen, unknownOrganization = None, None, None
        organizationLiteral = "Stadssoldaten"
    elif ' ? ' in functionInfo:
        function, _, years = functionInfo = functionInfo.split(' ')
        wijk, doelen, stadssoldaten = None, None, None
        unknownOrganization = "Unknown"
        organizationLiteral = "Unknown organization"
    else:
        # overm. Hd 1659-01-01|1659-12-31/1659-01-01|1659-12-31
        function, doelen, years = functionInfo.split(' ')
        wijk, unknownOrganization = None, None
        organizationLiteral = afkortingen[doelen]

    if function == '?':
        roleTypePerson = RoleType(gaRoleType.term('Unknown'),
                                  subClassOf=ga.Role,
                                  label=["?"])
    else:
        roleTypePerson = RoleType(gaRoleType.term(
            functies[function].title().replace(' ', '')),
                                  subClassOf=ga.Role,
                                  label=[functies[function].title()])

    begin, end = years.split('/')

    earliestBeginTimeStamp, latestBeginTimeStamp = begin.split('|')
    earliestEndTimeStamp, latestEndTimeStamp = end.split('|')

    beginYearLabel = datetime.datetime.fromisoformat(
        earliestBeginTimeStamp).year if earliestBeginTimeStamp != "?" else "?"
    endYearLabel = datetime.datetime.fromisoformat(
        latestEndTimeStamp).year if latestEndTimeStamp != "?" else "?"

    earliestBeginTimeStamp = Literal(
        earliestBeginTimeStamp,
        datatype=XSD.date) if earliestBeginTimeStamp != "?" else None
    latestBeginTimeStamp = Literal(
        latestBeginTimeStamp,
        datatype=XSD.date) if latestBeginTimeStamp != "?" else None
    earliestEndTimeStamp = Literal(
        earliestEndTimeStamp,
        datatype=XSD.date) if earliestEndTimeStamp != "?" else None
    latestEndTimeStamp = Literal(
        latestEndTimeStamp,
        datatype=XSD.date) if latestEndTimeStamp != "?" else None

    organization = Organization(
        gaOrganization.term(wijk or doelen or stadssoldaten
                            or unknownOrganization),
        label=[Literal(organizationLiteral, lang='nl')])

    functionEvent = Event(
        nsEvent.term(f"{pid}-event-{next(eventCounter)}"),
        label=[
            Literal(
                f"{person.label[0]} als {roleTypePerson.label[0]} bij {organizationLiteral} ({beginYearLabel}-{endYearLabel})",
                lang='nl'),
            Literal(
                f"{person.label[0]} as {roleTypePerson.label[0]} at {organizationLiteral} ({beginYearLabel}-{endYearLabel})",
                lang='en')
        ],
        participationOf=[person, organization],
        hasEarliestBeginTimeStamp=earliestBeginTimeStamp,
        hasLatestBeginTimeStamp=latestBeginTimeStamp,
        hasEarliestEndTimeStamp=earliestEndTimeStamp,
        hasLatestEndTimeStamp=latestEndTimeStamp)

    roleCount = next(roleCounter)

    rolePerson = SpecificRoleType(
        nsRole.term(f"{pid}-role-{roleCount}"),
        type=roleTypePerson,
        carriedIn=functionEvent,
        carriedBy=person,
        label=[
            Literal(
                f"{person.label[0]} in de rol van {roleTypePerson.label[0]}",
                lang='nl'),
            Literal(
                f"{person.label[0]} in the role of {roleTypePerson.label[0]}",
                lang='en')
        ])

    roleTypeOrganization = SpecificRoleType(
        nsRole.term(f"{pid}-org-{roleCount}"),
        type=roleTypeOrganization,
        carriedIn=functionEvent,
        carriedBy=organization,
        label=[
            Literal(
                f"{organizationLiteral} in de rol van {roleTypeOrganization.label[0]}",
                lang='nl'),
            Literal(
                f"{organizationLiteral} in the role of {roleTypeOrganization.label[0]}",
                lang='en')
        ])

    organizationSubEventDict[organization].append(functionEvent)

    return functionEvent, organizationSubEventDict


def parseRegeerInfo(regeerInfo, person, organization, roleTypeOrganization,
                    organizationSubEventDict, nsEvent, pid, eventCounter,
                    nsRole, roleCounter):

    function, years = regeerInfo.split(' ')

    roleTypePerson = RoleType(gaRoleType.term(
        bestuursfuncties[function].title().replace(' ', '')),
                              subClassOf=ga.Role,
                              label=[bestuursfuncties[function].title()])

    begin, end = years.split('/')

    earliestBeginTimeStamp, latestBeginTimeStamp = begin.split('|')
    earliestEndTimeStamp, latestEndTimeStamp = end.split('|')

    beginYearLabel = datetime.datetime.fromisoformat(
        earliestBeginTimeStamp).year if earliestBeginTimeStamp != "?" else "?"
    endYearLabel = datetime.datetime.fromisoformat(
        latestEndTimeStamp).year if latestEndTimeStamp != "?" else "?"

    earliestBeginTimeStamp = Literal(
        earliestBeginTimeStamp,
        datatype=XSD.date) if earliestBeginTimeStamp != "?" else None
    latestBeginTimeStamp = Literal(
        latestBeginTimeStamp,
        datatype=XSD.date) if latestBeginTimeStamp != "?" else None
    earliestEndTimeStamp = Literal(
        earliestEndTimeStamp,
        datatype=XSD.date) if earliestEndTimeStamp != "?" else None
    latestEndTimeStamp = Literal(
        latestEndTimeStamp,
        datatype=XSD.date) if latestEndTimeStamp != "?" else None

    bestuursEvent = Event(
        nsEvent.term(f"{pid}-event-{next(eventCounter)}"),
        label=[
            Literal(
                f"{person.label[0]} als {roleTypePerson.label[0]} bij de Stadsregering ({beginYearLabel}-{endYearLabel})",
                lang='nl'),
            Literal(
                f"{person.label[0]} as {roleTypePerson.label[0]} at the City Government ({beginYearLabel}-{endYearLabel})",
                lang='en')
        ],
        participationOf=[person, organization],
        hasEarliestBeginTimeStamp=earliestBeginTimeStamp,
        hasLatestBeginTimeStamp=latestBeginTimeStamp,
        hasEarliestEndTimeStamp=earliestEndTimeStamp,
        hasLatestEndTimeStamp=latestEndTimeStamp)

    roleCount = next(roleCounter)

    rolePerson = SpecificRoleType(
        nsRole.term(f"{pid}-role-{roleCount}"),
        type=roleTypePerson,
        carriedIn=bestuursEvent,
        carriedBy=person,
        label=[
            Literal(
                f"{person.label[0]} in de rol van {roleTypePerson.label[0]}",
                lang='nl'),
            Literal(
                f"{person.label[0]} in the role of {roleTypePerson.label[0]}",
                lang='en')
        ])

    roleTypeOrganization = SpecificRoleType(
        nsRole.term(f"{pid}-org-{roleCount}"),
        type=roleTypeOrganization,
        carriedIn=bestuursEvent,
        carriedBy=organization,
        label=[
            Literal(
                f"Stadsregering in de rol van {roleTypeOrganization.label[0]}",
                lang='nl'),
            Literal(
                f"City Government in the role of {roleTypeOrganization.label[0]}",
                lang='en')
        ])

    organizationSubEventDict[organization].append(bestuursEvent)

    return bestuursEvent, organizationSubEventDict


def toRDF(data, uri, name, description, filename, target=None):

    nametype = os.path.split(target)[1].replace('.trig', '')

    nsAnnotation = Namespace(
        f"https://data.goldenagents.org/datasets/corporatiestukken/annotation/{nametype}/"
    )

    nsPerson = Namespace(
        f"https://data.goldenagents.org/datasets/corporatiestukken/person/{nametype}/"
    )

    nsGeneralEvent = Namespace(
        f"https://data.goldenagents.org/datasets/corporatiestukken/event/")

    nsEvent = Namespace(
        f"https://data.goldenagents.org/datasets/corporatiestukken/event/{nametype}/"
    )

    nsRole = Namespace(
        f"https://data.goldenagents.org/datasets/corporatiestukken/role/{nametype}/"
    )

    dataset = ns.term('')

    g = rdfSubject.db = Graph(identifier=uri)

    _ = RoleType(
        ga.Groom,
        subClassOf=ga.Role,
        label=[Literal("Groom", lang='en'),
               Literal("Bruidegom", lang='nl')])
    _ = RoleType(
        ga.Bride,
        subClassOf=ga.Role,
        label=[Literal("Bride", lang='en'),
               Literal("Bruid", lang='nl')])
    _ = RoleType(
        ga.Born,
        subClassOf=ga.Role,
        label=[Literal("Born", lang='en'),
               Literal("Geborene", lang='nl')])
    _ = RoleType(ga.Deceased,
                 subClassOf=ga.Role,
                 label=[
                     Literal("Deceased", lang='en'),
                     Literal("Overledene", lang='nl')
                 ])

    artworkDepictedDict = defaultdict(list)
    organizationSubEventDict = defaultdict(list)

    # For the artworks
    if 'corporatiestukken.trig' in target:

        for nrow, d in enumerate(data, 2):

            # Prov
            anno = Annotation(
                nsAnnotation.term(str(nrow)),
                hasTarget=ResourceSelection(
                    None,
                    hasSource=filename,
                    hasSelector=FragmentSelector(
                        None,
                        conformsTo=URIRef("http://tools.ietf.org/rfc/rfc7111"),
                        value=f"row={nrow}")))

            # Artwork
            art_id = d['identifier'].replace(' ', '').replace('.', '')
            artwork = CreativeArtifact(
                nsArtwork.term(art_id),
                label=[d['title']],
                creationDate=d['date'],
                artist=[d['artist']],
                #disambiguatingDescription=d['dimensions'],
                comment=[Literal(d['description'], lang='nl')],
                wasDerivedFrom=[anno])

            sameAs = [
                URIRef(i) for i in [
                    d['wikidata_uri'], d['rkd_uri'], d['rijksmuseum_uri'],
                    d['amsterdammuseum_uri'], d['stadsarchief_uri']
                ] if i is not None
            ]
            artwork.sameAs = sameAs

            depictions = []
            if d['amsterdammuseum_uri']:
                with open('data/depictions_amsterdammuseum.json') as infile:
                    depictions_amsterdammuseum = json.load(infile)

                    depictionsList = [
                        URIRef(i) for i in depictions_amsterdammuseum[
                            d['amsterdammuseum_uri']]
                    ]
                    depictions += depictionsList

            if d['rijksmuseum_uri']:
                with open('data/depictions_rijksmuseum.json') as infile:
                    depictions_rijksmuseum = json.load(infile)

                portrait = depictions_rijksmuseum.get(d['rijksmuseum_uri'])
                if portrait:
                    depictions.append(URIRef(portrait))

            if d['stadsarchief_uri']:
                with open('data/depictions_stadsarchief.json') as infile:
                    depictions_stadsarchief = json.load(infile)

                portrait = depictions_stadsarchief.get(d['stadsarchief_uri'])
                if portrait:
                    depictions.append(URIRef(portrait))

            artwork.depiction = depictions

            # for the exampleResource
            p = artwork

    # For the person data
    else:
        for nrow, d in enumerate(data, 2):

            # Prov
            anno = Annotation(
                nsAnnotation.term(str(nrow)),
                hasTarget=ResourceSelection(
                    None,
                    hasSource=filename,
                    hasSelector=FragmentSelector(
                        None,
                        conformsTo=URIRef("http://tools.ietf.org/rfc/rfc7111"),
                        value=f"row={nrow}")))

            # Person

            lifeEvents = []

            gender = d['geslacht']
            if gender == 'M':
                gender = ga.Male
            elif gender == "F":
                gender = ga.Female

            pn, labels = getPersonName(d)

            # pid = str(next(personCounter))
            personCounter = count(1)
            roleCounter = count(1)
            eventCounter = count(1)

            pid = d['id']
            person_sameAs = []
            
            if Qid:= d['Wikidata']:
                person_sameAs.append(URIRef("http://www.wikidata.org/entity/" + Qid))

            p = Person(nsPerson.term(str(pid)),
                       hasName=pn,
                       gender=gender,
                       label=labels,
                       wasDerivedFrom=[anno], sameAs=person_sameAs)

            birthPlace = d['Doop/geboren te']
            deathPlace = d['Begraven/overleden te']

            birthDateEarliest, birthDateLatest, birthTimeStamp = parseDate(
                d['Doop/geboren genormaliseerd'])
            deathDateEarliest, deathDateLatest, deathTimeStamp = parseDate(
                d['Begraven/overleden genormaliseerd'])

            # Birth
            beginBirthYearLabel = datetime.datetime.fromisoformat(
                birthDateEarliest
            ).year if birthDateEarliest and birthDateEarliest != "?" else "?"
            endBirthYearLabel = datetime.datetime.fromisoformat(
                birthDateLatest
            ).year if birthDateLatest and birthDateLatest != "?" else "?"

            if birthTimeStamp:
                birthYearLabel = datetime.datetime.fromisoformat(
                    birthTimeStamp).year
            elif beginBirthYearLabel == endBirthYearLabel:
                birthYearLabel = beginBirthYearLabel
            else:
                birthYearLabel = f"ca. {beginBirthYearLabel}-{endBirthYearLabel}"

            birthEvent = Birth(
                nsEvent.term(f"{pid}-birth"),
                label=[
                    Literal(f"Geboorte van {labels[0]} ({birthYearLabel})",
                            lang='nl'),
                    Literal(f"Birth of {labels[0]} ({birthYearLabel})",
                            lang='en')
                ],
                hasTimeStamp=birthTimeStamp,
                hasEarliestBeginTimeStamp=birthDateEarliest,
                hasLatestBeginTimeStamp=birthDateLatest,
                hasLatestEndTimeStamp=birthDateLatest,
                hasEarliestEndTimeStamp=birthDateEarliest,
                place=birthPlace,
                principal=p)
            birthEvent.participationOf = [p]
            p.birth = birthEvent

            roleBorn = Born(nsRole.term(f"{pid}-born"),
                            carriedIn=birthEvent,
                            carriedBy=p,
                            label=[
                                Literal(f"{labels[0]} in de rol van geborene",
                                        lang='nl'),
                                Literal(f"{labels[0]} in the role of born",
                                        lang='en')
                            ])
            lifeEvents.append(birthEvent)

            # Death

            beginDeathYearLabel = datetime.datetime.fromisoformat(
                deathDateEarliest
            ).year if deathDateEarliest and deathDateEarliest != "?" else "?"
            endDeathYearLabel = datetime.datetime.fromisoformat(
                deathDateLatest
            ).year if deathDateLatest and deathDateLatest != "?" else "?"

            if deathTimeStamp:
                deathYearLabel = datetime.datetime.fromisoformat(
                    deathTimeStamp).year
            elif beginDeathYearLabel == endDeathYearLabel:
                deathYearLabel = beginDeathYearLabel
            else:
                deathYearLabel = f"ca. {beginDeathYearLabel}-{endDeathYearLabel}"

            deathEvent = Death(
                nsEvent.term(f"{pid}-death"),
                label=[
                    Literal(f"Overlijden van {labels[0]} ({deathYearLabel})",
                            lang='nl'),
                    Literal(f"Death of {labels[0]} ({deathYearLabel})",
                            lang='en')
                ],
                hasTimeStamp=deathTimeStamp,
                hasEarliestBeginTimeStamp=deathDateEarliest,
                hasLatestBeginTimeStamp=deathDateLatest,
                hasLatestEndTimeStamp=deathDateLatest,
                hasEarliestEndTimeStamp=deathDateEarliest,
                place=deathPlace,
                principal=p)
            deathEvent.participationOf = [p]
            p.death = deathEvent

            roleDeceased = Deceased(
                nsRole.term(f"{pid}-deceased"),
                carriedIn=deathEvent,
                carriedBy=p,
                label=[
                    Literal(f"{labels[0]} in de rol van overledene",
                            lang='nl'),
                    Literal(f"{labels[0]} in the role of deceased", lang='en')
                ])

            lifeEvents.append(deathEvent)

            if d['Geportretteerd op genormaliseerd']:

                art_id = d['Geportretteerd op genormaliseerd']
                art_id = art_id.replace(' ', '').replace('.', '')

                artwork = CreativeArtifact(nsArtwork.term(art_id))
                artworkDepictedDict[artwork].append(p)
                # p.subjectOf = [artwork]

            # RoleTypes
            RoleTypeAdministrativeOrganization = RoleType(
                gaRoleType.AdministrativeOrganization,
                subClassOf=ga.Role,
                label=[
                    Literal("Administratieve organisatie", lang='nl'),
                    Literal("Administrative organization", lang='en')
                ])

            # 1 poorters
            if 'poorters.trig' in target:
                occupationInfo = d['regent / kerkmeester genormaliseerd']

                if occupationInfo:
                    for occInfo in occupationInfo.split('; '):

                        if occInfo.startswith('km. '):
                            rtp = "Kerkmeester"
                            occInfo = occInfo.replace('km. ', '')
                            RoleTypePoorter = RoleType(gaRoleType.term(rtp),
                                                       subClassOf=ga.Role,
                                                       label=[rtp.title()])
                        else:
                            RoleTypePoorter = RoleType(gaRoleType.Regent,
                                                       subClassOf=ga.Role,
                                                       label=["Regent"])

                        occupationEvent, organizationSubEventDict = parseOccupationInfo(
                            occInfo,
                            roleTypePerson=RoleTypePoorter,
                            person=p,
                            roleTypeOrganization=
                            RoleTypeAdministrativeOrganization,
                            organizationSubEventDict=organizationSubEventDict,
                            nsEvent=nsEvent,
                            pid=pid,
                            eventCounter=eventCounter,
                            nsRole=nsRole,
                            roleCounter=roleCounter)
                        lifeEvents.append(occupationEvent)

                stadsregeringInfo = d[
                    'functie in stadsregering genormaliseerd']

                if stadsregeringInfo:

                    organization = Organization(gaOrganization.Stadsregering,
                                                label=[
                                                    Literal("Stadsregering",
                                                            lang='nl'),
                                                    Literal("City Government",
                                                            lang='en')
                                                ])

                    for regeerInfo in stadsregeringInfo.split('; '):

                        regeerEvent, organizationSubEventDict = parseRegeerInfo(
                            regeerInfo,
                            person=p,
                            organization=organization,
                            roleTypeOrganization=
                            RoleTypeAdministrativeOrganization,
                            organizationSubEventDict=organizationSubEventDict,
                            nsEvent=nsEvent,
                            pid=pid,
                            eventCounter=eventCounter,
                            nsRole=nsRole,
                            roleCounter=roleCounter)
                        lifeEvents.append(regeerEvent)

                functionInfo = d[
                    'lid/officier schutterij (vaandrigs vanaf 1650) genormaliseerd']

                if functionInfo:

                    RoleTypeSchutterij = RoleType(
                        gaRoleType.Schutterij,
                        subClassOf=ga.Role,
                        label=[Literal("Schutterij", lang='nl')])

                    RoleTypeDoelen = RoleType(
                        gaRoleType.Doelen,
                        subClassOf=ga.Role,
                        label=[Literal("Doelen", lang='nl')])

                    RoleTypeUnknown = RoleType(gaRoleType.term('Unknown'),
                                               subClassOf=ga.Role,
                                               label=["?"])

                    for funcInfo in functionInfo.split('; '):

                        if 'W.' in funcInfo:
                            rt = RoleTypeSchutterij

                        elif 'Hd' in funcInfo or 'Vd' in funcInfo or 'Kd' in funcInfo:
                            rt = RoleTypeDoelen

                        else:
                            rt = RoleTypeUnknown

                        # try:

                        functionEvent, organizationSubEventDict = parseFunctionInfo(
                            funcInfo,
                            person=p,
                            roleTypeOrganization=rt,
                            organizationSubEventDict=organizationSubEventDict,
                            nsEvent=nsEvent,
                            pid=pid,
                            eventCounter=eventCounter,
                            nsRole=nsRole,
                            roleCounter=roleCounter)
                        lifeEvents.append(functionEvent)

                        # except ValueError:
                        #     print("VALERROR", d['id'], functionInfo)
                        # except KeyError:
                        #     print("KEYERROR", d['id'], functionInfo)

                # marriage
                if d['Getrouwd met genormaliseerd']:

                    for marriage in d['Getrouwd met genormaliseerd'].split(
                            '; '):

                        wifeName, year = marriage.split(' (', 1)
                        marriageYear = year[:-1]

                        earliestDate, latestDate = yearToDate(marriageYear)

                        pnWife, labelsWife = parsePersonName(wifeName)
                        pidWife = f"{pid}-wife-{next(personCounter)}"
                        wife = Person(nsPerson.term(pidWife),
                                      hasName=pnWife,
                                      gender=ga.Female,
                                      label=labelsWife)

                        lifeEventsWife = []

                        marriageEvent = Marriage(
                            nsEvent.term(
                                f"{pid}-marriage-{next(eventCounter)}"),
                            label=[
                                Literal(
                                    f"Huwelijk tussen {labels[0]} en {wifeName} ({marriageYear})",
                                    lang='nl'),
                                Literal(
                                    f"Marriage between {labels[0]} and {wifeName} ({marriageYear})",
                                    lang='en')
                            ],
                            hasEarliestBeginTimeStamp=earliestDate,
                            hasLatestEndTimeStamp=latestDate,
                            participationOf=[p, wife],
                            partner=[p, wife])
                        lifeEvents.append(marriageEvent)
                        lifeEventsWife.append(marriageEvent)

                        roleGroom = Groom(
                            nsRole.term(f"{pid}-{next(roleCounter)}-groom"),
                            carriedIn=marriageEvent,
                            carriedBy=p,
                            label=[
                                Literal(f"{labels[0]} in de rol van bruidegom",
                                        lang='nl'),
                                Literal(f"{labels[0]} in the role of groom",
                                        lang='en')
                            ])

                        roleBride = Bride(
                            nsRole.term(
                                f"{pidWife}-{next(roleCounter)}-bride"),
                            carriedIn=marriageEvent,
                            carriedBy=wife,
                            label=[
                                Literal(f"{labelsWife[0]} in de rol van bruid",
                                        lang='nl'),
                                Literal(
                                    f"{labelsWife[0]} in the role of bride",
                                    lang='en')
                            ])

                        wife.participatesIn = lifeEventsWife

            # 2 regentessen
            if 'regentessen.trig' in target:

                RoleTypeRegentes = RoleType(gaRoleType.Regentes,
                                            subClassOf=ga.Role,
                                            label=["Regentes"])

                # regentes
                occupationInfo = d['Regentes genormaliseerd']

                for occupation in occupationInfo.split('; '):

                    occupationEvent, organizationSubEventDict = parseOccupationInfo(
                        occupation,
                        roleTypePerson=RoleTypeRegentes,
                        person=p,
                        roleTypeOrganization=RoleTypeAdministrativeOrganization,
                        organizationSubEventDict=organizationSubEventDict,
                        nsEvent=nsEvent,
                        pid=pid,
                        eventCounter=eventCounter,
                        nsRole=nsRole,
                        roleCounter=roleCounter)
                    lifeEvents.append(occupationEvent)

                # marriage
                if d['huisvrouw (hv) van / weduwe (w) van genormaliseerd']:

                    for marriage in d[
                            'huisvrouw (hv) van / weduwe (w) van genormaliseerd'].split(
                                '; '):

                        marriage = re.sub(
                            r"(?:hv. v. )|(?:w. v. )|(?:hertr. )", "",
                            marriage)
                        husbandName, rest = marriage.split('(', 1)
                        years, comment = rest.split(')', 1)

                        bioYear, marriageYear = years.rsplit('x', 1)
                        bioYear = bioYear.replace(', ', '')

                        if ' ' in bioYear:
                            birthPlaceHusband, bioYear = bioYear.rsplit(' ', 1)
                        else:
                            birthPlaceHusband = None

                        earliestDate, latestDate = yearToDate(marriageYear)

                        try:
                            birthYear, deathYear = bioYear.split('-')
                            if birthYear != "?":
                                birthDateEarliest, birthDateLatest = yearToDate(
                                    birthYear)
                            else:
                                birthDateEarliest, birthDateLatest = None, None

                            if deathYear != "?":
                                deathDateEarliest, deathDateLatest = yearToDate(
                                    deathYear)
                            else:
                                deathDateEarliest, deathDateLatest = None, None
                        except ValueError:  # quick and dirty
                            birthDateEarliest, birthDateLatest, deathDateEarliest, deathDateLatest = None, None, None, None

                        pnHusband, labelsHusband = parsePersonName(husbandName)
                        pidHusband = f"{pid}-husband-{next(personCounter)}"
                        husband = Person(nsPerson.term(pidHusband),
                                         hasName=pnHusband,
                                         gender=ga.Male,
                                         label=labelsHusband,
                                         comment=[comment])

                        lifeEventsHusband = []

                        # Birth Husband

                        beginBirthYearLabel = datetime.datetime.fromisoformat(
                            birthDateEarliest
                        ).year if birthDateEarliest and birthDateEarliest != "?" else "?"
                        endBirthYearLabel = datetime.datetime.fromisoformat(
                            birthDateLatest
                        ).year if birthDateLatest and birthDateLatest != "?" else "?"

                        if beginBirthYearLabel == endBirthYearLabel:
                            birthYearLabel = beginBirthYearLabel
                        else:
                            birthYearLabel = f"ca. {beginBirthYearLabel}-{endBirthYearLabel}"

                        birthEventHusband = Birth(
                            nsEvent.term(f"{pidHusband}-birth"),
                            label=[
                                Literal(
                                    f"Geboorte van {labelsHusband[0]} ({birthYearLabel})",
                                    lang='nl'),
                                Literal(
                                    f"Birth of {labelsHusband[0]} ({birthYearLabel})",
                                    lang='en')
                            ],
                            hasEarliestBeginTimeStamp=birthDateEarliest,
                            hasLatestBeginTimeStamp=birthDateLatest,
                            hasLatestEndTimeStamp=birthDateLatest,
                            hasEarliestEndTimeStamp=birthDateEarliest,
                            place=birthPlaceHusband,
                            principal=husband)
                        birthEventHusband.participationOf = [husband]

                        roleBorn = Born(
                            nsRole.term(f"{pidHusband}-born"),
                            carriedIn=birthEventHusband,
                            carriedBy=husband,
                            label=[
                                Literal(
                                    f"{labelsHusband[0]} in de rol van geborene",
                                    lang='nl'),
                                Literal(
                                    f"{labelsHusband[0]} in the role of born",
                                    lang='en')
                            ])
                        lifeEventsHusband.append(birthEventHusband)
                        husband.birth = birthEventHusband

                        # Death

                        beginDeathYearLabel = datetime.datetime.fromisoformat(
                            deathDateEarliest
                        ).year if deathDateEarliest and deathDateEarliest != "?" else "?"
                        endDeathYearLabel = datetime.datetime.fromisoformat(
                            deathDateLatest
                        ).year if deathDateLatest and deathDateLatest != "?" else "?"

                        if beginDeathYearLabel == endDeathYearLabel:
                            deathYearLabel = beginDeathYearLabel
                        else:
                            deathYearLabel = f"ca. {beginDeathYearLabel}-{endDeathYearLabel}"

                        deathEventHusband = Death(
                            nsEvent.term(f"{pidHusband}-death"),
                            label=[
                                Literal(
                                    f"Overlijden van {labelsHusband[0]} ({deathYearLabel})",
                                    lang='nl'),
                                Literal(
                                    f"Death of {labelsHusband[0]} ({deathYearLabel})",
                                    lang='en')
                            ],
                            hasEarliestBeginTimeStamp=deathDateEarliest,
                            hasLatestBeginTimeStamp=deathDateLatest,
                            hasLatestEndTimeStamp=deathDateLatest,
                            hasEarliestEndTimeStamp=deathDateEarliest,
                            principal=husband)
                        deathEventHusband.participationOf = [husband]

                        roleDeceased = Deceased(
                            nsRole.term(f"{pidHusband}-deceased"),
                            carriedIn=deathEventHusband,
                            carriedBy=husband,
                            label=[
                                Literal(
                                    f"{labelsHusband[0]} in de rol van overledene",
                                    lang='nl'),
                                Literal(
                                    f"{labelsHusband[0]} in the role of deceased",
                                    lang='nl')
                            ])

                        lifeEventsHusband.append(deathEventHusband)
                        husband.death = deathEventHusband

                        marriageEvent = Marriage(
                            nsEvent.term(
                                f"{pid}-marriage-{next(eventCounter)}"),
                            label=[
                                Literal(
                                    f"Huwelijk tussen {labels[0]} en {husbandName} ({marriageYear})",
                                    lang='nl'),
                                Literal(
                                    f"Marriage between {labels[0]} and {husbandName} ({marriageYear})",
                                    lang='en')
                            ],
                            hasEarliestBeginTimeStamp=earliestDate,
                            hasLatestEndTimeStamp=latestDate,
                            participationOf=[p, husband],
                            partner=[p, husband])
                        lifeEvents.append(marriageEvent)
                        lifeEventsHusband.append(marriageEvent)

                        roleBride = Bride(
                            nsRole.term(f"{pid}-bride-{next(roleCounter)}"),
                            carriedIn=marriageEvent,
                            carriedBy=p,
                            label=[
                                Literal(f"{labels[0]} in de rol van bruid",
                                        lang='nl'),
                                Literal(f"{labels[0]} in the role of bride",
                                        lang='en')
                            ])

                        roleGroom = Groom(
                            nsRole.term(
                                f"{pidHusband}-groom-{next(roleCounter)}"),
                            carriedIn=marriageEvent,
                            carriedBy=husband,
                            label=[
                                Literal(
                                    f"{labelsHusband[0]} in de rol van bruidegom",
                                    lang='nl'),
                                Literal(
                                    f"{labelsHusband[0]} in the role of groom",
                                    lang='en')
                            ])

                        husband.participatesIn = lifeEventsHusband

            # 3 regenten
            if 'regenten.trig' in target:
                RoleTypeRegent = RoleType(gaRoleType.Regent,
                                          subClassOf=ga.Role,
                                          label=["Regent"])

                occupationInfo = d['regent / kerkmeester genormaliseerd']

                if occupationInfo:
                    for occupation in occupationInfo.split('; '):
                        occupationEvent, organizationSubEventDict = parseOccupationInfo(
                            occupation,
                            roleTypePerson=RoleTypeRegent,
                            person=p,
                            roleTypeOrganization=
                            RoleTypeAdministrativeOrganization,
                            organizationSubEventDict=organizationSubEventDict,
                            nsEvent=nsEvent,
                            pid=pid,
                            eventCounter=eventCounter,
                            nsRole=nsRole,
                            roleCounter=roleCounter)
                        lifeEvents.append(occupationEvent)

            # 4 gildenleden
            if 'gildenleden.trig' in target:

                # marriage
                if d['Getrouwd met genormaliseerd']:

                    for marriage in d['Getrouwd met genormaliseerd'].split(
                            '; '):
                        wifeName, year = marriage.split(' (', 1)
                        marriageYear = year[:-1]

                        earliestDate, latestDate = yearToDate(marriageYear)

                        pnWife, labelsWife = parsePersonName(wifeName)
                        pidWife = f"{pid}-wife-{next(personCounter)}"

                        wife = Person(nsPerson.term(pidWife),
                                      hasName=pnWife,
                                      gender=ga.Female,
                                      label=labelsWife)

                        lifeEventsWife = []

                        marriageEvent = Marriage(
                            nsEvent.term(
                                f"{pid}-marriage-{next(eventCounter)}"),
                            label=[
                                Literal(
                                    f"Huwelijk tussen {labels[0]} en {wifeName} ({marriageYear})",
                                    lang='nl'),
                                Literal(
                                    f"Marriage between {labels[0]} and {wifeName} ({marriageYear})",
                                    lang='en')
                            ],
                            hasEarliestBeginTimeStamp=earliestDate,
                            hasLatestEndTimeStamp=latestDate,
                            participationOf=[p, wife],
                            partner=[p, wife])
                        lifeEvents.append(marriageEvent)
                        lifeEventsWife.append(marriageEvent)

                        roleGroom = Groom(
                            nsRole.term(f"{pid}-groom-{next(roleCounter)}"),
                            carriedIn=marriageEvent,
                            carriedBy=p,
                            label=[
                                Literal(f"{labels[0]} in de rol van bruidegom",
                                        lang='nl'),
                                Literal(f"{labels[0]} in the role of groom",
                                        lang='en')
                            ])

                        roleBride = Bride(
                            nsRole.term(
                                f"{pidWife}-bride-{next(roleCounter)}"),
                            carriedIn=marriageEvent,
                            carriedBy=wife,
                            label=[
                                Literal(f"{labelsWife[0]} in de rol van bruid",
                                        lang='nl'),
                                Literal(
                                    f"{labelsWife[0]} in the role of bride",
                                    lang='en')
                            ])

                        wife.participatesIn = lifeEventsWife

            p.participatesIn = lifeEvents

            # break

    # Dict lists
    ## Artworks
    for artwork, depictedList in artworkDepictedDict.items():
        artwork.depicts = depictedList

    ## Organizations
    organizationResUri2label = dict()
    organizationResUriSubEventDict = defaultdict(list)
    for organization, subEvents in organizationSubEventDict.items():
        organizationResUriSubEventDict[organization.resUri] += subEvents
        organizationResUri2label[organization.resUri] = organization.label[0]

    for organization, subEvents in organizationResUriSubEventDict.items():

        eventCounter = count(1)

        organizationEvent = Event(
            nsGeneralEvent.term(
                f"{str(organization).rsplit('/', 1)[1]}-{next(eventCounter)}"),
            participationOf=[organization],
            subEvent=subEvents,
            label=[
                Literal(
                    f"Tijdlijn van {organizationResUri2label[organization]}",
                    lang='nl'),
                Literal(
                    f"Timeline of {organizationResUri2label[organization]}",
                    lang='en')
            ])
        for e in subEvents:
            e.subEventOf = organizationEvent

        Organization(organization).participatesIn = [organizationEvent
                                                     ] + subEvents

    # ########
    # # Meta #
    # ########

    # rdfSubject.db = g

    # description = """"""

    # download = DataDownload(
    #     None,
    #     # contentUrl=URIRef(
    #     #     "https://raw.githubusercontent.com/LvanWissen/iets.trig"
    #     # ),
    #     # name=Literal(),
    #     # url=URIRef(
    #     #     "https://github.com/LvanWissen/iets/data"
    #     # ),
    #     encodingFormat="application/trig",
    #     version="0.1")

    # date = Literal(datetime.datetime.now().strftime('%Y-%m-%d'),
    #                datatype=XSD.date)

    # dataset = DatasetClass(uri,
    #                        name=[name],
    #                        description=[description],
    #                        isPartOf=ns.term(''),
    #                        inDataset=ns.term(''),
    #                        triples=sum(
    #                            1 for i in g.subjects()))

    # mainDataset = DatasetClass(
    #     ns.term(''),
    #     name=[
    #         Literal(
    #             "Schutters, gildebroeders, regenten en regentessen: Het Amsterdamse corporatiestuk 1525-1850",
    #             lang='nl')
    #     ],
    #     temporalCoverage=[Literal("1525-01-01/1850-12-31")],
    #     spatialCoverage=[Literal("Amsterdam")],
    #     # about=URIRef(''),
    #     # url=URIRef(''),
    #     description=[Literal(description, lang='nl')],
    #     creator=[
    #         SchemaPerson(URIRef("http://viaf.org/viaf/12415105"),
    #                      name=["Norbert Middelkoop"])
    #     ],
    #     publisher=[
    #         SchemaOrganization(URIRef("https://www.goldenagents.org/"),
    #                            name=["Golden Agents Project"])
    #     ],
    #     contributor=[
    #         SchemaPerson(URIRef("https://orcid.org/0000-0001-8672-025X"),
    #                      name=["Leon van Wissen"]),
    #         SchemaPerson(URIRef("https://orcid.org/0000-0003-2702-4371"),
    #                      name=["Jirsi Reinders"])
    #     ],
    #     citation=[
    #         URIRef(
    #             'http://hdl.handle.net/11245.1/509fbcc0-8dc0-44ae-869d-2620f905092e'
    #         )
    #     ],
    #     isBasedOn=[
    #         URIRef(
    #             "http://hdl.handle.net/11245.1/509fbcc0-8dc0-44ae-869d-2620f905092e"
    #         )
    #     ],
    #     datePublished=None,
    #     dateCreated=None,
    #     dateModified=date,
    #     distribution=download,
    #     workExample=p,
    #     vocabulary=[
    #         ga.term(''),
    #         URIRef("http://semanticweb.cs.vu.nl/2009/11/sem/")
    #     ],
    #     triples=sum(1 for i in g.subjects()),
    #     licenseprop=URIRef("https://creativecommons.org/licenses/by/4.0/"),
    #     hasPart=[dataset])

    # Skolemize BNodes
    g = g.skolemize(
        new_graph=rdflib.Graph(identifier=uri),
        authority="https://data.goldenagents.org/",
        basepath=rdflib.term.skolem_genid,
    )

    g.bind('owl', OWL)
    g.bind('dcterms', dcterms)
    g.bind('ga', ga)
    g.bind('schema', schema)
    g.bind('sem', sem)
    g.bind('void', void)
    g.bind('foaf', foaf)
    g.bind('wd', URIRef("http://www.wikidata.org/entity/"))
    g.bind('pnv', pnv)
    g.bind('bio', bio)
    g.bind('prov', prov)
    g.bind('oa', oa)

    print(f"Serializing to {target}")
    g.serialize(target, format='trig')


if __name__ == "__main__":
    main()
