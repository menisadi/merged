import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# create a sample dataframe
data = {
    "timestamp": [
        "2022-01-01 10:00:00",
        "2022-01-01 10:01:00",
        "2022-01-01 10:02:00",
        "2022-01-01 10:03:00",
        "2022-01-01 10:04:00",
        "2022-01-01 10:05:00",
        "2022-01-01 10:06:00",
        "2022-01-01 10:07:00",
    ],
    "user_id": [1, 2, 3, 4, 1, 2, 3, 4],
    "browser_version": [
        "chrome 108.0.1.4",
        "firefox 92.0.1",
        "chrome 108.0.0.0",
        "firefox 93.0.1",
        "chrome 109.0.0.0",
        "firefox 94.0",
        "chrome 109.0.1.1",
        "firefox 95.0",
    ],
}

df = pd.DataFrame(data)

# select the users you want to plot
user_ids = [1, 2, 3, 4]
df = df[df["user_id"].isin(user_ids)]

# convert timestamp to datetime and set it as the index
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.set_index("timestamp", inplace=True)

# create a new column for each user that contains the browser version
for user_id in user_ids:
    user_df = df[df["user_id"] == user_id]
    browser_versions = (
        user_df["browser_version"]
        .str.split(" ", expand=True)[1]
        .str.split(".", expand=True)
    )
    browser_versions = browser_versions.astype(int)
    for i in range(1, 4):
        zero_mask = browser_versions[i] == 0
        next_subversion = browser_versions[i][~zero_mask].shift(-1)
        browser_versions[i][zero_mask] = next_subversion[zero_mask]
    df.loc[
        df["user_id"] == user_id, ["major", "minor", "patch", "subpatch"]
    ] = browser_versions.values

# plot the data
for user_id in user_ids:
    user_df = df[df["user_id"] == user_id]
    version = (
        user_df["major"]
        + user_df["minor"] / 100
        + user_df["patch"] / 10000
        + user_df["subpatch"] / 1000000
    )
    zeros_mask = user_df["subpatch"] == 0
    for i in range(1, 4):
        zero_mask = user_df["subpatch"] == 0
        lower = version.shift(1)[zero_mask]
        upper = version.shift(-1)[zero_mask]
        lower.fillna(version.iloc[0], inplace=True)
        upper.fillna(version.iloc[-1], inplace=True)
        plt.fill_between(user_df.index[zero_mask], lower, upper, alpha=0.2)
    plt.plot(user_df.index, version, label=f"User {user_id}")

plt.legend()
plt.xlabel("Time")
plt.ylabel("Browser Version")
plt.show()
