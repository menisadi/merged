import re

import hard_rules
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd


def preprocessing(data):
    needed_columns = [
        "timestamp",
        "filename",
        "maid",
        "hh_id",
        "iiqid",
        "partner_id",
        "ip",
        "iscellip",
        "cellispid",
        "domain",
        "is_house_ip_or_source_ip",
        "brand",
        "model",
        "os",
        "osversion",
        "browser",
        "advertisedbrowser",
        "browserversion",
        "type",
        "is_best_ip",
    ]
    unnecessary_columns = [c for c in data.columns if c not in needed_columns]

    data.drop(unnecessary_columns, axis=1, inplace=True)

    data["time"] = pd.to_datetime(data["timestamp"], unit="ms")

    data.dropna(inplace=True)

    # hh_id contains households id and also non-houdsehols.
    # The former are strings and the later are integers.
    # So we record this in a seperate cell and convert all to str
    data["is_hh"] = data["hh_id"].apply(lambda x: isinstance(x, str))

    data["hh_id"] = data["hh_id"].astype(str)

    return data


def maid2int(m):
    maid_dict = {"maid": 4, "third_party": 7}
    return maid_dict[m]


def int2maid(m_number):
    maid_int_dict = {4: "maid", 7: "third_party"}
    return maid_int_dict[m_number]


def count_perfect_cookies(data, maid=None):
    if maid != None:
        if isinstance(maid, int):
            only_relevant_maid = data[data["maid"] == maid]
        else:
            only_relevant_maid = data[data["maid"] == maid2int(maid)]
    else:
        only_relevant_maid = data

    # filter out versions which are not in the standard format
    # they are rare but breaks the following steps
    pattern = re.compile(r"^\d+(\.\d+)*$")
    only_relevant_maid = only_relevant_maid[
        only_relevant_maid.osversion.str.match(pattern)
    ]

    more_than_one = only_relevant_maid.groupby(
        ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser"]
    ).filter(lambda x: x["iiqid"].nunique() > 1)

    grouped_data = (
        more_than_one.groupby(
            ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser", "iiqid"]
        )
        .agg(
            {
                "browserversion": [hard_rules.min_ver, hard_rules.max_ver],
                "osversion": [hard_rules.min_ver, hard_rules.max_ver],
                "time": ["min", "max"],
            }
        )
        .reset_index()
    )

    grouped_data.columns = [
        "hh_id",
        "brand",
        "model",
        "os",
        "browser",
        "advertisedbrowser",
        "iiqid",
        "min_browser_ver",
        "max_browser_ver",
        "min_os_ver",
        "max_os_ver",
        "min_time",
        "max_time",
    ]

    grouped_data = grouped_data.sort_values(
        by=["hh_id", "brand", "model", "os", "browser", "advertisedbrowser", "min_time"]
    )
    grouped_data["prev_max_time"] = (
        grouped_data.groupby(
            ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser"]
        )["max_time"]
        .shift(1)
        .fillna(pd.Timestamp.min)
    )
    grouped_data["prev_max_browser_ver"] = (
        grouped_data.groupby(
            ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser"]
        )["max_browser_ver"]
        .shift(1)
        .fillna(hard_rules.MINUS_INF_VERSION)
    )
    grouped_data["prev_max_os_ver"] = (
        grouped_data.groupby(
            ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser"]
        )["max_os_ver"]
        .shift(1)
        .fillna(hard_rules.MINUS_INF_VERSION)
    )
    full_valid_rows = grouped_data[
        (grouped_data["min_time"] > grouped_data["prev_max_time"])
        & (
            np.vectorize(hard_rules.compare_versions)(
                grouped_data["min_browser_ver"], grouped_data["prev_max_browser_ver"]
            )
            >= 0
        )
        & (
            np.vectorize(hard_rules.compare_versions)(
                grouped_data["min_os_ver"], grouped_data["prev_max_os_ver"]
            )
            >= 0
        )
    ]

    original_rows_per_hhua = grouped_data.groupby(
        ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser"]
    ).size()
    valid_rows_per_hhua = full_valid_rows.groupby(
        ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser"]
    ).size()
    all_mergable = valid_rows_per_hhua.eq(original_rows_per_hhua)

    result = pd.concat([original_rows_per_hhua, all_mergable], axis=1)
    result.columns = ["cookies", "mergeable"]

    mergable = result.pivot_table(
        values="mergeable",
        columns="cookies",
        index="browser",
        aggfunc=sum,
        fill_value=0,
    ).sort_values(2, ascending=False)
    uq_cookies = result.pivot_table(
        values="mergeable",
        columns="cookies",
        index="browser",
        aggfunc="count",
        fill_value=0,
    ).sort_values(2, ascending=False)

    mergable["+6"] = mergable[[i for i in mergable.columns if i >= 6]].sum(axis=1)
    mergable.drop(
        [i for i in mergable.columns if isinstance(i, int) and i >= 6],
        axis=1,
        inplace=True,
    )
    mergable.columns = [str(i) for i in mergable.columns]

    uq_cookies["+6"] = uq_cookies[[i for i in uq_cookies.columns if i >= 6]].sum(axis=1)
    uq_cookies.drop(
        [i for i in uq_cookies.columns if isinstance(i, int) and i >= 6],
        axis=1,
        inplace=True,
    )
    uq_cookies.columns = [str(i) for i in uq_cookies.columns]

    non_mergable = (uq_cookies - mergable).sort_values(by="2", ascending=False)

    return mergable, non_mergable, uq_cookies


def plot_cookies_dist(data, maid=None):
    maid_number = None
    if maid is not None:
        if isinstance(maid, int):
            maid_number = maid
        else:
            maid_number = maid2int(maid)

    df = preprocessing(data)

    m, n, t = count_perfect_cookies(df, maid_number)

    HH_UA = [
        "hh_id",
        "brand",
        "model",
        "os",
        "browser",
        "advertisedbrowser",
    ]

    fig, axs = plt.subplots(nrows=4, ncols=2)
    fig.set_figheight(16)
    fig.set_figwidth(12)
    plt.subplots_adjust(hspace=0.5)
    fig.suptitle(f"Mergable VS Non-Mergable\n\n{int2maid(maid_number)}")

    total_count = (
        df[df.maid == maid_number].groupby(HH_UA).iiqid.nunique().reset_index()
    )
    top_browsers = (
        total_count.groupby("browser").size().sort_values(ascending=False).index[:8]
    )
    top_browsers = [b for b in top_browsers if b in t.index]
    not_enough_browsers = len(top_browsers) < 8
    i = 0
    while not_enough_browsers and i < len(t.index):
        relevant_browsers = t.sort_values(by="2", ascending=False).index
        if relevant_browsers[i] not in top_browsers:
            top_browsers.append(relevant_browsers[i])
        i += 1
        not_enough_browsers = len(top_browsers) < 8

    for i, b in enumerate(top_browsers):
        all_unique_hh_ua = (
            total_count[total_count["browser"] == b].iiqid.value_counts().sum()
        )

        browser_comparison = pd.concat([n.loc[b], m.loc[b]], axis=1)
        browser_comparison.columns = ["Non Mergable", "Mergable"]
        browser_comparison_normalized = browser_comparison.div(all_unique_hh_ua, axis=0)

        ax = axs.flatten()[i]
        browser_comparison_normalized.plot(kind="bar", stacked=True, ax=ax, legend=0)
        ax.title.set_text(f"{b} : total : {all_unique_hh_ua}")
        ax.set_xlabel("")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="upper center",
            fontsize="medium",
            bbox_to_anchor=(0.5, 0.05),
        )
    plt.show()
