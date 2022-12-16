# Linksets

Via different Linksets and Lenses in https://lenticularlens.goldenagents.org/?job_id=f399a189f02246ee0b9a7300677a6be6 the persons mentioned in the Corporate Group Portraits datasets were deduplicated:

Via Linkset #14: 'Middelkoop versus Middelkoop (ontdubbeling o.b.v. Wikidata)' 37 persons were deduplicated based upon URI's from Wikidata and validation at once

Via Linkset #17: 'Middelkoop versus Middelkoop (ontdubbeling) 2' matched all potential duplicated persons based upon the exact literal names (593 potential matches)
    ###the assumption was made the Middelkoop used exactly the same name for another registration of the same person and no deduplicated had to be made on name               varieties.

These two Linksets were merged in Lens #4: 'Middelkoop vs. Middelkoop (ontdubbeling) -Wikidata 2'

In a lot of the remanining cases persons were mentioned in an event with in a slighlty different a day, month or year. This was the reason to create another Linkset in which at least one event (birth, marriage or death) was matched with a time frame that included the period of one year before or after the other event, Linkset #16: 'Middelkoop vs. Middelkoop (ontdubbeling incl. datum)'

Lens #4 was merged with Linkset #16 in a new Lens, Lens #6: 'Middelkoop vs. Middelkoop (-Wikidata) -Constraint 1 year 3' (189 matches were found and validated at once)

Manual validation eventually delivered a dataset (Lens #6) with 380 accepted matches, 131 rejected matches and 87 uncertain matches. For the manual deduplication task the works of Elias, NNBW, Van der Aa and the indices of the Amsterdam City Archives were consulted.

In most of the above mentioned linksets/lenses, people were matched to certain events based upon event dates. Since Middelkoop mentions only for ca. 30% of the persons an event data (a year of birth, marriage and/or burial for instance) roughly ca. 70% of all persons couldn't be matched this way. For these people a solution was found by standardizing the portrait date and using the newly created time frame as a starting point to find at leat two group members of a corporate group portrait in a period of 10 years before or after the creation date of the painting and match this with people acting in all kinds of notarial deeds. A Levensthein of 0.7 was used in Lens #7: 'Person - All deeds (0.7-0.8, 2 persons, 10 years (event date and portrait date)' resulting eventually to 3,975 possible matches of which 890 links could be accepted.
