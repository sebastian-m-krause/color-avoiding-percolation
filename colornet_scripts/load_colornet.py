from __future__ import division, print_function
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from collections import defaultdict
from scipy.interpolate import interp1d
import json
import logbin


def get_data_from_file(fname):
    d = json.load(open(fname))
    d["k"] = np.array(d["k"])
    d["kc"] = d["Nc"] / (d["Nc"] - 1)
    d["S_color"] = np.array(d["S_color"]) / d["N"]
    return d


def load_glob(glob_arg):
    return [get_data_from_file(fname) for fname in glob(glob_arg)]


def scatter_plot_S_color(data, offset=None, connect_dots=False):
    if offset is None:
        offset = data["kc"]
    ls = ".-" if connect_dots else "."
    plt.loglog(data["k"] - offset, data["S_color"], ls)


def extract_data_points(data_list, offset=None):
    points = []
    for d in data_list:
        if offset is None:
            offset = d["kc"]
        points.extend(list(zip(d['k'] - offset, d['S_color'])))
    return points

def plot_average_S_color(data_list,offset=None,label_string="",error=None):
    points = extract_data_points(data_list,offset)
    lb = logbin.LogBin(points)
    lb.run()
    if error == "both":
        plt.errorbar(lb.xavg,lb.yavg,xerr=lb.xerr,yerr=lb.yerr,label=label_string)
    elif error == "y":
        plt.errorbar(lb.xavg,lb.yavg,yerr=lb.yerr,label=label_string)
    else:
        plt.loglog(lb.xavg,lb.yavg,'.-',label=label_string)

def plot_full_Scolor_curve(fname):
    d = json.load(open(fname))
    plt.plot(np.array(range(len(d['S_color']))) * d['link_res'] * 2 / d['N'], np.array(d['S_color']) / d['N'], '.-',
             label="$N_c=%i$" % d['Nc'])
    return d


def plot_all_curves(glob_arg):
    ds = list(map(plot_full_Scolor_curve, glob(glob_arg)))
    plt.xlabel(r"$<k>$")
    plt.ylabel(r"$S_color$")
    plt.legend(loc=2)
    return ds


def plot_above_kc(d):
    # this is from Sebastian's write-up:
    kc = lambda Nc: Nc / (Nc - 1)
    N_links_c = lambda N, Nc: int(2 * N * kc(Nc))
    N = d['N']
    Nc = d['Nc']
    # k = np.array(range(len(d['S_color'])))*2/d['N'] - kc(Nc)
    k = np.array(d['k']) - kc(Nc)
    S_color = np.array(d['S_color']) / d['N']
    try:
        plt.loglog(k, S_color, '.-', label="$N_c=%i$" % d['Nc'])
        plt.show()
    except ValueError:
        print("Unable to plot, max k is %.5f and max S_color is %.5f" % (max(k), max(S_color)))
    #plt.loglog(k[N_links_c(N,Nc):], S_color[N_links_c(N,Nc):] , label="$N_c=%i$"%d['Nc'])
    return k, S_color


def plot_fits(preloaded=None, glob_arg=None):
    if preloaded is None:
        ds = map(lambda fn: json.load(open(fn)), glob(glob_arg))
    else:
        ds = preloaded
    to_return = map(plot_above_kc, ds)
    return to_return


def plot_averaged_fits(curves):
    S_avg = np.mean([i[1] for i in curves], axis=0)
    S_err = np.std([i[1] for i in curves], axis=0)
    k = np.mean([i[0] for i in curves], axis=0)
    k_err = np.std([i[0] for i in curves], axis=0)
    if sum(k_err) < 1e-7:
        plt.errorbar(k, S_avg, yerr=S_err)
    else:
        plt.errorbar(k, S_avg, xerr=k_err, yerr=S_err)
    plt.plot(k, S_avg, lw=3)
    return k, S_avg, S_err