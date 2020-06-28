import requests
from bs4 import BeautifulSoup

from time import sleep
import json
import re

import datetime
import calendar
from dateutil import relativedelta

URL = "http://resources.huygens.knaw.nl/repertoriumambtsdragersambtenaren1428-1861/app/personen/index.html?persoon.geslachtsnaam=&persoon.searchable_geslachtsnaam=&persoon.voornaam=&persoon.alias=&persoon.heerlijkheid=&persoon.opmerkingen=&persoon.adel=&persoon.adel-empty-marker=1&persoon.adellijketitel-empty-marker=1&persoon.academischetitel-empty-marker=1&persoon.timespan_birth.day=0&persoon.timespan_birth.month=0&persoon.timespan_birth.year=&persoon.timespan_birth.to.day=0&persoon.timespan_birth.to.month=0&persoon.timespan_birth.to.year=&persoon.timespan_death.day=0&persoon.timespan_death.month=0&persoon.timespan_death.year=&persoon.timespan_death.to.day=0&persoon.timespan_death.to.month=0&persoon.timespan_death.to.year=&persoon.timespan_aanst.day=0&persoon.timespan_aanst.month=0&persoon.timespan_aanst.year=&persoon.timespan_aanst.to.day=0&persoon.timespan_aanst.to.month=0&persoon.timespan_aanst.to.year=&persoon.functie-empty-marker=1&persoon.functie_and_query=any&persoon.functie_and_query-empty-marker=1&persoon.instelling-empty-marker=1&persoon.instelling_and_query=any&persoon.instelling_and_query-empty-marker=1&persoon.provincie-empty-marker=1&persoon.regio-empty-marker=1&persoon.lokaal-empty-marker=1&persoon.stand-empty-marker=1&persoon.actions.zoeken=zoeken"


def parseDate(d):

    try:
        if len(d.split('-')) == 3 and 'ca. ' not in d and '00-' not in d:
            date = datetime.datetime.strptime(d,
                                              "%d-%m-%Y").strftime("%Y-%m-%d")
            beginDate = date
            endDate = date
        elif len(d.split('-')) == 3 and 'ca. ' in d and '00-' not in d:

            _, d = d.split('ca. ')

            date = datetime.datetime.strptime(d, "%d-%m-%Y").date()

            # 1 month before / after
            beginDate = (
                date -
                relativedelta.relativedelta(months=1)).strftime("%Y-%m-%d")
            endDate = (
                date +
                relativedelta.relativedelta(months=1)).strftime("%Y-%m-%d")
            date = None

        elif len(d.split('-')) == 2:
            date = None

            month, year = d.split('-')
            _, lastday = calendar.monthrange(int(year), int(month))

            beginDate = f"{year}-{month}-01"
            endDate = f"{year}-{month}-{str(lastday).zfill(1)}"

        elif d.isnumeric() and len(d) == 4:
            date = None
            beginDate = f"{d}-01-01"
            endDate = f"{d}-12-31"
        elif 'ca. ' in d and '-' not in d:
            # 2 years before / after
            _, d = d.split('ca. ')
            date = None

            if d:
                d = int(d)
                beginDate = f"{d-2}-01-01"
                endDate = f"{d+2}-12-31"
            else:
                beginDate = None
                endDate = None
        else:
            date = None
            beginDate = None
            endDate = None

        return {
            'hasTimeStamp': date,
            'hasEarliestBeginTimeStamp': beginDate,
            'hasLatestBeginTimeStamp': endDate,
            'hasEarliestEndTimeStamp': beginDate,
            'hasLatestEndTimeStamp': endDate
        }
    except:
        return {
            'hasTimeStamp': None,
            'hasEarliestBeginTimeStamp': None,
            'hasLatestBeginTimeStamp': None,
            'hasEarliestEndTimeStamp': None,
            'hasLatestEndTimeStamp': None
        }


def getPersons(url):

    persons = []
    for n in range(0, 12001, 100):
        # for n in [100, 200]:

        print(f"Fetching {n}/12093")

        r = requests.get(URL + f"&start={n}")

        soup = BeautifulSoup(r.text, 'html.parser')

        resultDiv = soup.findAll('div', class_='results')[0]
        personTags = resultDiv.findAll('a')

        for ptag in personTags:
            uri = ptag['href']

            namedata = ptag.getText()
            name = namedata.replace('\r', '')

            namesplit = name.split('\n')
            if len(namesplit) == 3:
                baseSurname, givenName, surnamePrefix = namesplit
            else:
                name = name.replace('\n\n',
                                    '\n').replace('\n\n',
                                                  '\n').replace('\n\n', '\n')
                baseSurname, _, givenName, surnamePrefix = name.split('\n')
            if baseSurname.endswith(','):
                baseSurname = baseSurname[:-1].strip()
            else:
                baseSurname = baseSurname.strip()

            surnamePrefix = surnamePrefix.strip()
            if not surnamePrefix:
                surnamePrefix = None

            givenName = givenName.strip()
            if not givenName:
                givenName = None

            literalName = " ".join(
                [i for i in [givenName, surnamePrefix, baseSurname] if i])

            datesdata = ptag.parent.getText()
            dates = datesdata.rsplit('(', 1)[1].rsplit(')', 1)[0]
            birthDate, deathDate = dates.split('\n-\n')

            birthDate = parseDate(birthDate)
            deathDate = parseDate(deathDate)

            persons.append({
                'name': {
                    'baseSurname': baseSurname,
                    'givenName': givenName,
                    'surnamePrefix': surnamePrefix,
                    'literalName': literalName
                },
                'uri': uri,
                'data': datesdata,
                'birthDate': birthDate,
                'deathDate': deathDate
            })

        sleep(1)

    return persons


