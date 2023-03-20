# plot_home.py
# utility to plot homes
# work with code of preprocessing
import os
import sys
import random
import datetime
import logging.config
import numpy as np
import pprint
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

print(sys.path)
ipchange_proj_root = os.environ.get('IPCHANGE_PROJ_ROOT')
if ipchange_proj_root not in sys.path:
    sys.path.append(ipchange_proj_root)

from ipchange_definitions import *
from ipchange_dataclass import IPChangeDayLimits
from Config.ipchange_config_definitions import CUT_DATA_WITH_TV_DATES, TRAINING_CONFIG, COUNT_HOMES
from ipchange_utils import set_home_ip, filter_home_profiles, create_config_for_preprocessing_use_disk, get_day_limits
from ipchange_utils import get_tv_prof, read_data
from ipchange_feature_utils import get_avg_3_err_min, get_extreme, prepare_errors_norm_num_of_points
from candidate_ip_utils import RANK, PROF_SCORE, POINT_SCORE, PROF_NUM, POINTS_NUM, POINT_NORM_VAL, PROF_NORM_VAL
from preprocessing import prepare_group, set_output, get_data_file, data_cleaning
from preprocessing_utils import set_change_point_limits
from preprocessing_config import set_group

# config logger
# -----------------------------------
logging.config.fileConfig(fname='log.conf')
logger = logging.getLogger(__name__)

logging.getLogger('matplotlib.font_manager').setLevel(logging.INFO)
logging.getLogger('matplotlib').setLevel(logging.INFO)

# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

# GLOBALS
# -----------------------------------
BASE_ERR_PLOTS = 3

regular_anno = '-o'
tv_anno = '-D'
mean_anno = '--'
sum_anno = ':'
large_markersize = 10
small_markersize = 5


def get_data(group_name):
    data_file = get_data_file(group_name)
    df = read_data(data_file)
    df_data = data_cleaning(df).copy()
    return df_data


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
    for id_, id_group in df_hh.groupby(PROF_ID):
        if id_group[IP].unique().size > 1:
            id_mult_ip.append(id_)

    n_colors = len(id_list)
    colours = cm.rainbow(np.linspace(0, 1, n_colors))
    color_dic = dict(zip(id_list, colours))

    axs = fig.get_axes()
    if not isinstance(axs, list):
        axs = [axs]
    axs_idx = -1

    df_hh_grouped = df_hh.groupby(IP)
    for ip in ip_list:
        ip_group = df_hh_grouped.get_group(ip)
        # y_next is constant and change within ID
        y_next = 1
        axs_idx += 1
        axs[axs_idx].set_title('N{:} IP {:}'.format(axs_idx, ip))
        ip_group = ip_group.sort_values([TIMESTAMP], ascending=True)
        # Uniques are returned in order of appearance. Hash table-based unique, therefore does NOT sort.
        id_sub_list = ip_group[PROF_ID].unique()
        ip_grouped_by_id = ip_group.groupby(PROF_ID)
        for id_ in id_sub_list:
            id_group = ip_grouped_by_id.get_group(id_)
            id_group = id_group.sort_values([TIMESTAMP], ascending=True)
            x = id_group[TIMESTAMP].values
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


