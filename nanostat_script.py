from bs4 import BeautifulSoup as bs
import re
from pandas import DataFrame
from collections import OrderedDict
import sys
import json


def scrape_stats(soup, class_name, result_index = 0):
    ''' Search bs4 object for HTML class occurence and return list of strings '''
    
    s = soup.find_all("div", class_=class_name)[result_index].text
    
    l = [e.strip() for e in s.split("\n") if e.strip()]
    return l


def manual_curation(total):
    ''' 
    Takes an unformated list of scrape results and curates it into a dictionary.
    
    This is a highly manual process due to the varied formatting between keys and values in the report.
    '''

    # Remove lines that are headers or superfluent
    to_remove = ['DATA OUTPUT',
                'Data written to disk',
                'BASECALLING',
                'Pass',
                'Fail',
                'RUN DURATION',
                'RUN SETUP',
                'RUN SETTINGS',
                'DATA OUTPUT SETTINGS',
                'SOFTWARE VERSIONS']
    for i in to_remove:
        total.remove(i)


    # Manually re-shuffle lines pertaining to Q score threshold and pass/fail
    p = re.compile("min Q score\: [\d]+")
    q_score = p.search("".join(total)).group()[13:]

    i = total.index(f'Bases called (min Q score: {q_score})')
    total[i] = 'Bases passed'
    total.insert(i+2, 'Bases failed')
    total.insert(i, "Q score")
    total.insert(i+1, q_score)


    # Curate based on whether key-value pairs in the list are...

    # 1)
    two_lines = total[:-5]
    data = {key : val for key, val in zip(two_lines[::2], two_lines[1::2])}
    # 2)
    missing_keys = total[-5:-1]
    keys = ["Run duration",
            "Experiment name",
            "Sample name",
            "Instrument position"]
    for k, v in zip(keys, missing_keys):
        data[k] = v
    # 3)
    one_line = total[-1]
    data[one_line.split(": ")[0]] = one_line.split(": ")[1]

    return data


def scrape_barcodes(soup):
    ''' Search bs4 object for "barcode" class occurence and return dict of barcode counts '''
    
    bcs = soup.find_all("div", class_="barcode")

    if bcs:
        unsorted = {}
        for bc in bcs:
            s = bc.text.strip()

            p = re.compile("\d+")
            bc_name, bc_count = s[0:9], p.search(s[10:]).group()
            unsorted[bc_name] = bc_count
            bc_dict = OrderedDict(sorted(unsorted.items()))
        return bc_dict
    else:
        return None


def get_data(report):
    ''' 
    Takes an ONT .html run report and returns a dictionary containing relevant data.
    
    Barcode counts are appended as last dictionary entry as an ordered dict if applicable.
    '''

    soup = bs(open(report, "r"),"html.parser")

    total = []                                                     # List element(s) are...
    total += scrape_stats(soup, "accordion content", 0)             # Headers, keys or values
    total += scrape_stats(soup, "accordion content", 1)             # -||-
    total += scrape_stats(soup, "run-details")[0].split(" · ")      # Values w/o keys, separated by " · "
    total += scrape_stats(soup, "protocol-run-id")                  # Key : Value

    data = manual_curation(total)

    # Check for barcodes, and add read count dict, if any
    barcodes = scrape_barcodes(soup)
    if barcodes:
        data["barcode_reads"] = barcodes

    # Assert MinKNOW version
    version, subversion, patch  = [int(i) for i in data["MinKNOW"].split(".")]
    assert (version, subversion, patch) == (22, 5, 7)

    return data


if __name__ == "__main__":
    
    report = sys.argv[1]
    data = get_data(report)

    print(data)