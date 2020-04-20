import time
import datetime
import json
import re
from itertools import count, product
import pandas as pd

import rdflib
from rdflib import Dataset, ConjunctiveGraph, Graph, URIRef, Literal, XSD, Namespace, RDFS, BNode, OWL
from rdfalchemy import rdfSubject, rdfMultiple, rdfSingle

create = Namespace("https://data.create.humanities.uva.nl/")
schema = Namespace("http://schema.org/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
bio = Namespace("http://purl.org/vocab/bio/0.1/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
void = Namespace("http://rdfs.org/ns/void#")
dcterms = Namespace("http://purl.org/dc/terms/")
pnv = Namespace('https://w3id.org/pnv#')

rdflib.graph.DATASET_DEFAULT_GRAPH_ID = create

ns = Namespace("https://data.create.humanities.uva.nl/id/corporatiestukken/")

nsPerson = Namespace(
    "https://data.create.humanities.uva.nl/id/corporatiestukken/person/")
personCounter = count(1)

nsArtwork = Namespace(
    "https://data.create.humanities.uva.nl/id/corporatiestukken/artwork/")
artworkCounter = count(1)


class Entity(rdfSubject):
    rdf_type = URIRef('urn:entity')

    label = rdfMultiple(RDFS.label)
    name = rdfMultiple(schema.name)
    description = rdfMultiple(schema.description)

    mainEntityOfPage = rdfSingle(schema.mainEntityOfPage)
    sameAs = rdfMultiple(OWL.sameAs)

    disambiguatingDescription = rdfSingle(schema.disambiguatingDescription)

    depiction = rdfSingle(foaf.depiction)
    subjectOf = rdfMultiple(schema.subjectOf)
    about = rdfSingle(schema.about)
    url = rdfSingle(schema.url)

    inDataset = rdfSingle(void.inDataset)


class CreativeWork(Entity):
    rdf_type = schema.CreativeWork

    publication = rdfMultiple(schema.publication)
    author = rdfMultiple(schema.author)

    mainEntity = rdfSingle(schema.mainEntity)

    version = rdfSingle(schema.version)


class DatasetClass(rdfSubject):
    """Dataset class, both a schema:Dataset and a void:Dataset.

    Indicate at least:
        * name (name of the dataset, str)
        * description (detailed description (Markdown allowed), str)

    See also: https://developers.google.com/search/docs/data-types/dataset
    """

    rdf_type = void.Dataset, schema.Dataset
    label = rdfMultiple(RDFS.label)

    ##########
    # schema #
    ##########

    name = rdfMultiple(schema.name)
    description = rdfMultiple(schema.description)
    alternateName = rdfMultiple(schema.alternateName)
    creator = rdfMultiple(schema.creator,
                          range_type=(schema.Person, schema.Organization))
    publisher = rdfMultiple(schema.publisher)
    citation = rdfMultiple(schema.citation,
                           range_type=(Literal, schema.CreativeWork))
    hasPart = rdfMultiple(schema.hasPart, range_type=(URIRef, schema.Dataset))
    isPartOf = rdfSingle(schema.isPartOf, range_type=(URIRef, schema.Dataset))
    isBasedOn = rdfMultiple(schema.isBasedOn,
                            range_type=(URIRef, schema.CreativeWork))
    identifier = rdfMultiple(schema.identifier,
                             range_type=(URIRef, Literal,
                                         schema.PropertyValue))
    keywords = rdfMultiple(schema.keywords, range_type=Literal)
    licenseprop = rdfSingle(schema.license,
                            range_type=(URIRef, schema.CreativeWork))
    sameAs = rdfMultiple(schema.sameAs, range_type=URIRef)
    spatialCoverage = rdfMultiple(schema.spatialCoverage,
                                  range_type=(Literal, schema.Place))
    temporalCoverage = rdfMultiple(schema.temporalCoverage, range_type=Literal)
    variableMeasured = rdfMultiple(schema.variableMeasured,
                                   range_type=(Literal, schema.PropertyValue))
    version = rdfMultiple(schema.sameAs, range_type=Literal)
    url = rdfMultiple(schema.url, range_type=URIRef)

    distribution = rdfSingle(schema.distribution,
                             range_type=schema.DataDownload)
    dateModified = rdfSingle(schema.dateModified)

    image = rdfSingle(schema.image, range_type=URIRef)

    ########
    # void #
    ########

    dctitle = rdfMultiple(dcterms.title)
    dcdescription = rdfMultiple(dcterms.description)
    dccreator = rdfMultiple(dcterms.creator)
    dcpublisher = rdfMultiple(dcterms.publisher)
    dccontributor = rdfMultiple(dcterms.contributor)
    dcsource = rdfSingle(dcterms.source)
    dcdate = rdfSingle(dcterms.date)
    dccreated = rdfSingle(dcterms.created)
    dcissued = rdfSingle(dcterms.issued)
    dcmodified = rdfSingle(dcterms.modified)

    dataDump = rdfSingle(void.dataDump)
    sparqlEndpoint = rdfSingle(void.sparqlEndpoint)
    exampleResource = rdfSingle(void.exampleResource)
    vocabulary = rdfMultiple(void.vocabulary)
    triples = rdfSingle(void.triples)

    inDataset = rdfSingle(void.inDataset)
    subset = rdfMultiple(void.subset)

    # I left out some very specific void properties.


class DataDownload(CreativeWork):
    rdf_type = schema.DataDownload

    contentUrl = rdfSingle(schema.contentUrl)
    encodingFormat = rdfSingle(schema.encodingFormat)


class ScholarlyArticle(CreativeWork):
    rdf_type = schema.ScholarlyArticle


class VisualArtwork(CreativeWork):
    rdf_type = schema.VisualArtwork

    artist = rdfMultiple(schema.artist)

    dateCreated = rdfSingle(schema.dateCreated)
    dateModified = rdfSingle(schema.dateModified)

    temporal = rdfSingle(schema.temporal)


class PublicationEvent(Entity):
    rdf_type = schema.PublicationEvent

    startDate = rdfSingle(schema.startDate)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)

    location = rdfSingle(schema.location)

    publishedBy = rdfMultiple(schema.publishedBy)


class Place(Entity):
    rdf_type = schema.Place


class Marriage(Entity):
    rdf_type = bio.Marriage

    date = rdfSingle(bio.date)
    partner = rdfMultiple(bio.partner)
    place = rdfSingle(bio.place)

    subjectOf = rdfMultiple(schema.subjectOf)


class Person(Entity):
    rdf_type = schema.Person

    birthPlace = rdfSingle(schema.birthPlace)
    deathPlace = rdfSingle(schema.deathPlace)

    birthDate = rdfSingle(schema.birthDate)
    deathDate = rdfSingle(schema.deathDate)

    hasName = rdfMultiple(pnv.hasName, range_type=pnv.PersonName)


class PersonName(Entity):
    rdf_type = pnv.PersonName
    label = rdfSingle(RDFS.label)

    # These map to A2A
    literalName = rdfSingle(pnv.literalName)
    givenName = rdfSingle(pnv.givenName)
    surnamePrefix = rdfSingle(pnv.surnamePrefix)
    baseSurname = rdfSingle(pnv.baseSurname)

    # These do not
    prefix = rdfSingle(pnv.prefix)
    disambiguatingDescription = rdfSingle(pnv.disambiguatingDescription)
    patronym = rdfSingle(pnv.patronym)
    surname = rdfSingle(pnv.surname)


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

    prefixes = d['Titel'].split(' / ') if d['Titel'] else [None]
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
                        literalName=literalName)

        pns.append(pn)

    return pns, labels