def plot_err(axs, points, errs, from_ip, to_ip, change_point):
    assert len(axs) >= BASE_ERR_PLOTS
    ax = axs[-3]
    ax.set_title('Error: Number of Points from IP {:} to IP {:}'.format(from_ip, to_ip))
    ax.set_xlabel('Points')
    ax.set_ylabel('Error = Num of Points')
    ax.plot(points, errs[PLOT_NUM_POINT_ERR, :], '-o', markersize=small_markersize)
    ax.grid(True)
    title = 'From IP {:} to IP {:} Col {:}'.format(from_ip, to_ip, PLOT_NUM_POINT_ERR)
    plot_peaks(points, errs[PLOT_NUM_POINT_ERR, :], ax, title)
    if change_point is not None:
        ax.axvline(change_point)

    ax = axs[-2]
    ax.set_title('Error: Number of Profiles from IP {:} to IP {:}'.format(from_ip, to_ip))
    ax.set_xlabel('Points')
    ax.set_ylabel('Error = Num of Profiles')
    ax.plot(points, errs[PLOT_NUM_PROF_ERR, :], '-o', markersize=small_markersize)
    ax.grid(True)
    title = 'From IP {:} to IP {:} Col {:}'.format(from_ip, to_ip, PLOT_NUM_PROF_ERR)
    plot_peaks(points, errs[PLOT_NUM_PROF_ERR, :], ax, title)
    if change_point is not None:
        ax.axvline(change_point)

    ax = axs[-1]
    ax.set_title('Error: Average of Time Intervals from IP {:} to IP {:}'.format(from_ip, to_ip))
    ax.set_xlabel('Points')
    ax.set_ylabel('Error = Average Distance')
    ax.plot(points, errs[PLOT_DIST_ERR, :], '-o', markersize=small_markersize)
    ax.grid(True)
    title = 'From IP {:} to IP {:} Col {:}'.format(from_ip, to_ip, PLOT_DIST_ERR)
    plot_peaks(points, errs[PLOT_DIST_ERR, :], ax, title)
    if change_point is not None:
        ax.axvline(change_point)


def plot_peaks(x_data, y_data, ax, title, negate_data=True):

    x_peak, peak_idx = get_extreme(x_data, y_data, negate_data)
    if peak_idx is not None:
        y_peak = y_data[peak_idx]
        ax.plot(x_peak, y_peak, "X", color='r', markersize=large_markersize)
        ax.set_title(title)


def plot_one_hh(hh, hh_data, tv_prof, day_limits: IPChangeDayLimits, config_train):
    hh_ip = set_home_ip(hh, hh_data)
    hh_data = filter_home_profiles(hh, hh_ip, hh_data)

    ip_pairs, raw_data, df_shared_ips, change_point_ip_list = prepare_group(hh, hh_ip, hh_data, tv_prof,
                                                                            day_limits, config_train)
    fig_list = []

    for from_ip, to_ip in ip_pairs:
        df_ip = df_shared_ips[df_shared_ips[IP] == to_ip]
        if df_ip.empty:
            logger.warning('HH {:} df_shared_ips is empty for to_ip {:}'.format(hh, to_ip))
            to_ip_str = ''
        else:
            to_ip_dic = df_ip.to_dict('records')[0]
            # noinspection LongLine
            to_ip_str = '\nToIP {:} Rank {:} Score Prof {:.2f} Score Point {:.2f} Num Prof {:} Num Point {:} HomeIP Num Prof {:} HomeIP Num Point {:}'\
                .format(to_ip, to_ip_dic[RANK], to_ip_dic[PROF_SCORE], to_ip_dic[POINT_SCORE], to_ip_dic[PROF_NUM], to_ip_dic[POINTS_NUM],
                        to_ip_dic[PROF_NORM_VAL],  to_ip_dic[POINT_NORM_VAL])
        # end if df_ip.empty

        points, errs = prepare_errors_norm_num_of_points(hh, from_ip, to_ip, raw_data, day_limits, config_train)
        err_min = {}
        for col in ONE_PLOT_ERR_TYPES_EXTENDED:
            x_peak, peak_idx = get_extreme(points, errs[col, :], negate=True)
            err_min[col] = x_peak
            logger.debug(
                'HH {:} Err {:} Peaks {:} Peak Index {:}'.format(hh, PLOT_ERR_TYPE2STR[col], x_peak, peak_idx))
        # end for col

        x_peak_vals = np.array([err_min[col] for col in ONE_PLOT_ERR_TYPES if err_min[col] is not None])

        # cp_idx = None
        change_point_est = None
        if x_peak_vals.size > 0:
            change_point_est = get_avg_3_err_min(x_peak_vals)
            logger.info('HH {:} Estimated change point {:}'.format(hh, change_point_est))
            # estimated change point values in min error points
            # cp, cp_idx = find_closest_datetime(change_point_est, points)
        # end if

        ip_list_local = [from_ip, to_ip]
        if change_point_ip_list is not None:
            ip_list_local = np.union1d(ip_list_local, change_point_ip_list)

        fig, axs = plt.subplots(len(ip_list_local) + BASE_ERR_PLOTS, sharex='col')
        fig.suptitle('Home {:} fromIP {:} toIP {:} Change IPs {:} HomeIP {:}{:}'
                     .format(hh, from_ip, to_ip, change_point_ip_list, hh_ip, to_ip_str))
        id_list = raw_data[PROF_ID].unique()
        plot_sequence(fig, hh, ip_list_local, id_list, raw_data, tv_prof, change_point_est)
        plot_err(axs, points, errs, from_ip, to_ip, change_point_est)
        fig_list.append(fig)

    # end for from_ip, to_ip

    return fig_list


