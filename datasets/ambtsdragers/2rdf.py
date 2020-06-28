import re
import json
from itertools import count
import datetime
from collections import defaultdict

from rdflib import Graph, Namespace, OWL, Literal, URIRef, BNode, XSD, RDFS, RDF
from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple

bio = Namespace("http://purl.org/vocab/bio/0.1/")
schema = Namespace('http://schema.org/')
void = Namespace('http://rdfs.org/ns/void#')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
sem = Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/')
pnv = Namespace('https://w3id.org/pnv#')

JSONFILE = 'repertorium_van_ambtsdragers.json'

import sys
sys.path.append("../..")

from ga import *


def parseFunctionInfo(functionInfo, person, organizationSubEventDict,
                      identifier):

    if functionInfo['role']:
        term = functionInfo['role'].title().replace(' ', '')
        roleTypePerson = RoleType(gaRoleType.term(term),
                                  subClassOf=ga.Role,
                                  label=[functionInfo['role']])
    else:
        roleTypePerson = RoleType(gaRoleType.term('Unknown'),
                                  subClassOf=ga.Role,
                                  label=["?"])

    earliestBeginTimeStamp = functionInfo['hasEarliestBeginTimeStamp']
    latestBeginTimeStamp = functionInfo['hasLatestBeginTimeStamp']
    earliestEndTimeStamp = functionInfo['hasEarliestEndTimeStamp']
    latestEndTimeStamp = functionInfo['hasLatestEndTimeStamp']
    beginTimeStamp = functionInfo['hasBeginTimeStamp']
    endTimeStamp = functionInfo['hasEndTimeStamp']

    beginYearLabel = datetime.datetime.fromisoformat(
        earliestBeginTimeStamp).year if earliestBeginTimeStamp else "?"
    endYearLabel = datetime.datetime.fromisoformat(
        latestEndTimeStamp).year if latestEndTimeStamp else "?"

    earliestBeginTimeStamp = Literal(
        earliestBeginTimeStamp,
        datatype=XSD.date) if earliestBeginTimeStamp else None
    latestBeginTimeStamp = Literal(
        latestBeginTimeStamp,
        datatype=XSD.date) if latestBeginTimeStamp else None
    earliestEndTimeStamp = Literal(
        earliestEndTimeStamp,
        datatype=XSD.date) if earliestEndTimeStamp else None
    latestEndTimeStamp = Literal(
        latestEndTimeStamp, datatype=XSD.date) if latestEndTimeStamp else None
    beginTimeStamp = Literal(beginTimeStamp,
                             datatype=XSD.date) if beginTimeStamp else None
    endTimeStamp = Literal(endTimeStamp,
                           datatype=XSD.date) if endTimeStamp else None

    if functionInfo['organization'].get('uri'):
        term = URIRef(functionInfo['organization']['uri'])
    elif functionInfo['organization']['name']:
        term = functionInfo['organization']['name'].title().replace(' ', '')
        term = gaOrganization.term(term)
    else:
        term = None

    organization = Organization(
        term,
        label=[
            Literal(functionInfo['organization']['name']
                    or "Onbekende organisatie",
                    lang='nl')
        ])

    functionEvent = Event(
        identifier,
        label=[
            Literal(
                f"{person.label[0]} als {roleTypePerson.label[0]} bij {functionInfo['organization']['name']} ({beginYearLabel}-{endYearLabel})",
                lang='nl'),
            Literal(
                f"{person.label[0]} as {roleTypePerson.label[0]} at {functionInfo['organization']['name']} ({beginYearLabel}-{endYearLabel})",
                lang='en')
        ],
        participationOf=[person, organization],
        hasEarliestBeginTimeStamp=earliestBeginTimeStamp,
        hasLatestBeginTimeStamp=latestBeginTimeStamp,
        hasEarliestEndTimeStamp=earliestEndTimeStamp,
        hasLatestEndTimeStamp=latestEndTimeStamp,
        hasBeginTimeStamp=beginTimeStamp,
        hasEndTimeStamp=endTimeStamp)

    rolePerson = SpecificRoleType(
        None,
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
        None,
        type=gaRoleType.AdministrativeOrganization
        if functionInfo['organization']['name'] else gaRoleType.Unknown,
        carriedIn=functionEvent,
        carriedBy=organization,
        label=[
            Literal(
                f"{functionInfo['organization']['name']} in de rol van Administratieve organisatie",
                lang='nl'),
            Literal(
                f"{functionInfo['organization']['name']} in the role of Administrative organization",
                lang='en')
        ])

    organizationSubEventDict[organization].append(functionEvent)

    return functionEvent, organizationSubEventDict


