import pandas as pd

# 1. A->constant UA = B-> constant UA
# 2. A->changing(version) UA <= B-> changing(version)UA
# 3. A and B were in the same IP/routers (we currently still work with ips so we need to make sure the ip didnt jump and we are actually looking at two different routers. this is important because we can see two cookies that are actually in different routers and not actually connected at all but think that they are)
# 4. A stopped appearing in any ip before B started appearing for the first time


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings in the format "x.y.z", where x, y, and z are integers.
    Returns 1 if version1 is greater than version2, -1 if version1 is less than version2, and 0 if they are equal.

    Args:
        version1 (str): First version string to compare.
        version2 (str): Second version string to compare.

    Returns:
        int: 1 if version1 is greater than version2, -1 if version1 is less than version2, and 0 if they are equal.
    """
    v1 = version1.split(".")
    v2 = version2.split(".")
    len1, len2 = len(v1), len(v2)
    i = 0

    while i < len1 or i < len2:
        if i >= len1:
            if all(int(n) == 0 for n in v2[i:]):
                return 0  # version 1 is a prefix of version 2 but the sufix is 0
            else:
                return -1
        if i >= len2:
            if all(int(n) == 0 for n in v1[i:]):
                return 0  # version 2 is a prefix of version 1 but the sufix is 0
            else:
                return 1

        if int(v1[i]) < int(v2[i]):
            return -1  # version 1 is less than version 2
        elif int(v1[i]) > int(v2[i]):
            return 1  # version 1 is greater than version 2

        i += 1

    return 0  # version 1 is equal to version 2


def constUA(row: pd.Series[any]) -> pd.Series[any]:
    """
    Extracts the columns "brand", "model", "os", "browser", and "advertisedbrowser" from a row.

    Args:
        row (pd.Series): A row of a Pandas DataFrame.

    Returns:
        pd.Series: pandas Series with only the needed features
    """
    return row[["brand", "model", "os", "browser", "advertisedbrowser"]]


def constUAconsistent(row1: pd.Series, row2: pd.Series) -> bool:
    """
    Check if the columns 'brand', 'model', 'os', 'browser', and 'advertisedbrowser' are equal between two pandas DataFrame rows.

    Returns:
        True if the columns are equal, False otherwise.
    """
    return constUA(row1).equals(constUA(row2))


def changinUAconsistent(row1: pd.Series, row2: pd.Series) -> bool:
    """
    Check if the versions of 'os' and 'browser' in two pandas DataFrame rows are consistent.

    Returns:
        True if the versions are consistent, False otherwise.
    """
    os_consistent = compare_versions(row1["osversion"], row2["osversion"]) < 0
    browser_consistent = (
        compare_versions(row1["browserversion"], row2["browserversion"]) < 0
    )
    return os_consistent and browser_consistent


def time_intersection(row1: pd.Series, row2: pd.Series) -> bool:
    """
    Check if the timestamps of two pandas DataFrame rows intersect.

    Returns:
        True if the timestamps intersect, False otherwise.
    """
    row1["timestamp"] < row2["timestamp"]


def candidate_cookies(df: pd.DataFrame, cookie1: str, cookie2: str) -> bool:
    """Given a dataframe `df` and two cookie identifiers `cookie1` and `cookie2`,
    returns True if the two cookies are candidates for being the same user based on
    the user agent and timestamp data in the dataframe, and False otherwise.

    Args:
        df: A pandas DataFrame containing data on user behavior, including columns
            for "iiqid" (cookie identifier), "brand", "model", "os", "osversion",
            "browser", "browserversion", "advertisedbrowser", and "timestamp".
        cookie1: A string identifying the first cookie to compare.
        cookie2: A string identifying the second cookie to compare.

    Returns:
        A boolean value indicating whether the two cookies are candidates for being
        the same user based on their user agent and timestamp data in the dataframe.
    """
    df_cookie1 = df[df["iiqid"] == cookie1]
    df_cookie2 = df[df["iiqid"] == cookie2]
    first_ck1, last_ck1 = (
        df_cookie1[df_cookie1["timestamp"].min()],
        df_cookie1[df_cookie1["timestamp"].max()],
    )
    first_ck2, last_ck2 = (
        df_cookie2[df_cookie2["timestamp"].min()],
        df_cookie2[df_cookie2["timestamp"].max()],
    )
    if last_ck1["timestamp"] < first_ck2["timestamp"]:
        return constUAconsistent(last_ck1, first_ck2) and changinUAconsistent(
            last_ck1, first_ck2
        )
    elif first_ck1["timestamp"] > last_ck2["timestamp"]:
        return constUAconsistent(first_ck1, last_ck2) and changinUAconsistent(
            first_ck1, last_ck2
        )

    return False
