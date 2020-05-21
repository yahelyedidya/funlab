import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

P_VALS = "p_values.tsv"

REP_LIST = ['1_month', '6_month', '10_month', '15_month']

DIR = "/vol/sci/bio/data/yotam.drier/Gal_and_Yahel/CSC"
FIRST_FILE = "control_vs_csc_after_1_month_rep{0}"
ALL_NAME = "csc_all_rep{0}.tsv"
CHANGES_REP = "csc_all_changes_rep{0}.tsv"


def create_one_file(target_file_name):
    combined = pd.read_csv(DIR + os.path.sep + FIRST_FILE, sep="\t")
    combined = combined.drop(columns=['cov', 'strand', 'change'])
    combined = combined.rename(columns={"treatment": "1_month"})
    # a = os.listdir(DIR)
    for file in os.listdir(DIR):
        if file != FIRST_FILE and file.endswith("2"):
            time_interval = file.split("_")[4]
            print(time_interval)
            temp = pd.read_csv(DIR + os.path.sep + file, sep="\t")
            combined["{0}_month".format(time_interval)] = temp["treatment"]
    combined = combined[['ID_REF',
                         'chr',
                         'start',
                         'end',
                         'control',
                         '1_month',
                         '6_month',
                         '10_month',
                         '15_month']]
    print(combined.head())
    combined.to_csv(DIR + os.path.sep + target_file_name, sep="\t", index=False)


def create_changes(k):
    combined = pd.read_csv(DIR + os.path.sep + FIRST_FILE.format(k), sep="\t")
    combined = combined.drop(columns=['cov', 'strand', 'treatment'])
    combined = combined.rename(columns={"change": "1_month"})
    data = pd.read_csv(DIR + os.path.sep + ALL_NAME.format(k), sep="\t")
    for i in range(1, len(REP_LIST)):
        combined[REP_LIST[i]] = data[REP_LIST[i-1]] - data[REP_LIST[i]]
        print(i)
    print(combined.head())
    combined.to_csv(DIR + os.path.sep + CHANGES_REP.format(k), sep="\t", index=False)


def get_uniq_rate(b, label):
    round = np.around(np.array(b[label]), 2)
    return np.unique(round, return_counts=True)


def plot_change(i):
    data = pd.read_csv(DIR + os.path.sep + CHANGES_REP.format(i), sep="\t")
    xs_list, ys_list = [], []
    for col in REP_LIST:
        xs, ys = get_uniq_rate(data, col)
        xs_list += list(xs)
        ys_list += list(ys)
        y = data[col]
        plt.hist(y, alpha=0.5, label=col)
    plt.scatter(xs_list, ys_list, color="black")
    # plt.plot(xs_list, ys_list, color="black")

    plt.xlabel("methylation change rate")
    plt.ylabel("Amount of performances")
    plt.title("methylation change distribution according to time, replication : {0}".format(i))
    plt.legend()
    # plt.savefig(DIR + os.path.sep + "change_distribution_graph_rep{0}".format(i))
    plt.show()


def statistic_test():
    rep_1 = pd.read_csv(DIR + os.path.sep + ALL_NAME.format(1), sep="\t")
    rep_2 = pd.read_csv(DIR + os.path.sep + ALL_NAME.format(2), sep="\t")

    result = rep_1
    result = result.drop(columns=REP_LIST)
    result = result.drop(columns=['control'])
    for title in REP_LIST:
        p_vals = []
        for i in range(rep_1.shape[0]):
            control = [rep_1['control'][i], rep_2['control'][i]]
            after = [rep_1[title][i], rep_2[title][i]]
            t_test = stats.ttest_ind(control, after, equal_var=False)
            p_vals.append(t_test.pvalue)
        result[title] = p_vals
    result.to_csv(DIR + os.path.sep + P_VALS, sep="\t", index=False)


def kde_scipy(x, x_grid, bandwidth=0.2, **kwargs):
    """Kernel Density Estimation with Scipy"""
    # Note that scipy weights its bandwidth by the covariance of the
    # input data.  To make the results comparable to the other methods,
    # we divide the bandwidth by the sample standard deviation here.
    kde = stats.gaussian_kde(x, bw_method=bandwidth / x.std(ddof=1), **kwargs)
    return kde.evaluate(x_grid)


def smoothshow(i):
    data = pd.read_csv(DIR + os.path.sep + CHANGES_REP.format(i), sep="\t")
    data = data.drop(columns=['ID_REF', 'chr', 'start', 'end', 'control'])
    x = np.array(data)
    x_grid = np.linspace(-1, 1, 1000)
    pdf = kde_scipy(x, x_grid, bandwidth=0.2)
    plt.plot(x_grid, pdf, color='blue', alpha=0.5, lw=3)
    # plt.fill(x_grid, pdf_true, ec='gray', fc='gray', alpha=0.4)
    # plt.set_title(kde_funcnames[i])
    # plt.set_xlim(-4.5, 3.5)
    plt.show()


def data_to_plot():
    data = pd.read_csv(DIR + os.path.sep + CHANGES_REP.format(2), sep="\t")
    data = data.drop(columns=['ID_REF', 'chr', 'start', 'end', 'control'])
    data.to_csv("csc/changes_to_plot_1", index=False)


if __name__ == '__main__':
    print("hi")
    plot_change(1)