def getFunctions(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    print(url)

    functions = []

    # membership

    membershipDiv = soup.findAll('span', class_='functie')
    for md in membershipDiv:

        mdText = md.getText()
        mdText = re.sub(r'  +', '', mdText).strip()

        func, org, *dates = mdText.split('\n')
        dates = " ".join(dates)
        dates = re.sub(r'[\(\)\.]', '', dates)

        beginDate, endDate = dates.split(' - ')

        beginDateDict = parseDate(beginDate)
        endDateDict = parseDate(endDate)

        earliestBeginTimeStamp = beginDateDict['hasEarliestBeginTimeStamp']
        latestBeginTimeStamp = beginDateDict['hasLatestEndTimeStamp']
        earliestEndTimeStamp = endDateDict['hasEarliestBeginTimeStamp']
        latestEndTimeStamp = beginDateDict['hasLatestEndTimeStamp']

        if 'hasTimeStamp' in beginDateDict:
            beginTimeStamp = beginDateDict['hasTimeStamp']
        else:
            beginTimeStamp = None

        if 'hasTimeStamp' in endDateDict:
            endTimeStamp = endDateDict['hasTimeStamp']
        else:
            endTimeStamp = None

        functions.append({
            'role': func,
            'organization': {
                'name': org,
                'uri': None
            },
            'hasBeginTimeStamp': beginTimeStamp,
            'hasEndTimeStamp': endTimeStamp,
            'hasEarliestBeginTimeStamp': earliestBeginTimeStamp,
            'hasLatestBeginTimeStamp': latestBeginTimeStamp,
            'hasEarliestEndTimeStamp': earliestEndTimeStamp,
            'hasLatestEndTimeStamp': latestEndTimeStamp
        })

    # functions

    for funcDiv in soup.findAll('div', class_='results'):

        funcText = funcDiv.getText()
        funcText = re.sub(r'  +', '', funcText)

        items = [
            i.replace('\n', ' ').strip() for i in funcText.split('\n\n')
            if i != 'anderen met deze aanstelling...'
        ]

        func, org, period, region = None, None, None, None
        for i in items:
            if i.startswith('functie: '):
                func = i.replace('functie: ', '')
            if i.startswith('instelling: '):
                org = i.replace('instelling: ', '')
            if i.startswith('van: '):
                period = i.replace('van: ', '')
            if i.startswith('- '):
                period = i
            if i.startswith('namens: '):
                region = i.replace('namens: ', '')

        if period and period.strip().endswith('-'):
            beginDate, endDate = period.split(' -')
        elif period and period.strip().startswith('-'):
            beginDate, endDate = period.split('- ')
        elif period:
            beginDate, endDate = period.split(' - ')
        else:
            beginDate, endDate = None, None

        beginDateDict = parseDate(beginDate)
        endDateDict = parseDate(endDate)

        earliestBeginTimeStamp = beginDateDict['hasEarliestBeginTimeStamp']
        latestBeginTimeStamp = beginDateDict['hasLatestEndTimeStamp']
        earliestEndTimeStamp = endDateDict['hasEarliestBeginTimeStamp']
        latestEndTimeStamp = beginDateDict['hasLatestEndTimeStamp']

        if 'hasTimeStamp' in beginDateDict:
            beginTimeStamp = beginDateDict['hasTimeStamp']
        else:
            beginTimeStamp = None

        if 'hasTimeStamp' in endDateDict:
            endTimeStamp = endDateDict['hasTimeStamp']
        else:
            endTimeStamp = None

        commentsDiv = funcDiv.findAll('p', class_='opmerkingen')
        if commentsDiv:
            comments = commentsDiv[0].getText()
        else:
            comments = None

        atags = funcDiv.findAll('a')
        for a in atags:
            if a.get('class') == 'sortering':
                continue
            elif 'app/instellingen' in a['href']:
                orguri = a['href']

                if orguri.endswith('#'):
                    orguri = orguri[:-1]
                break
            else:
                orguri = None

        functions.append({
            'role': func,
            'organization': {
                'name': org,
                'region': region,
                'uri': orguri
            },
            'hasBeginTimeStamp': beginTimeStamp,
            'hasEndTimeStamp': endTimeStamp,
            'hasEarliestBeginTimeStamp': earliestBeginTimeStamp,
            'hasLatestBeginTimeStamp': latestBeginTimeStamp,
            'hasEarliestEndTimeStamp': earliestEndTimeStamp,
            'hasLatestEndTimeStamp': latestEndTimeStamp
        })

    return functions


def main():
    persons = getPersons(URL)

    for n, person in enumerate(persons, 1):

        print(f"Getting functions for {n}/{len(persons)}")

        functions = getFunctions(person['uri'])

        person['functions'] = functions

        sleep(0.8)

    with open('repertorium_van_ambtsdragers.json', 'w') as outfile:
        json.dump(persons, outfile, indent=4)
    print("Done!")


if __name__ == "__main__":
    main()
