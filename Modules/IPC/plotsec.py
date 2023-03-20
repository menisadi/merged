from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# GLOBALS
# -----------------------------------
BASE_ERR_PLOTS = 3

regular_anno = '-o'
tv_anno = '-D'
mean_anno = '--'
sum_anno = ':'
large_markersize = 10
small_markersize = 5

# noinspection PyUnusedLocal
def plot_sequence(fig, hh, ip_list, id_list, df_hh, tv_list, change_point):
    """
    Plot Home sequences, multiple plots per IP
    :param fig: figure to plot
    :param hh: home name
    :param ip_list: list of ips to plot
    :param id_list: list of prof ids to plot
    :param df_hh: filtered data of the home
    :param tv_list: list of tv to plot with special annotation
    :param change_point: value on X to plot vertical line
    :return: fig - figure with multiple plots
    """
    id_mult_ip = []
    for id_, id_group in df_hh.groupby('iiqid'):
        if id_group['ip'].unique().size > 1:
            id_mult_ip.append(id_)

    n_colors = len(id_list)
    colours = cm.rainbow(np.linspace(0, 1, n_colors))
    color_dic = dict(zip(id_list, colours))

    axs = fig.get_axes()
    if not isinstance(axs, list):
        axs = [axs]
    axs_idx = -1

    df_hh_grouped = df_hh.groupby('ip')
    for ip in ip_list:
        ip_group = df_hh_grouped.get_group(ip)
        # y_next is constant and change within ID
        y_next = 1
        axs_idx += 1
        axs[axs_idx].set_title('N{:} IP {:}'.format(axs_idx, ip))
        ip_group = ip_group.sort_values(['timestamp'], ascending=True)
        # Uniques are returned in order of appearance. Hash table-based unique, therefore does NOT sort.
        id_sub_list = ip_group['iiqid'].unique()
        ip_grouped_by_id = ip_group.groupby('iiqid')
        for id_ in id_sub_list:
            id_group = ip_grouped_by_id.get_group(id_)
            id_group = id_group.sort_values(['timestamp'], ascending=True)
            x = id_group['timestamp'].values
            y = np.full(x.size, y_next)
            y_next += 1
            color = color_dic[id_]
            anno = regular_anno if id not in tv_list else tv_anno
            lbl = id_ if id_ not in tv_list else 'TV ' + id_
            markersize = large_markersize if id_ in id_mult_ip else small_markersize
            axs[axs_idx].plot(x, y, anno, label=lbl, color=color, markersize=markersize)
        # end for id
        if change_point is not None:
            axs[axs_idx].axvline(change_point)
        axs[axs_idx].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        axs[axs_idx].set_yticks(range(1, len(id_sub_list)+1))
        axs[axs_idx].set_yticklabels(id_sub_list)
        axs[axs_idx].xaxis.grid(True)
    # end for ip
