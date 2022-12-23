

# Linksets

- [Linksets](#linksets)
  - [Internal](#internal)
  - [External](#external)


Via different Linksets and Lenses in the [Lenticular Lens](https://lenticularlens.org/) tool (job: https://lenticularlens.goldenagents.org/?job_id=f399a189f02246ee0b9a7300677a6be6) the persons mentioned in the Corporate Group Portraits datasets were deduplicated and reconciled to other datasets. We distinguish between internal and external linksets.


## Internal
Internal linksets serve to deduplicate the persons mentioned in the Corporate Group Portraits dataset, within or between files (i.e. Poorters, Regentessen etc.). The following linksets were used to deduplicate the persons mentioned in dataset:

* [`lens_f399a189f02246ee0b9a7300677a6be6_6_accepted.trig`](internal/lens_f399a189f02246ee0b9a7300677a6be6_6_accepted.trig)
* [`sameAs_events.trig`](internal/sameAs_events.trig)
* [`sameAs_roles.trig`](internal/sameAs_roles.trig)

Via several individual linksets persons were deduplicated based upon URI's from Wikidata and validation at once. We matched all potential duplicated persons based upon the exact literal names (593 potential matches) under the the assumption was made the original data collection used exactly the same name for another registration of the same person and no deduplication had to be made on name variants.

In a lot of the remanining cases persons were mentioned in an event with in a slighlty different a day, month or year. This was the reason to create another Linkset in which at least one event (birth, marriage or death) was matched with a time frame that included the period of one year before or after the other event.

Manual validation eventually delivered a dataset (Lens #6, above) with 380 accepted matches, 131 rejected matches and 87 uncertain matches. For the manual deduplication task the works of Elias, NNBW, Van der Aa and the indices of the Amsterdam City Archives were consulted.

## External

External linksets serve to reconcile the persons mentioned in the Corporate Group Portraits dataset to other datasets. The following linksets were created:

* Baptism Registries of the Amsterdam City Archives
  * [`linkset_baptism_04b998f243b0c86500d0d099f851b365_16_accepted.trig`](external/linkset_baptism_04b998f243b0c86500d0d099f851b365_16_accepted.trig)
* Marriage Registries of the Amsterdam City Archives
  * [`lens_otr_04b998f243b0c86500d0d099f851b365_2_accepted.trig`](external/lens_otr_04b998f243b0c86500d0d099f851b365_2_accepted.trig)
  * [`linkset_otr_04b998f243b0c86500d0d099f851b365_2_accepted.trig`](external/linkset_otr_04b998f243b0c86500d0d099f851b365_2_accepted.trig)
* Burial Registries of the Amsterdam City Archives
  * [`lens_begraaf_04b998f243b0c86500d0d099f851b365_1_accepted.trig`](external/lens_begraaf_04b998f243b0c86500d0d099f851b365_1_accepted.trig) 
  * [`linkset_begraaf_04b998f243b0c86500d0d099f851b365_10_accepted.trig`](external/linkset_begraaf_04b998f243b0c86500d0d099f851b365_10_accepted.trig)
* Notarial Archives of the Amsterdam City Archives
  * [`lens_na_04b998f243b0c86500d0d099f851b365_6_accepted.trig`](external/lens_na_04b998f243b0c86500d0d099f851b365_6_accepted.trig) 
  * [`lens_na_04b998f243b0c86500d0d099f851b365_7_accepted.trig`](external/lens_na_04b998f243b0c86500d0d099f851b365_7_accepted.trig)
* Occasional Poetry (Golden Agents dataset and NTA)
  * [`lens_ggd_04b998f243b0c86500d0d099f851b365_3_accepted.trig`](external/lens_ggd_04b998f243b0c86500d0d099f851b365_3_accepted.trig)
  * [`lens_ggd_04b998f243b0c86500d0d099f851b365_4_accepted.trig`](external/lens_ggd_04b998f243b0c86500d0d099f851b365_4_accepted.trig)
  * [`linkset_ggd_04b998f243b0c86500d0d099f851b365_18_accepted.trig`](external/linkset_ggd_04b998f243b0c86500d0d099f851b365_18_accepted.trig)

In most of the above mentioned linksets/lenses, people were matched to certain events based upon event dates. Since the original data mentions only for ca. 30% of the persons an event date (a year of birth, marriage and/or burial for instance) roughly ca. 70% of all persons couldn't be matched this way. 

For these people a solution was found by standardizing the portrait date and using the newly created time frame as a starting point to find at leat two group members of a corporate group portrait in a period of 10 years before or after the creation date of the painting and match this with people acting in all kinds of notarial deeds. 

A normalized Levenshtein edit distance of 0.7 was used in Lens #7: 'Person - All deeds (0.7-0.8, 2 persons, 10 years (event date and portrait date)' resulting eventually in 3,975 possible matches of which 890 links could be accepted.
