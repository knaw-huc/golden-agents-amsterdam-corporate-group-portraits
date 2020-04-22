import time
import datetime
import json
import re
from itertools import count, product
from collections import defaultdict
import pandas as pd

from dateutil import parser as dateParser

import rdflib
from rdflib import Dataset, ConjunctiveGraph, Graph, URIRef, Literal, XSD, Namespace, RDFS, BNode, OWL
from rdfalchemy import rdfSubject, rdfMultiple, rdfSingle

from ga import *

ns = Namespace("https://data.goldenagents.org/datasets/corporatiestukken/")
rdflib.graph.DATASET_DEFAULT_GRAPH_ID = ns

nsPerson = Namespace(
    "https://data.goldenagents.org/datasets/corporatiestukken/person/")
personCounter = count(1)

nsArtwork = Namespace(
    "https://data.goldenagents.org/datasets/corporatiestukken/artwork/")
artworkCounter = count(1)

afkortingen = {
    "Amwh": "Aalmoezeniersweeshuis",
    "Bwh": "Burgerweeshuis",
    "Dh": "Dolhuis",
    "Gh": "Gasthuizen",
    "Lh": "Leprozenhuis",
    "OMVGh": "Oude Mannen- en Vrouwengasthuis",
    "Rh": "Rasphuis",
    "SJh": "Sint Jorishof",
    "Sph": "Spinhuis",
    "SphNWh": "Spin- en Nieuwe Werkhuis",
    "Wwh": "Walenweeshuis",
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


def main(loadData=None):

    #######
    # RDF #
    #######

    # default graph

    # dataset specific
    df1 = pd.read_csv(
        'data/Middelkoop diss. dl. 2 - bijlage 4a - mannelijke poorters.csv')
    df1 = df1.where((pd.notnull(df1)), None)

    toRDF(df1.to_dict(orient='records'),
          uri=ns.term('poorters/'),
          name=Literal("Mannelijke poorters", lang='nl'),
          description="",
          target='trig/poorters.trig')

    df2 = pd.read_csv(
        'data/Middelkoop diss. dl. 2 - bijlage 4b - regentessen.csv')
    df2 = df2.where((pd.notnull(df2)), None)
    toRDF(df2.to_dict(orient='records'),
          uri=ns.term('regentessen/'),
          name=Literal("Regentessen", lang='nl'),
          description="",
          target='trig/regentessen.trig')

    df3 = pd.read_csv(
        'data/Middelkoop diss. dl. 2 - bijlage 4c - regenten Walenweeshuis.csv'
    )
    df3 = df3.where((pd.notnull(df3)), None)
    toRDF(df3.to_dict(orient='records'),
          uri=ns.term('regenten/'),
          name=Literal("Regenten Walenweeshuis", lang='nl'),
          description="",
          target='trig/regenten.trig')

    df4 = pd.read_csv(
        'data/Middelkoop diss. dl. 2 - bijlage 4d - geportretteerde gildenleden.csv'
    )
    df4 = df4.where((pd.notnull(df4)), None)
    toRDF(df4.to_dict(orient='records'),
          uri=ns.term('gildenleden/'),
          name=Literal("Geportretteerde gildenleden", lang='nl'),
          description="",
          target='trig/gildenleden.trig')

    # artwork dataset
    df5 = pd.read_csv('data/corporatiestukken.csv')
    df5 = df5.where((pd.notnull(df5)), None)
    toRDF(df5.to_dict(orient='records'),
          uri=ns.term('corporatiestukken/'),
          name=Literal("Lijst van corporatiestukken", lang='nl'),
          description="Overgenomen uit appendix 3 (Middelkoop 2019).",
          target='trig/corporatiestukken.trig')


def getPersonName(d):

    surnamePrefixes = ['de', 'van', 'la', 'der', 'du']
    pns = []
    labels = []

    prefixes = d['Titel'].split(
        ' / ') if d['Titel'] and d['Titel'] != "*" else [None]
    givenNames = d['Voornaam'].split(' / ') if d['Voornaam'] else [None]
    patronyms = d['Patroniem en tussenvoegsel'].split(
        ' / ') if d['Patroniem en tussenvoegsel'] else [None]
    baseSurnames = d['Achternaam'].split(' / ') if d['Achternaam'] else [None]

    for prefix, givenName, patronym, baseSurname in product(
            prefixes, givenNames, patronyms, baseSurnames):

        if prefix:
            prefix = prefix.strip()
        if givenName:
            givenName = givenName.strip()
        if patronym:
            patronym = " ".join([
                i for i in patronym.split(' ') if i not in surnamePrefixes
            ]).strip()

            surnamePrefix = " ".join([
                i for i in patronym.split(' ') if i in surnamePrefixes
            ]).strip()

            if surnamePrefix == "":
                surnamePrefix = None
            if patronym == "":
                patronym = None
        else:
            surnamePrefix = None

        literalName = " ".join([
            i
            for i in [prefix, givenName, patronym, surnamePrefix, baseSurname]
            if i is not None
        ])
        labels.append(literalName)

        pn = PersonName(None,
                        prefix=prefix,
                        givenName=givenName,
                        patronym=patronym,
                        surnamePrefix=surnamePrefix,
                        baseSurname=baseSurname,
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
        patronymfix = ('sz', 'sz.', 'szoon')

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
            name = name_removed_fix.split(infix)
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

        pn = PersonName(
            identifier,
            literalName=full_name.strip()
            if full_name is not None else "Unknown",
            prefix=prefix if prefix != "" else None,
            givenName=first_name if first_name != "" else None,
            surnamePrefix=infix if infix != "" else None,
            surname=family_name if family_name != "" else None,
            patronym=patronym if patronym != "" else None,
            disambiguatingDescription=suffix if suffix != "" else None)

        pn.label = [pn.literalName]

        pns.append(pn)
        labels.append(pn.literalName)

    return pns, labels


def parseDate(dateString):

    if dateString is None:
        return None, None

    if '/' in dateString:

        earliestDate, latestDate = dateString.split('/')

        earliestDate = dateParser.parse(earliestDate)
        latestDate = dateParser.parse(latestDate)
    else:
        date = dateParser.parse(dateString)
        earliestDate = date
        latestDate = date

    return Literal(earliestDate.date(),
                   datatype=XSD.date), Literal(latestDate.date(),
                                               datatype=XSD.date)


def yearToDate(yearString):
    if yearString is None or yearString == "?":
        return None, None

    return Literal(f"{yearString}-01-01",
                   datatype=XSD.date), Literal(f"{yearString}-12-31",
                                               datatype=XSD.date)


def toRDF(data, uri, name, description, target=None):

    ds = Dataset()
    dataset = ns.term('')

    g = rdfSubject.db = ds.graph(identifier=uri)

    artworkDepictedDict = defaultdict(list)

    # For the artworks
    if 'corporatiestukken.trig' in target:

        for d in data:
            art_id = d['identifier'].replace(' ', '').replace('.', '')
            artwork = CreativeArtifact(
                nsArtwork.term(art_id),
                label=[d['title']],
                creationDate=d['date'],
                artist=[d['artist']],
                #disambiguatingDescription=d['dimensions'],
                comment=[Literal(d['description'], lang='nl')])

            sameAs = [
                URIRef(i)
                for i in [d['rijksmuseum_uri'], d['amsterdammuseum_uri']]
                if i is not None
            ]
            artwork.sameAs = sameAs

            # for the exampleResource
            p = artwork

    # For the person data
    else:
        for d in data:

            lifeEvents = []

            gender = d['geslacht']
            if gender == 'M':
                gender = ga.Male
            elif gender == "F":
                gender = ga.Female

            pn, labels = getPersonName(d)

            p = Person(nsPerson.term(str(next(personCounter))),
                       hasName=pn,
                       gender=gender,
                       label=labels)

            birthDate = Literal(d['Doop/geboren genormaliseerd'],
                                datatype=XSD.date
                                ) if d['Doop/geboren genormaliseerd'] else None
            birthPlace = d['Doop/geboren te']
            deathDate = Literal(
                d['Begraven/overleden genormaliseerd'], datatype=XSD.date
            ) if d['Begraven/overleden genormaliseerd'] else None
            deathPlace = d['Begraven/overleden te']

            birthDateEarliest, birthDateLatest = parseDate(
                d['Doop/geboren genormaliseerd'])
            deathDateEarliest, deathDateLatest = parseDate(
                d['Begraven/overleden genormaliseerd'])

            # Birth
            birthEvent = Event(
                None,
                label=[Literal(f"Geboorte van {labels[0]}", lang='nl')],
                hasEarliestBeginTimeStamp=birthDateEarliest,
                hasLatestEndTimeStamp=birthDateLatest,
                place=birthPlace)
            birthEvent.participationOf = [p]

            roleBorn = Born(None,
                            carriedIn=birthEvent,
                            carriedBy=p,
                            label=["Born"])
            lifeEvents.append(birthEvent)

            # Death
            deathEvent = Event(
                None,
                label=[Literal(f"Overlijden van {labels[0]}", lang='nl')],
                hasEarliestBeginTimeStamp=deathDateEarliest,
                hasLatestEndTimeStamp=deathDateLatest,
                place=deathPlace)
            deathEvent.participationOf = [p]

            roleDied = Died(None,
                            carriedIn=deathEvent,
                            carriedBy=p,
                            label=["Died"])

            lifeEvents.append(deathEvent)

            #    birthDate=birthDate,
            #    deathDate=deathDate,
            #    birthPlace=birthPlace,
            #    deathPlace=deathPlace)

            if d['Geportretteerd op']:

                try:
                    art_id = re.findall(r"([A-Z]{1,3}\. \d+)",
                                        d['Geportretteerd op'])[0]
                except:
                    art_id = d['Geportretteerd op']
                art_id = art_id.replace(' ', '').replace('.', '')

                artwork = CreativeArtifact(nsArtwork.term(art_id))
                artworkDepictedDict[artwork].append(p)
                # p.subjectOf = [artwork]

            # regentessen
            if 'huisvrouw (hv) van / weduwe (w) van genormaliseerd' in d and d[
                    'huisvrouw (hv) van / weduwe (w) van genormaliseerd']:

                # regentes
                RoleTypeRegentes = RoleType(BNode("Regentes"),
                                            subClassOf=ga.Role,
                                            label=["Regentes"])

                occupationInfo = d['Regentes genormaliseerd']

                for occupation in occupationInfo.split('; '):
                    organizationString, years = occupation.split(' ', 1)

                    begin, end = years.split('/')

                    earliestBeginTimeStamp, latestBeginTimeStamp = begin.split(
                        '|')
                    earliestEndTimeStamp, latestEndTimeStamp = end.split('|')

                    earliestBeginTimeStamp = Literal(
                        earliestBeginTimeStamp, datatype=XSD.date
                    ) if earliestBeginTimeStamp != "?" else None
                    latestBeginTimeStamp = Literal(
                        latestBeginTimeStamp, datatype=XSD.date
                    ) if latestBeginTimeStamp != "?" else None
                    earliestEndTimeStamp = Literal(
                        earliestEndTimeStamp, datatype=XSD.date
                    ) if earliestEndTimeStamp != "?" else None
                    latestEndTimeStamp = Literal(
                        latestEndTimeStamp, datatype=XSD.date
                    ) if latestEndTimeStamp != "?" else None

                    RoleTypeAdministrativeOrganization = RoleType(
                        BNode("AdministrativeOrganization"),
                        subClassOf=ga.Role,
                        label=["Administrative Organization"])

                    organization = Organization(
                        BNode(organizationString),
                        label=[
                            Literal(afkortingen[organizationString], lang='nl')
                        ])

                    regentesEvent = Event(
                        None,
                        label=[
                            Literal(
                                f"Regentes bij {afkortingen[organizationString]}",
                                lang='nl')
                        ],
                        participationOf=[p, organization],
                        hasEarliestBeginTimeStamp=earliestBeginTimeStamp,
                        hasLatestBeginTimeStamp=latestBeginTimeStamp,
                        hasEarliestEndTimeStamp=earliestEndTimeStamp,
                        hasLatestEndTimeStamp=latestEndTimeStamp)
                    lifeEvents.append(regentesEvent)

                    roleRegentes = SpecificRoleType(None,
                                                    type=RoleTypeRegentes,
                                                    carriedIn=regentesEvent,
                                                    carriedBy=p)

                    roleAdministrativeOrganization = SpecificRoleType(
                        None,
                        type=RoleTypeAdministrativeOrganization,
                        carriedIn=regentesEvent,
                        carriedBy=organization)

                for marriage in d[
                        'huisvrouw (hv) van / weduwe (w) van genormaliseerd'].split(
                            '; '):

                    marriage = re.sub(r"(?:hv. v. )|(?:w. v. )|(?:hertr. )",
                                      "", marriage)
                    husbandName, rest = marriage.split('(', 1)
                    years, comment = rest.split(')', 1)

                    *_, marriageYear = years.rsplit('x', 1)

                    earliestDate, latestDate = yearToDate(marriageYear)

                    try:
                        birthYear, deathYear = years.split('-')
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
                    husband = Person(nsPerson.term(str(next(personCounter))),
                                     hasName=pnHusband,
                                     label=labelsHusband,
                                     comment=[comment])

                    lifeEventsHusband = []

                    # Birth Husband
                    birthEventHusband = Event(
                        None,
                        label=[
                            Literal(f"Geboorte van {labelsHusband[0]}",
                                    lang='nl')
                        ],
                        hasEarliestBeginTimeStamp=birthDateEarliest,
                        hasLatestEndTimeStamp=birthDateLatest,
                        place=birthPlace)
                    birthEventHusband.participationOf = [husband]

                    roleBorn = Born(None,
                                    carriedIn=birthEventHusband,
                                    carriedBy=husband,
                                    label=["Born"])
                    lifeEventsHusband.append(birthEventHusband)

                    # Death
                    deathEventHusband = Event(
                        None,
                        label=[
                            Literal(f"Overlijden van {labelsHusband[0]}",
                                    lang='nl')
                        ],
                        hasEarliestBeginTimeStamp=deathDateEarliest,
                        hasLatestEndTimeStamp=deathDateLatest,
                        place=deathPlace)
                    deathEventHusband.participationOf = [husband]

                    roleDied = Died(None,
                                    carriedIn=deathEventHusband,
                                    carriedBy=husband,
                                    label=["Died"])

                    lifeEventsHusband.append(deathEventHusband)

                    marriageEvent = Event(
                        None,
                        label=[
                            Literal(
                                f"Huwelijk tussen {labels[0]} en {husbandName}",
                                lang='nl')
                        ],
                        hasEarliestBeginTimeStamp=earliestDate,
                        hasLatestEndTimeStamp=latestDate,
                        participationOf=[p, husband])
                    lifeEvents.append(marriageEvent)
                    lifeEventsHusband.append(marriageEvent)

                    roleBride = Bride(None,
                                      carriedIn=marriageEvent,
                                      carriedBy=p,
                                      label=["Bride"])

                    roleGroom = Groom(None,
                                      carriedIn=marriageEvent,
                                      carriedBy=husband,
                                      label=["Groom"])

                    husband.participatesIn = lifeEventsHusband

            p.participatesIn = lifeEvents

            # break

    # Dict lists
    for artwork, depictedList in artworkDepictedDict.items():
        artwork.depicts = depictedList

    ########
    # Meta #
    ########

    rdfSubject.db = ds

    description = """"""

    contributors = ""

    download = DataDownload(
        None,
        # contentUrl=URIRef(
        #     "https://raw.githubusercontent.com/LvanWissen/iets.trig"
        # ),
        # name=Literal(),
        # url=URIRef(
        #     "https://github.com/LvanWissen/iets/data"
        # ),
        encodingFormat="application/trig",
        version="0.1")

    date = Literal(datetime.datetime.now().strftime('%Y-%m-%d'),
                   datatype=XSD.datetime)

    dataset = DatasetClass(uri,
                           name=[name],
                           description=[description],
                           isPartOf=ns.term(''),
                           inDataset=ns.term(''),
                           triples=sum(
                               1 for i in ds.graph(identifier=uri).subjects()))

    mainDataset = DatasetClass(
        ns.term(''),
        dctitle=[
            Literal(
                "Schutters, gildebroeders, regenten en regentessen: Het Amsterdamse corporatiestuk 1525-1850",
                lang='nl')
        ],
        name=[
            Literal(
                "Schutters, gildebroeders, regenten en regentessen: Het Amsterdamse corporatiestuk 1525-1850",
                lang='nl')
        ],
        temporalCoverage=[Literal("1525-01-01/1850-12-31")],
        spatialCoverage=[Literal("Amsterdam")],
        # about=URIRef(''),
        # url=URIRef(''),
        description=[Literal(description, lang='nl')],
        dcdescription=[Literal(description, lang='nl')],
        creator=[
            Person(nsPerson.term('norbert-middelkoop'),
                   label=["Norbert Middelkoop"],
                   sameAs=[URIRef("http://viaf.org/viaf/12415105")])
        ],
        dccreator=[
            Person(nsPerson.term('norbert-middelkoop'),
                   label=["Norbert Middelkoop"],
                   sameAs=[URIRef("http://viaf.org/viaf/12415105")])
        ],
        publisher=[URIRef("https://leonvanwissen.nl/me")],
        dcpublisher=[URIRef("https://leonvanwissen.nl/me")],
        # contributor=contributor,
        dcsource=URIRef(
            'https://hdl.handle.net/11245.1/509fbcc0-8dc0-44ae-869d-2620f905092e'
        ),
        citation=[
            URIRef(
                'https://hdl.handle.net/11245.1/509fbcc0-8dc0-44ae-869d-2620f905092e'
            )
        ],
        isBasedOn=[
            URIRef(
                "https://hdl.handle.net/11245.1/509fbcc0-8dc0-44ae-869d-2620f905092e"
            )
        ],
        dcdate=date,
        dateModified=date,
        distribution=download,
        dccreated=None,
        dcissued=None,
        dcmodified=None,
        exampleResource=p,
        vocabulary=[
            URIRef("http://schema.org/"),
            URIRef("http://semanticweb.cs.vu.nl/2009/11/sem/"),
            URIRef("http://xmlns.com/foaf/0.1/")
        ],
        triples=sum(1 for i in ds.graph(identifier=ns).subjects()),
        licenseprop=URIRef("https://creativecommons.org/licenses/by-sa/4.0/"),
        hasPart=[dataset],
        subset=[dataset])

    ds.bind('owl', OWL)
    ds.bind('dcterms', dcterms)
    ds.bind('ga', ga)
    ds.bind('schema', schema)
    ds.bind('sem', sem)
    ds.bind('void', void)
    ds.bind('foaf', foaf)
    ds.bind('wd', URIRef("http://www.wikidata.org/entity/"))
    ds.bind('pnv', pnv)

    print(f"Serializing to {target}")
    ds.serialize(target, format='trig')


if __name__ == "__main__":
    main()
