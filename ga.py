import time
import datetime
import json
import re
from itertools import count, product
import pandas as pd

import rdflib
from rdflib import Dataset, ConjunctiveGraph, Graph, URIRef, Literal, XSD, Namespace, RDF, RDFS, BNode, OWL
from rdfalchemy import rdfSubject, rdfMultiple, rdfSingle, rdfContainer

ga = Namespace("https://data.goldenagents.org/ontology#")

schema = Namespace("http://schema.org/")
sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
bio = Namespace("http://purl.org/vocab/bio/0.1/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
void = Namespace("http://rdfs.org/ns/void#")
dcterms = Namespace("http://purl.org/dc/terms/")
pnv = Namespace('https://w3id.org/pnv#')


class Entity(rdfSubject):
    rdf_type = URIRef('urn:entity')
    label = rdfMultiple(RDFS.label)
    comment = rdfMultiple(RDFS.comment)

    sameAs = rdfMultiple(OWL.sameAs)

    creationDate = rdfSingle(ga.creationDate)

    depiction = rdfMultiple(foaf.depiction)


class Bearer(Entity):
    rdf_type = ga.Bearer

    participatesIn = rdfMultiple(ga.participatesIn)


class Event(Entity):
    rdf_type = ga.Event

    participationOf = rdfMultiple(ga.participationOf)

    subEvent = rdfMultiple(ga.subEvent)
    subEventOf = rdfSingle(ga.subEventOf)

    hasTimeStamp = rdfSingle(sem.hasTimeStamp)
    hasBeginTimeStamp = rdfSingle(sem.hasBeginTimeStamp)
    hasEndTimeStamp = rdfSingle(sem.hasEndTimeStamp)
    hasEarliestBeginTimeStamp = rdfSingle(sem.hasEarliestBeginTimeStamp)
    hasLatestBeginTimeStamp = rdfSingle(sem.hasLatestBeginTimeStamp)
    hasEarliestEndTimeStamp = rdfSingle(sem.hasEarliestEndTimeStamp)
    hasLatestEndTimeStamp = rdfSingle(sem.hasLatestEndTimeStamp)

    place = rdfSingle(ga.place)


class Role(Entity):
    rdf_type = ga.Role

    carriedIn = rdfSingle(ga.carriedIn)
    carriedBy = rdfSingle(ga.carriedBy)


class RoleType(Role):
    rdf_type = ga.RoleType

    subClassOf = rdfSingle(RDFS.subClassOf)


class Organization(Bearer):
    rdf_type = ga.Organization


class Person(Bearer):
    rdf_type = ga.Person

    hasName = rdfMultiple(pnv.hasName, range_type=pnv.PersonName)

    gender = rdfSingle(ga.gender)


class PersonName(Entity):
    rdf_type = pnv.PersonName

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


class CreativeArtifact(Entity):
    rdf_type = ga.CreativeArtifact

    depicts = rdfMultiple(ga.depicts)

    artist = rdfMultiple(ga.artist)  # not in ontology


### RoleTypes


class Born(RoleType, Role):
    rdf_type = ga.Born


class Died(RoleType, Role):
    rdf_type = ga.Died


class Bride(RoleType, Role):
    rdf_type = ga.Bride


class Groom(RoleType, Role):
    rdf_type = ga.Groom


class SpecificRoleType(RoleType, Role):
    rdf_type = None

    type = rdfSingle(RDF.type)


### Generic dataset


class CreativeWork(Entity):
    rdf_type = schema.CreativeWork

    publication = rdfMultiple(schema.publication)
    author = rdfMultiple(schema.author)

    mainEntity = rdfSingle(schema.mainEntity)

    version = rdfSingle(schema.version)
    url = rdfSingle(schema.url)
    name = rdfMultiple(schema.name)


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
