import pandas as pd
import matplotlib.pyplot as plt

def longest_sequence(data, name_str='id', start_str='start', end_str='end'):
    """
    Given a Pandas DataFrame `data` with columns `name_str`, `start_str`, and `end_str`,
    returns the IDs in the longest sequence of intervals that overlap.

    Args:
        data (pd.DataFrame): DataFrame containing interval data.
        name_str (str, optional): Name of the column containing the IDs. Defaults to 'id'.
        start_str (str, optional): Name of the column containing the start times.
        Defaults to 'start'.
        end_str (str, optional): Name of the column containing the end times. Defaults to 'end'.

    Returns:
        List: IDs in the longest sequence of overlapping intervals.

    """
    # Sort dataframe by start time
    data = data.sort_values(by=start_str)

    # Initialize dictionary to keep track of longest sequences
    # ending with each id
    seq_lengths = {i: e - s for i, s, e in data[[name_str, start_str, end_str]].values}

    # Initialize dictionary to keep track of the previous id
    # in the longest sequence ending with each id
    prev_ids = {i: None for i in data[name_str].values}

    for i in range(len(data)):
        curr_row = data.iloc[i]
        for j in range(i):
            prev_row = data.iloc[j]
            curr_interval = curr_row[end_str] - prev_row[end_str]
            if prev_row[end_str] <= curr_row[end_str] and prev_row[end_str] >= curr_row[start_str]:
                if seq_lengths[curr_row[name_str]] < seq_lengths[prev_row[name_str]] \
                            + curr_interval:
                    seq_lengths[curr_row[name_str]] = seq_lengths[prev_row[name_str]] \
                            + curr_interval
                    prev_ids[curr_row[name_str]] = prev_row[name_str]

    # Find id with longest sequence ending with it
    end_id = max(seq_lengths, key=seq_lengths.get)

    # Reconstruct longest sequence
    seq = []
    while end_id is not None:
        seq.insert(0, end_id)
        end_id = prev_ids[end_id]

    return seq

def plot_intervals(data, name_str='id', start_str='start', end_str='end',
                   color='blue', highlight_ids=None, highlight_color='red'):
    """
    Given a Pandas DataFrame `data` with columns `name_str`, `start_str`, and `end_str`,
    plots a horizontal bar chart with the intervals for each row.

    Args:
        data (pd.DataFrame): DataFrame containing interval data.
        name_str (str, optional): Name of the column containing the IDs. Defaults to 'id'.
        start_str (str, optional): Name of the column containing the start times.
        Defaults to 'start'.
        end_str (str, optional): Name of the column containing the end times.
        Defaults to 'end'.
        color (str, optional): Color to use for the bars. Defaults to 'blue'.
        highlight_ids (List[str], optional): List of IDs to highlight with a different color.
        Defaults to None.
        highlight_color (str, optional): Color to use for highlighted bars. Defaults to 'red'.

    Returns:
        None
    """
    # Create a horizontal bar chart with the intervals for each row
    fig, ax = plt.subplots(figsize=(8, 3))
    for i, row in data.iterrows():
        name = row[name_str]
        start = row[start_str]
        end = row[end_str]
        if highlight_ids and name in highlight_ids:
            ax.broken_barh([(start, end - start)], (i, 1), label=name, facecolors=highlight_color)
        else:
            ax.broken_barh([(start, end - start)], (i, 1), label=name, facecolors=color)

    # Add legend and axis labels
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_xlabel('Time')
    ax.set_ylabel('Row')

    # Show the plot
    plt.show()
