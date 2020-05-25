import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from cells_dict import *

#genome build 38
START = "start"
CHR = "chr"
END = "end"
MIN_COV = 5
COV = 3
METHYLATION = 4
MATRIX_SOURCE = "/vol/sci/bio/data/yotam.drier/Gal_and_Yahel/cell/CTCF.fimocentered200bpwherefound.min50.hg38.bed"
CHR_I = 3
MATRIX = "/vol/sci/bio/data/yotam.drier/Gal_and_Yahel/cell/the_big_matrix.tsv" #todo:change
MATRIX_FOR_PLAY = "/vol/sci/bio/data/yotam.drier/Gal_and_Yahel/cell/site_&_bind_matrix.tsv"
COLUMNS = ["chr", "start", "end"]
THRESHOLD = 50


def build_matrix():
    """
    A function that initialize the site matrix and save it to csv file
    :param lst_of_site_files: list of BED file with sites
    :return: the matrix as DataFrame
    """
    # matrix = pd.DataFrame(columns=COLUMNS)
    # for f in lst_of_site_files:
    #     data = create_site_df(f)
    #     exist_site = False
    #     for chr, start, end in zip(data[0], data[1], data[2]):
    #         if chr[CHR_I:] in CTCF_SITES.keys():
    #             for site in CTCF_SITES[chr[CHR_I:]]:
    #                 if (site[0] - THRESHOLD <= start <= site[1]) and (site[0] <= end <= site[1] + THRESHOLD):
    #                     exist_site = True
    #                     break
    #             if not exist_site:
    #                 CTCF_SITES[chr[CHR_I:]].append([start, end])
    #                 exist_site = False
    #                 matrix = matrix.append(pd.DataFrame([[chr[CHR_I:], start, end]], columns=COLUMNS))
    #         else:
    #             CTCF_SITES[chr[CHR_I:]] = []
    #             CTCF_SITES[chr[CHR_I:]].append([start, end])
    #             exist_site = False
    #             matrix = matrix.append(pd.DataFrame([[chr[CHR_I:], start, end]], columns=COLUMNS))
    #     matrix = matrix.sort_values(COLUMNS)
    #     matrix.to_csv(MATRIX)
    #     return matrix
    matrix = pd.read_csv(MATRIX_SOURCE, sep='\t', header=None)
    matrix.rename(columns={0:"chr", 1:"start", 2:"end"}, inplace=True)
    matrix.to_csv(MATRIX, sep="\t")


def create_site_df(f, to_sort=False):
    data = pd.read_csv(f, sep='\t', skiprows=[131629], header=None)  # todo: deal with problemist rows
    data = data.drop(columns=[i for i in range(CHR_I, 10)])
    if to_sort:
        data = data.sort_values([0, 1, 2])
    return data


def add_cell(methylation_files_dir, binding_file, name, as_lst=True, matrix_as_df = False, matrix=MATRIX):
    """
    A function that add new cell column to the big matrix and save the matrix as file
    :param methylation_files_dir: the path to the methylation file
    :param binding_file: the path to the binding file
    :param name:the name of the new column
    :param as_lst: a boolean parameter that decide if the data came as list
    :param matrix_as_df: a boolean parameter that decide if the matrix came as dataframe
    :param matrix: the site matrix
    :return:the matrix as dataframe
    """
    if not matrix_as_df:
        matrix = pd.read_csv(matrix, index_col=0, sep="\t")
    print(matrix.describe())
    biding = create_site_df(binding_file, True)
    matrix[name + "_met"] = "."
    matrix[name + "_bind"] = "."
    print("I am here")
    if as_lst:
        for c in os.listdir(methylation_files_dir):
            f = pd.read_csv(methylation_files_dir + os.sep + c, sep='\t')
            chrom_name = (list(f)[0].split("=")[1])[COV:]
            for chr, start, end in zip(matrix[CHR], matrix[START], matrix[END]):
                if chrom_name != chr:
                    continue
                else:
                    met = np.mean(f.loc[(start - THRESHOLD <= f.index) & (f.index <= end + THRESHOLD)])[0]
                    bind = biding[(biding[0] == CHR + chr) & (start - THRESHOLD <= biding[1]) & (biding[1] <= end)
                                  & (start <= biding[2]) & (biding[2] <= end + THRESHOLD)]
                    if bind.empty:
                        matrix.loc[(matrix[CHR] == chr) & (start == matrix[START]) &
                                   (matrix[END] == end), name] = str((met, 0))
                    else:
                        matrix.loc[(matrix[CHR] == chr) & (start == matrix[START]) &
                                   (matrix[END] == end), name] = str((met, 1))
    else:
        f = pd.read_csv(methylation_files_dir, sep='\t', header=None)
        print("after reading f")
        f = f[f[COV] >= MIN_COV]
        print("filtered by coverage")
        f[METHYLATION] = f[METHYLATION] / 100
        for c in range(1, 25):
            if c == 23:
                chrom_name = CHR + "X"
            elif c == 24:
                chrom_name = CHR + "Y"
            else:
                chrom_name = CHR + str(c)
            file = f[f[0] == chrom_name]
            for chr, start, end in zip(matrix[CHR], matrix[START], matrix[END]):
                if chrom_name != chr:
                    continue
                else:
                    met = np.mean(file[(chr == file[0]) & (start - THRESHOLD <= file[1]) & (file[1] <= end + THRESHOLD)])[METHYLATION]
                    matrix.loc[(matrix[CHR] == chr) & (start == matrix[START]) & (matrix[END] == end), name + "_met"] = met
                    bind = ((biding[0] == chrom_name) & (((biding[1] <= start) & (end <= biding[2])) |
                                         ((start <= biding[1]) & (biding[2] <= end)) |
                                         ((biding[1] - THRESHOLD <= start) & (end <= biding[2]  + THRESHOLD)) )).any()
                    if bind:
                        matrix.loc[(matrix[CHR] == chr) & (start == matrix[START]) &
                                   (matrix[END] == end), name + "_bind"] = 1
                    else:
                        matrix.loc[(matrix[CHR] == chr) & (start == matrix[START]) &
                                   (matrix[END] == end), name + "_bind"] = 0
    matrix.to_csv(MATRIX, sep="\t") #todo: pay attention
    return matrix


