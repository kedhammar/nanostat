from bs4 import BeautifulSoup as bs
import re
from pandas import DataFrame
from collections import OrderedDict
import sys
import json


def scrape_text(soup):
    ''' Convert soup object to list of strings '''
    
    s = soup.getText()
    l = [e.strip() for e in s.split("\n") if e.strip()]

    return l


def fetch_kv_pairs(l):
    keys = ['Estimated bases',
                'Data produced',
                'Reads generated',
                'Estimated N50',
                'Elapsed time',
                'Run status',
                'Flow Cell type',
                'Flow Cell ID',
                'Kit type',
                'Specified run length',
                'Active channel selection',
                'Pore scan freq.',
                'Bias voltage (initial)',
                'Bias voltage (final)',
                'Reserved pores',
                'Basecalling',
                'FAST5 output',
                'FAST5 reads per file',
                'FASTQ output',
                'FASTQ reads per file',
                'BAM output',
                'Bulk file output',
                'Data location',
                'MinKNOW',
                'Bream',
                'Configuration',
                'Guppy',
                'MinKNOW Core']

    d = {}
    for e in l:
        if e in keys:
            d[e] = l[l.index(e)+1]

    return d


def fetch_misc_stats(l):
    indices = [1, 3, 4, 24, 25, 26]
    misc_stats = [e for e in l if l.index(e) in indices]

    d = {}
    d["Instrument"] = misc_stats[0]
    for k, v in zip(["Duration", "Experiment name", "Sample name", "Position"], misc_stats[1].split(" · ")):
        d[k] = v
    d[misc_stats[2].split(": ")[0]] = misc_stats[2].split(": ")[1]
    d["Min Q score"] = misc_stats[3].split(" ")[-1][:-1]
    d["Bases called"] = misc_stats[4]
    d["Bases uncalled"] = misc_stats[5]

    return d


def format_info(l):

    # Un-comment the following line and export to spreadsheet to get overview of how to trim the list
    # df = DataFrame(l)
    # df.to_csv("report_entries.tsv", sep="\t")
    
    misc_stats = fetch_misc_stats(l)
    key_value_pairs = fetch_kv_pairs(l)
    barcode_reads = 
    event_log = 
    
    run_data = {"run_stats" : misc_stats.update(key_value_pairs),
                "event_log" : event_log}

    if barcode_reads:
        run_data["barcode_reads"] = barcode_reads

    return run_data
    


def get_data(report):

    soup = bs(open(report, "r"),"html.parser")
    l = scrape_text(soup)

    # Assert MinKNOW version TODO
    version, subversion, patch  = [int(i) for i in data["MinKNOW"].split(".")]
    assert (version, subversion, patch) == (22, 5, 7)

    return data



if __name__ == "__main__":
    
    report = sys.argv[1]
    data = get_data(report)

    print(data)