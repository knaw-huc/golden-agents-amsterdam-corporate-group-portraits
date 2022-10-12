# Amsterdam Corporate Group Portraits (dataset)

:warning: | This repository is work in progress and contains unfinished data. 
:---: | :---

## Data

Downloaded from https://pure.uva.nl/ws/files/42046294/Bijlagen_4a_d.zip

If you use the data, alway cite the original research:

* Middelkoop, N. E. (2019). Schutters, gildebroeders, regenten en regentessen: Het Amsterdamse corporatiestuk 1525-1850. <https://hdl.handle.net/11245.1/509fbcc0-8dc0-44ae-869d-2620f905092e> 



### Changes

Files altered for transformation to RDF. No changes in content, only syntax. See git history for all changes made. 

## Model

### Golden Agents ontology

This dataset points to primary/archival sources, but each record is a biography/reconstruction on its own. Therefore, we model the data in the Golden Agents ontology so that it can be included directly in the Golden Agents Research Infrastructure. 

The ontology used is event based. 
### Dates
We tried to convert all uncertain dates to valid ISO-8601 date spans. In case there was a 'ca.' notation, we interpreted this as an uncertainty range of ±2 years. This helps us to (bulk) query the data in our datastore.
For example, a notation of `1505 ca.` is converted to a date span of `1503-01-01/1507-12-31` (earliest begin / latest end). Depending on the context of the date, this sometimes is written as `1503-01-01|1503-12-31/1507-01-01|1507-12-31` (earliest begin | latest begin / earliest end | latest end).

### Linksets

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
Only the CreativeWork and Person resources carry a `prov:wasDerivedFrom` property that refers to the row number of the original csv file. 

## License

CC BY 4.0
## Contact
