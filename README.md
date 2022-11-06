# Amsterdam Corporate Group Portraits (dataset)

- [Amsterdam Corporate Group Portraits (dataset)](#amsterdam-corporate-group-portraits-dataset)
  - [Introduction](#introduction)
  - [Data](#data)
    - [Changes](#changes)
  - [Model](#model)
    - [Golden Agents ontology](#golden-agents-ontology)
    - [Dates](#dates)
    - [Linksets](#linksets)
    - [Provenance](#provenance)
  - [License](#license)
  - [Contact](#contact)

## Introduction
The Amsterdam Corporate Group Portraits dataset contains biographical information on persons depicted on institutional/corporate group portraits in the seventeenth and eighteenth century in Amsterdam. The dataset is part of the [Golden Agents](https://goldenagents.org) project.

The original data were collected by Norbert Middelkoop and published as attachment to his dissertation [_Schutters, gildebroeders, regenten en regentessen_](https://hdl.handle.net/11245.1/509fbcc0-8dc0-44ae-869d-2620f905092e) (2019). The Golden Agent project took his data and heavily structured these, so that they could be used in the project's infrastructure infrastructure. 

We kept the original structure of the dataset, so that we separate information on:
1. Corporate group portraits (visual works)
2. Poorters [=Burghers] (persons)
3. Regentessen [=Regents (F)] (persons)
4. Regenten [=Regents (M)] (persons)
5. Gildenleden [=Guild members] (persons)

For all the persons, if available, we modelled information on their name, the portrait they are depicted on, when they were a regent or churchmaster, when they were a member of the civic guards (schutterij), when they were a member of a guild, and when they were a member of the city council. Besides this, we added information on their birth and death date, and their marriages.

Through linksets (see the [linkset documentation](linksets/README.md)) we linked the persons to Wikidata and to among others the [Amsterdam City Archives](https://archief.amsterdam). These linksets also serve as a way to link the persons to other datasets in the Golden Agents projec.

## Data

The original data were downloaded from https://pure.uva.nl/ws/files/42046294/Bijlagen_4a_d.zip

If you use the data, alway cite the original research:

* Middelkoop, N. E. (2019). Schutters, gildebroeders, regenten en regentessen: Het Amsterdamse corporatiestuk 1525-1850. <https://hdl.handle.net/11245.1/509fbcc0-8dc0-44ae-869d-2620f905092e> 

### Changes

The spreadsheets were altered for transformation to RDF. No changes were made in content, only in syntax. See the git history for all changes made. 

## Model

### Golden Agents ontology

This dataset points to primary/archival sources, but each record is a biography/reconstruction on its own. Therefore, we model the data in the Golden Agents ontology so that it can be included directly in the Golden Agents Research Infrastructure. 

The ontology used is event based and structurs person and event participation information in a way that every person is linked directly to an event with the `ga:participatesIn` property. A `ga:Role` instance (with corresponding `ga:carriedBy` and `carriedIn` properties) is used to reify this relationship.  

Example:

```turtle
```

### Dates
We tried to convert all uncertain dates to valid ISO-8601 date spans. In case there was a 'ca.' notation, we interpreted this as an uncertainty range of ±2 years. This helps us to (bulk) query the data in our datastore.

For example, a notation of `1505 ca.` is converted to a date span of `1503-01-01/1507-12-31` (earliest begin / latest end). Depending on the context of the date, this sometimes is written as `1503-01-01|1503-12-31/1507-01-01|1507-12-31` (earliest begin | latest begin / earliest end | latest end).

### Linksets
The original spreadsheets did not contain unique person mentions. It could be that a person appeared in other files as well, or multiple times in the same file. We therefore created linksets that disambiguate persons within the dataset. See the `[linksets/internal](linksets/internal/)` folder for more information.

If persons are disambiguated and linked using an `owl:sameAs` predicate, then this should also be done for any duplicate role and event information (e.g. the role of being born in a birth event). The two construct queries below partly solve this issue and can be found in that same folder. 

To construct a linkset of roles of persons:

```SPARQL
PREFIX ga: <https://data.goldenagents.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
CONSTRUCT {
    ?role1 owl:sameAs ?role2 .
} WHERE { 
    ?person a ga:Person ;
         ga:participatesIn ?event1, ?event2 .
    
    FILTER(?event1 != ?event2)
    
    ?event1 rdfs:label ?eventlabel .
    ?event2 rdfs:label ?eventlabel .
    
    ?role1 a ?roleType1 ;
          ga:carriedIn ?event1 ;
          ga:carriedBy ?person ;
          rdfs:label ?label .
    
    ?role2 a ?roleType2 ;
          ga:carriedIn ?event2 ;
          ga:carriedBy ?person ;
          rdfs:label ?label .
    
    FILTER(?role1 != ?role2)
    
    
}

```

To construct a linkset of events in which persons participate:


```SPARQL
PREFIX ga: <https://data.goldenagents.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
CONSTRUCT {
    ?event1 owl:sameAs ?event2 .
} WHERE { 
    ?person a ga:Person ;
         ga:participatesIn ?event1, ?event2 .
    
    FILTER(?event1 != ?event2)
    
    ?event1 rdfs:label ?eventlabel .
    ?event2 rdfs:label ?eventlabel .
    
    ?role1 a ?roleType1 ;
          ga:carriedIn ?event1 ;
          ga:carriedBy ?person ;
          rdfs:label ?label .
    
    ?role2 a ?roleType2 ;
          ga:carriedIn ?event2 ;
          ga:carriedBy ?person ;
          rdfs:label ?label .
    
    FILTER(?role1 != ?role2)
    
    
}
```

### Provenance
Only the CreativeWork and Person resources carry a `prov:wasDerivedFrom` property that refers to the row number of the original csv file. Original values were kept in different columns. Every file is converted to a separate named graph, so that the origin of certain statements can be traced once the data is loaded into a triplestore.

## License

CC BY 4.0
## Contact

Golden Agents project