def play_with_data(matrix):
    matrix = pd.read_csv(matrix, sep="\t")
    matrix = matrix[matrix['chr'] == 'chr1']
    matrix = matrix.fillna(0)
    # print(matrix.describe())
    col_name = list(matrix.columns)
    bind_col = [col_name[i] for i in range(5, len(col_name), 2)]
    met_col = [col_name[i] for i in range(4, len(col_name), 2)]
    matrix["binding_rate"] = matrix[bind_col].mean(axis=1)
    matrix["met_rate"] = matrix[met_col].mean(axis=1)
    # matrix.plot.scatter(x=0, y="met_rate", c="binding_rate", colormap='viridis')
    # plt.show()
    # x = 1
    matrix = matrix[matrix["binding_rate"] > 0.05]
    # methylation_dist_in_cell(matrix, col_name[4], col_name[5])
    fig, axes = plt.subplots(4, 5, figsize = (10, 7.5), dpi=100, sharex=True, sharey=True)
# colors = ['tab:red', 'tab:blue', 'tab:green', 'tab:pink', 'tab:olive']
    a = axes.flatten()
    cell_counter = 4
    axes_counter = 0
    while cell_counter < len(col_name) - 2:
        cell = (col_name[cell_counter].split("_"))[0]
        met = col_name[cell_counter]
        bind = col_name[cell_counter + 1]
        binded = matrix.loc[matrix[bind] == 1, met]
        unbinded = matrix.loc[matrix[bind] == 0, met]
        a[axes_counter].hist(binded, alpha=0.5, bins=50, density=True, stacked=True, label="methylation at the binded site")
        a[axes_counter].hist(unbinded, alpha=0.5, bins=50, density=True, stacked=True, label="methylation at the unbinded")
        a[axes_counter].set_title(cell)
        plt.yscale("log")
        cell_counter = cell_counter + 2
        axes_counter = axes_counter + 1
    plt.title("methylation distribution at CTCF binding site in diffrent cells",  y=4.95, x=-2 ,size=16)
    plt.tight_layout()
    plt.legend(loc="lower center", bbox_to_anchor=(0, -0.7))
    # plt.savefig("tests on healty data")
    plt.show()

if __name__ == '__main__':
    # print("start runing")
    # # build_matrix()
    # first = True
    # matrix = None
    # for name, cell in cells_dict.items():
    #     if name == "A549":
    #         continue
    #     print("start ", name)
    #     if first:
    #         matrix = add_cell(cell[0], cell[1], name, False)
    #         first = False
    #     else:
    #         matrix = add_cell(cell[0], cell[1], name, False, True, matrix)
    #     print("end ", name)
    # print("end running")
    # add_cell(cells_dict["pancreas"][0], cells_dict["pancreas"][1], "pancreas", False)
    play_with_data(MATRIX_FOR_PLAY)
