from bs4 import BeautifulSoup as bs
import re
from pandas import DataFrame
from collections import OrderedDict
import sys
import json



def scrape_text(soup):
    ''' Scrape all text from soup object and output as list of strings '''
    
    s = soup.getText()
    l = [e.strip() for e in s.split("\n") if e.strip()]

    return l



def fetch_kv_pairs(l):
    """
    In a list of strings, find elements matching of a pre-determined set of keys,
    for each such element, add it and the subsequent element in the list to a dict
    as a key-value pair. Return the dict.
    """

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
    """
    Based on prior knowledge of which elements in the list correspond to "singleton"
    stats, fetch these using their indices and re-format them appropriately into a
    dict, which is returned.
    """
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



def fetch_barcode_reads(l):
    """
    Fetch sublist of barcode counts, separate ID from
    read count and add as key-value pairs to return dict.
    """

    l_bc = [e for e in l if re.match("barcode\d{2}",e)]

    d = {}
    for e in l_bc:
        bc_id = re.search("barcode0?(\d+)", e).group(1)
        bc_reads = re.search("Reads: (\d+)", e).group(1)
        d[bc_id] = bc_reads

    return d



def fetch_event_log(l):

    l_ev = l[l.index("Disk space"):]

    d = {}
    for i in range(0,len(l_ev),4):
        subject = l_ev[i]
        time = l_ev[i+2]
        message = l_ev[i+3]

        d[time] = {subject : message}

    return d



def get_run_data(l):
    
    misc_stats = fetch_misc_stats(l)
    key_value_pairs = fetch_kv_pairs(l)
    barcode_reads = fetch_barcode_reads(l)
    event_log = fetch_event_log(l)
    

    run_data = {"stats" : {**misc_stats, **key_value_pairs}}
    if barcode_reads:
        run_data["barcode_reads"] = barcode_reads
    run_data["event_log"] = event_log

    return run_data
    


def get_data(report):

    soup = bs(open(report, "r"),"html.parser")
    l = scrape_text(soup)
    data = get_run_data(l)

    return data



def assert_MinKNOW(data):
    version, subversion, patch  = data["stats"]["MinKNOW"].split(".")
    
    assert (version, subversion, patch) == ("22", "05", "7")



def dump_json(data, outpath):
    
    with open(outpath, "w") as outfile:
        json.dump(data, outfile)



if __name__ == "__main__":
    
    report = sys.argv[1]
    outpath = sys.argv[2]
    data = get_data(report)

    assert_MinKNOW(data, outpath)

    print(data)
    dump_json(data, outpath)