def toRDF(data, uri, name, description, target=None):

    ds = Dataset()
    dataset = ns.term('')

    g = rdfSubject.db = ds.graph(identifier=uri)

    # For the artworks
    if 'corporatiestukken.trig' in target:

        for d in data:
            art_id = d['identifier'].replace(' ', '').replace('.', '')
            artwork = VisualArtwork(
                nsArtwork.term(art_id),
                name=[d['title']],
                dateCreated=d['date'],
                artist=[d['artist']],
                disambiguatingDescription=d['dimensions'],
                description=[Literal(d['description'], lang='nl')])

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

            lifeevents = []

            gender = d['geslacht']

            pn, label = getPersonName(d)

            birthDate = Literal(d['Doop/geboren genormaliseerd'],
                                datatype=XSD.date
                                ) if d['Doop/geboren genormaliseerd'] else None
            birthPlace = d['Doop/geboren te']
            deathDate = Literal(
                d['Begraven/overleden genormaliseerd'], datatype=XSD.date
            ) if d['Begraven/overleden genormaliseerd'] else None
            deathPlace = d['Begraven/overleden te']

            p = Person(nsPerson.term(str(next(personCounter))),
                       hasName=pn,
                       label=label,
                       birthDate=birthDate,
                       deathDate=deathDate,
                       birthPlace=birthPlace,
                       deathPlace=deathPlace)

            if d['Geportretteerd op']:

                try:
                    art_id = re.findall(r"([A-Z]{1,3}\. \d+)",
                                        d['Geportretteerd op'])[0]
                except:
                    art_id = d['Geportretteerd op']
                art_id = art_id.replace(' ', '').replace('.', '')

                artwork = VisualArtwork(nsArtwork.term(art_id))
                p.subjectOf = [artwork]

            # regentessen
            if 'huisvrouw (hv) van / weduwe (w) van genormaliseerd' in d and d[
                    'huisvrouw (hv) van / weduwe (w) van genormaliseerd']:

                for marriage in d[
                        'huisvrouw (hv) van / weduwe (w) van genormaliseerd'].split(
                            '; '):

                    marriage = re.sub(r"(?:hv. v. )|(?:w. v. )|(?:hertr. )",
                                      "", marriage)
                    husbandName, rest = marriage.split('(', 1)
                    years, rest = rest.split(')', 1)

                    print(years)
    ########
    # Meta #
    ########

    rdfSubject.db = ds

    description = """"""

    contributors = ""

    download = DataDownload(
        None,
        contentUrl=URIRef(
            "https://raw.githubusercontent.com/LvanWissen/schrijverskabinet-rdf/0.2/data/schrijverskabinet.trig"
        ),
        # name=Literal(),
        url=URIRef(
            "https://github.com/LvanWissen/schrijverskabinet-rdf/tree/0.2/data"
        ),
        encodingFormat="application/trig",
        version="0.2")

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
                   name=["Norbert Middelkoop"],
                   sameAs=[URIRef("http://viaf.org/viaf/12415105")])
        ],
        dccreator=[
            Person(nsPerson.term('norbert-middelkoop'),
                   name=["Norbert Middelkoop"],
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
    ds.bind('create', create)
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
