import re
import json
import pandas as pd


def main(filename, destination):

    # URI data
    with open('data/uri_rijksmuseum.json') as infile:
        rijksmuseum_uridata = json.load(infile)
    with open('data/uri_amsterdammuseum.json') as infile:
        amsterdammuseum_uridata = json.load(infile)

    with open(filename) as txtfile:
        text = txtfile.read()

    stukken = text.split('\n\n')

    data = list()
    for i in stukken:
        d = parseArtwork(i, rijksmuseum_uridata, amsterdammuseum_uridata)

        data.append(d)

    df = pd.DataFrame(data)
    df.to_csv(destination, index=False)


def parseArtwork(text, rijksmuseum_uridata=None, amsterdammuseum_uridata=None):

    lines = text.split('\n')

    identifier = re.findall(r"([A-Z]{1,3}\. \d+)", lines[0])[0]
    titleDate = lines[1]

    if ',' in titleDate:
        title, date = titleDate.rsplit(', ', 1)
    else:
        title = titleDate
        date = None

    artist = lines[2]

    dimensions = None
    for i in lines:
        if i.startswith(('Doek', 'Paneel', 'Gravure', 'Zwart krijt')):
            dimensions = i
            break

    for i in lines:
        matches = re.findall(r"(SK-(?:A|C)-\d+)", i)

        if len(matches) == 1:
            rijksmuseum = matches[0]

            rijksmuseum_uri = rijksmuseum_uridata.get(rijksmuseum)
            break
        else:
            rijksmuseum = None
            rijksmuseum_uri = None

    for i in lines:
        matches = re.findall(r"(SA \d+)", i)

        if len(matches) == 1:
            amsterdammuseum = matches[0]

            amsterdammuseum_uri = amsterdammuseum_uridata.get(amsterdammuseum)

            break
        else:
            amsterdammuseum = None
            amsterdammuseum_uri = None

    d = {
        'identifier': identifier,
        'title': title,
        'date': date,
        'artist': artist,
        'dimensions': dimensions,
        'rijksmuseum': rijksmuseum,
        'rijksmuseum_uri': rijksmuseum_uri,
        'amsterdammuseum': amsterdammuseum,
        'amsterdammuseum_uri': amsterdammuseum_uri,
        'description': text
    }

    return d


if __name__ == "__main__":
    main(filename='data/corporatiestukken.txt',
         destination='data/corporatiestukken.csv')
