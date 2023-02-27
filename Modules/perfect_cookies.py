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


def count_perfect_coolies(data, maid=0):
    if maid != 0:
        only_relevant_maid = data[data["maid"] == maid]
    else:
        only_relevant_maid = data

    more_than_one = only_relevant_maid.groupby(
        ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser"]
    ).filter(lambda x: x["iiqid"].nunique() > 1)

    grouped_data = (
        more_than_one.groupby(
            ["hh_id", "brand", "model", "os", "browser", "advertisedbrowser", "iiqid"]
        )
        .agg({"time": ["min", "max"]})
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
    full_valid_rows = grouped_data[
        grouped_data["min_time"] > grouped_data["prev_max_time"]
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