def iterate_plot_homes(df_data, tv_prof, home_list, day_limits: IPChangeDayLimits, config_train):
    global random_suf, date_str
    out_file = 'plot_home_{:}_{:}'.format(date_str, random_suf) + '.pdf'
    out_pdf_file = os.path.join(out_dir, out_file)
    out_pdf = PdfPages(out_pdf_file)
    count = config_train[COUNT_HOMES]

    for hh, hh_data in df_data.groupby(HH_ID):
        if (home_list is not None) and (hh not in home_list):
            continue

        # noinspection PyBroadException
        try:
            fig_list = plot_one_hh(hh, hh_data, tv_prof, day_limits, config_train)
        except Exception:
            logger.debug('Exception', exc_info=True)
            continue

        for fig in fig_list:
            plt.figure(fig.number)
            mng = plt.get_current_fig_manager()
            mng.full_screen_toggle()
            plt.pause(0.1)
            out_pdf.savefig(fig)
            plt.close()
        # end for fig

        if count is not None:
            count -= 1
            if count == 0:
                break
    # end for hh

    out_pdf.close()
    logger.info('Write {:}'.format(out_pdf_file))


# -----------------------------------
# MAIN
# -----------------------------------
if __name__ == '__main__':

    random_suf = random.randint(1000, 9999)
    date_str = datetime.datetime.now().strftime("%Y_%m_%d")

    config = create_config_for_preprocessing_use_disk()
    config_train = config[TRAINING_CONFIG]
    config_train[CUT_DATA_WITH_TV_DATES] = False   # for plotting do not cut with tv
    # config_train[COUNT_HOMES] = 10
    out_dir, out_file_pref = set_output("plot")

    for group_name in GROUP_LIST:  # ['A', 'C']:  # GROUP_LIST: #['B']:
        logger.info('--- Group {:} ---'.format(group_name))
        set_group(group_name, config_train)
        # config_train[IS_BIN_FREQ] = True
        logger.info('Config {:}'.format(pprint.pformat(config)))
        df_data = get_data(group_name)
        tv_prof = get_tv_prof(df_data)
        home_list = None
        # home_list = ['2yFp3hzeZa', '3jFjdNFCgJ', '9mb6qRAloS']  # group B TODO for debug
        # home_list = ['20Mw5EtREL']  # group A TODO for debug

        day_limits = get_day_limits(df_data[TIMESTAMP].max(), df_data[TIMESTAMP].min())
        set_change_point_limits(config_train, day_limits)

        # try:
        iterate_plot_homes(df_data, tv_prof, home_list, day_limits, config_train)

        # except Exception as e:
        #    logger.error(e)
        #    continue

    # end for group_name
    logger.info('End plot_home')
