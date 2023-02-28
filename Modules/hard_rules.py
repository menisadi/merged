from functools import cmp_to_key

MINUS_INF_VERSION = "0.0.0.0"


def versions_key(versions_series):
    """
    Compute integer keys for sorting a pandas Series of version numbers
    in a natural way.

    Parameters:
        versions_series (pandas.Series): A Series of version numbers as strings.

    Returns:
        pandas.Series: A Series of integer keys, where each key corresponds to a version number in the input
        Series and can be used for sorting the version numbers in a natural way.
    """
    expanded = versions_series.str.split(".", expand=True).fillna(value="0").astype(int)
    return (
        expanded.iloc[:, ::-1] * [10**i for i in range(0, len(expanded.columns))]
    ).sum(axis=1)


def trim_version(version):
    """
    Remove any trailing zeros from a version number and return the parts as a list of strings.

    Parameters:
        version (str): A version number as a string.

    Returns:
        list of str: A list of string parts with any trailing zeros removed, or the single string '0' if
        the version number is all zeros.
    """
    parts = version.split(".")
    last_nonzero_part = len(parts)
    found_non_zero = False
    for i in range(len(parts) - 1, -1, -1):
        if int(parts[i]) != 0:
            last_nonzero_part = i + 1
            found_non_zero = True
            break
    trimmed_parts = parts[:last_nonzero_part]
    return trimmed_parts if found_non_zero else ["0"]


def compare_versions(version1, version2):
    """
    Compare two version numbers and return -1, 0, or 1 to indicate whether the first version number is less
    than, equal to, or greater than the second version number. The comparison is based on the natural order
    of version numbers, with any trailing zeros treated as unknown.

    Parameters:
        version1 (str): The first version number as a string.
        version2 (str): The second version number as a string.

    Returns:
        int: -1 if version1 is less than version2, 0 if version1 is equal to version2, or 1 if version1
        is greater than version2.
    """
    # split and remove trailing zeros, as we treat them as 'unkown'
    v1 = trim_version(version1)
    v2 = trim_version(version2)

    len1, len2 = len(v1), len(v2)
    i = 0

    while i < len1 or i < len2:
        if i >= len1 or i >= len2:
            return 0  # if one is a prefix of the other then for our purposes they are equal

        if int(v1[i]) < int(v2[i]):
            return -1  # version 1 is less than version 2
        elif int(v1[i]) > int(v2[i]):
            return 1  # version 1 is greater than version 2

        i += 1

    return 0  # version 1 is equal to version 2


def min_ver(hh_ua_vers):
    key_func = cmp_to_key(compare_versions)
    min_ver = min(hh_ua_vers, key=key_func)
    return min_ver


def max_ver(hh_ua_vers):
    key_func = cmp_to_key(compare_versions)
    max_ver = max(hh_ua_vers, key=key_func)
    return max_ver


def constUA(row):
    """
    Return a pandas Series containing the 'brand', 'model', 'os', 'browser', and 'advertisedbrowser' columns
    of the input row. This function is used to extract the constant columns that are used to identify the user agent.

    Parameters:
        row (pandas.Series): A row from a pandas DataFrame representing the constant part of the user agent.

    Returns:
        pandas.Series: A Series containing the constant part of the user agent
        of the input row.
    """
    return row[["brand", "model", "os", "browser", "advertisedbrowser"]]


def constUAconsistent(row1, row2):
    """
    Determine whether two rows representing user agents have the same constant identifying information.
    This function is used to check if two user agents belong to the same device and browser.

    Parameters:
        row1 (pandas.Series): A row from a pandas DataFrame representing a user agent.
        row2 (pandas.Series): Another row from a pandas DataFrame representing a user agent.

    Returns:
        bool: True if the constant part of of the two rows are equal, False otherwise.
    """
    return constUA(row1).equals(constUA(row2))


def changinUAconsistent(row1, row2):
    """
    Determine whether two rows representing user agents have consistent version information.
    This function is used to check if two user agents can belong to the same user.

    Parameters:
        row1 (pandas.Series): A row from a pandas DataFrame representing a user agent.
        row2 (pandas.Series): Another row from a pandas DataFrame representing a user agent.

    Returns:
        bool: True if the 'osversion' column of row1 is less than or equal to the 'osversion' column of row2,
        and the 'browserversion' column of row1 is less than or equal to the 'browserversion' column of row2,
        False otherwise.
    """
    os_consistent = compare_versions(row1["osversion"], row2["osversion"]) <= 0
    browser_consistent = (
        compare_versions(row1["browserversion"], row2["browserversion"]) <= 0
    )
    return os_consistent and browser_consistent


def candidate_cookies(df, cookie1, cookie2):
    """
    Given a DataFrame `df` containing web analytics data, and the IDs of two cookies `cookie1` and `cookie2`,
    returns a boolean indicating whether these two cookies are considered "candidates" for being the same user, based on the following criteria:

    1. The first (earliest) event associated with `cookie1` occurred before the last (most recent) event associated with `cookie2`.
       In this case, the function returns True if and only if the "constant" parts of the user agents (browser, browser version, OS,
       OS version) associated with the last event of `cookie1` and the first event of `cookie2` are the same AND the "changing"
       parts of these user agents are consistent (that is, the OS and browser versions associated with the last event of `cookie1`
       are either equal to or older than the versions associated with the first event of `cookie2`).

    2. The first event associated with `cookie2` occurred before the last event associated with `cookie1`.
       In this case, the function returns True if and only if the "constant" parts of the user agents associated with the first event
       of `cookie1` and the last event of `cookie2` are the same AND the "changing" parts of these user agents are consistent (that
       is, the OS and browser versions associated with the first event of `cookie1` are either equal to or older than the versions
       associated with the last event of `cookie2`).

    If neither of the above conditions is satisfied, the function returns False.
    """
    df_cookie1 = df[df["iiqid"] == cookie1]
    df_cookie2 = df[df["iiqid"] == cookie2]
    first_ck1, last_ck1 = (
        df_cookie1.iloc[df_cookie1["timestamp"].argmin()],
        df_cookie1.iloc[df_cookie1["timestamp"].argmax()],
    )
    first_ck2, last_ck2 = (
        df_cookie2.iloc[df_cookie2["timestamp"].argmin()],
        df_cookie2.iloc[df_cookie2["timestamp"].argmax()],
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