def toRdf(filepath: str, target: str):

    g = rdfSubject.db = Graph()
    organizationSubEventDict = defaultdict(list)

    with open(filepath) as infile:
        data = json.load(infile)

    for p in data:

        pn = PersonName(None,
                        givenName=p['name']['givenName'],
                        baseSurname=p['name']['baseSurname'],
                        surnamePrefix=p['name']['surnamePrefix'],
                        literalName=p['name']['literalName'])

        birth = Birth(URIRef(p['uri'] + '#birth'), **p['birthDate'])

        beginBirthYearLabel = datetime.datetime.fromisoformat(
            p['birthDate']['hasEarliestBeginTimeStamp']
        ).year if p['birthDate']['hasEarliestBeginTimeStamp'] and p[
            'birthDate']['hasEarliestBeginTimeStamp'] != "?" else "?"
        endBirthYearLabel = datetime.datetime.fromisoformat(
            p['birthDate']['hasLatestEndTimeStamp']
        ).year if p['birthDate']['hasLatestEndTimeStamp'] and p['birthDate'][
            'hasLatestEndTimeStamp'] != "?" else "?"

        if p['birthDate']['hasTimeStamp']:
            birthYearLabel = datetime.datetime.fromisoformat(
                p['birthDate']['hasTimeStamp']).year
        elif beginBirthYearLabel == endBirthYearLabel:
            birthYearLabel = beginBirthYearLabel
        else:
            birthYearLabel = f"ca. {beginBirthYearLabel}-{endBirthYearLabel}"

        birth.label = [
            Literal(
                f"Geboorte van {p['name']['literalName']} ({birthYearLabel})",
                lang='nl'),
            Literal(f"Birth of {p['name']['literalName']} ({birthYearLabel})",
                    lang='en')
        ]

        roleBorn = Born(
            None,
            carriedIn=birth,
            label=[
                Literal(f"{p['name']['literalName']} in de rol van geborene",
                        lang='nl'),
                Literal(f"{p['name']['literalName']} in the role of born",
                        lang='en')
            ])

        death = Death(URIRef(p['uri'] + '#death'), **p['deathDate'])

        beginDeathYearLabel = datetime.datetime.fromisoformat(
            p['deathDate']['hasEarliestBeginTimeStamp']
        ).year if p['deathDate']['hasEarliestBeginTimeStamp'] and p[
            'deathDate']['hasEarliestBeginTimeStamp'] != "?" else "?"
        endDeathYearLabel = datetime.datetime.fromisoformat(
            p['deathDate']['hasLatestEndTimeStamp']
        ).year if p['deathDate']['hasLatestEndTimeStamp'] and p['deathDate'][
            'hasLatestEndTimeStamp'] != "?" else "?"

        if p['deathDate']['hasTimeStamp']:
            birthYearLabel = datetime.datetime.fromisoformat(
                p['deathDate']['hasTimeStamp']).year
        elif beginDeathYearLabel == endDeathYearLabel:
            birthYearLabel = beginDeathYearLabel
        else:
            birthYearLabel = f"ca. {beginDeathYearLabel}-{endDeathYearLabel}"

        death.label = [
            Literal(
                f"Geboorte van {p['name']['literalName']} ({birthYearLabel})",
                lang='nl'),
            Literal(f"Death of {p['name']['literalName']} ({birthYearLabel})",
                    lang='en')
        ]

        roleDeceased = Deceased(
            None,
            carriedIn=death,
            label=[
                Literal(f"{p['name']['literalName']} in de rol van overledene",
                        lang='nl'),
                Literal(f"{p['name']['literalName']} in the role of deceased",
                        lang='en')
            ])

        lifeEvents = [birth, death]

        person = Person(URIRef(p['uri']),
                        hasName=[pn],
                        label=[pn.literalName],
                        birth=birth,
                        death=death)

        birth.principal = person
        birth.participationOf = [person]
        roleBorn.carriedBy = person

        death.principal = person
        death.participationOf = [person]
        roleDeceased.carriedBy = person
        for n, function in enumerate(p['functions'], 1):
            identifier = URIRef(p['uri'] + f'#event-{n}')
            functionEvent, organizationSubEventDict = parseFunctionInfo(
                function, person, organizationSubEventDict, identifier)
            lifeEvents.append(functionEvent)

        person.participatesIn = lifeEvents

    ## Organizations
    organizationResUri2label = dict()
    organizationResUriSubEventDict = defaultdict(list)
    for organization, subEvents in organizationSubEventDict.items():
        organizationResUriSubEventDict[organization.resUri] += subEvents
        organizationResUri2label[organization.resUri] = organization.label[0]

    for organization, subEvents in organizationResUriSubEventDict.items():

        eventCounter = count(1)

        organizationEvent = Event(
            URIRef(str(organization) + '#event'),
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

    g.bind('foaf', foaf)
    g.bind('schema', schema)
    g.bind('void', void)
    g.bind('owĺ', OWL)
    g.bind('xsd', XSD)
    g.bind('sem', sem)
    g.bind('bio', bio)
    g.bind('pnv', pnv)
    g.bind('ga', ga)

    print(f"Serializing to {target}")
    g.serialize(target, format='turtle')


def main():
    toRdf(filepath=JSONFILE, target='ambtsdragers.ttl')


if __name__ == "__main__":
    main()