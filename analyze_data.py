import pandas as pd
# from sklearn import preprocessing as p
import numpy as np
import matplotlib.pyplot as plt
from itertools import islice
import os

COLUMNS = 1

"""number of cromosomes"""
NUM_OF_CHR = 23


def filter_data(filter, d, col, name):
    """
    A function that filter the data according do given arg and write it to new file
    :param filter: the arg to filtered by it
    :param d: the data
    :param col: the col to filter by
    :param name: the name of the filtered file
    :return: the data filters
    """
    data = pd.read_csv(d)
    data = data.drop(data.columns[0], axis=COLUMNS)
    if filter >= 0:
        data = data[data[col] >= filter]
    else:
        data = data[data[col] <= filter]
    data = remove_duplicate(data, "chr", "start", "end", "change")
    pd.DataFrame(data=data).to_csv(name)
    return data

def remove_duplicate(data, chr_col, start, end, change=""):
    """
    get data and remove the duplicate site
    :param data: the data to fix
    :param chr_col: a string that represent the name of the chrom column in the data
    :param start: the string that represent the name of the start column in the data
    :param end: the string that represent the name of the end column in the data
    :param change: the string that represent the name of the change column in the data
    :return: the fixed data
    """
    for ind, i in data.iterrows():
        for k, j in islice(data.iterrows(), 1, None):
            if ind >= k:
                continue
            if i[chr_col] == j[chr_col]:
                if abs(i[start] - j[start]) <= 10 and abs(i[end] - j[end]) <= 10:
                    data = data.drop(k)
                    continue
                if abs(i[start] - j[start]) <= 100 or abs(i[end] - j[end]) <= 100:
                    if change != "":
                        if i[change] == j[change]:
                            data = data.drop(k)
            continue
    return data

def read_genes_data(file, num_open_line=5):
    """
    A function that reads the genes DB and filter it to the genes data
    :param file: the file to read
    :param num_open_line: the number of line to ignore in the begining of the file
    :return: the filtered data
    """
    header = ['chr', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame', 'attribute']
    data = pd.read_csv(file, sep="\t", skiprows=[i for i in range(num_open_line)],
                       compression='gzip', header=None)
    data.columns = header[:len(data.columns)]
    # data = data.drop(data.columns[-1],axis=1)
    data = data[data['feature'] == 'gene']
    names = []
    for row in data.iterrows():
        line = row[1]['attribute']
        sindex = line.find("gene_name")
        line = line[sindex + 9:]
        line = line.split(";")[0]
        names.append(line)
    data['attribute'] = names
    data.to_csv("genes" + os.path.sep + "genes.csv", sep="\t")
    return data

def create_gene_data(file):
    data = read_genes_data(file)
    chroms = []
    for chr in range(NUM_OF_CHR - 2):
        chr_data = data[data['chr'] == chr + 1]
        chroms.append(chr_data)
    chr_data = data[data['chr'] == 'X']
    chroms.append(chr_data)
    chr_data = data[data['chr'] == 'y']
    chroms.append(chr_data)
    return chroms


def find_close_genes(filter, gene_data, site_file):
    """
    A function that finds which genes are close to the CTCF biding sites and count to how
    many site the gene is close.
    :param filter: the radius to look at
    :param gene_file: the data of genes
    :param site_file: the data of sites
    :return:
    """
    gene_dict = {}
    data_sites = pd.read_csv(site_file, sep=",")
    add_gene = []
    for site in data_sites.iterrows():
        genes = []
        fs = site[1]['start'] - filter
        fe = site[1]['end'] + filter
        chr = int(site[1]['chr'])
        # strand = site[1]['strand']
        for gene in gene_data[chr - 1].iterrows():
            # if gene[1]['strand'] == strand or gene[1]['strand'] == '.':
            if fs <= gene[1]['start'] and gene[1]['end'] <= fe:
                genes.append(gene[1]['attribute'])
                if gene[1]['attribute'] in gene_dict:
                    gene_dict[gene[1]['attribute']] += 1
                else:
                    gene_dict[gene[1]['attribute']] = 1
        add_gene.append(genes)
    data_sites['close genes'] = add_gene
    data_sites.to_csv("genes" + os.path.sep + "genes_close_to_sites_filter_{0}.csv".format(filter),
                      sep="\t")
    return gene_dict

def check_with_change_filter(list_of_filters, num_to_print):
    """
    A function that gets list of filter to look at, and print the most repetitive genes
    :param list_of_filters: the filters in list
    :param num_to_print: the num of repetitive elements to print
    """
    chroms = create_gene_data("Homo_sapiens.GRCh38.98.gtf.gz")
    print("yay data")
    for f in list_of_filters:
        d = find_close_genes(f, chroms, "decrease_mthylation_plass")
        print("dictionary after filter {0}".format(f))
        print(d)
        print("number of genes: {0}".format(len(d)))
        print_top_values(num_to_print, d)

def print_top_values(num_to_print, d):
    """
    A function that get dictionary and number of items to print and
    :param num_to_print:
    :param d: the dictionary to print
    """
    if num_to_print > len(d):
        num_to_print = len(d)
    counter = num_to_print
    for i in range(num_to_print):
        max_value = max(d.values())  # maximum value
        max_keys = [k for k, v in d.items() if v == max_value]
        print("value is: {0}, genes with that value: {1}". format(max_value, max_keys))
        counter -= len(max_keys)
        for key in max_keys:
            del d[key]
            if counter == 0:
                break
        if counter == 0:
            break



check_with_change_filter([10000, 50000, 100000], 10)
