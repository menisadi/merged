from typing import List, Tuple

import numpy as np


def longest_non_decreasing_subsequence(arr: List[int]) -> Tuple[List[int], List[int]]:
    """
    This function takes a list of integers and returns the longest non-decreasing
    subsequence of the list, along with the indices of the subsequence. A subsequence
    of a list is a sequence that can be derived from the original list by deleting
    some or no elements without changing the order of the remaining elements.
    Non-decreasing means that each element of the subsequence is greater than or
    equal to the previous element.

    Args:
        arr: A list of integers.

    Returns:
        A tuple containing two lists: the longest non-decreasing subsequence of
        the input list, and the indices of the subsequence in the original list.
    """
    arr_len = len(arr)
    if arr_len == 0:
        return [], []
    subseq_lens = np.ones(arr_len, dtype=int)
    prev_indices = -np.ones(arr_len, dtype=int)

    for i in range(1, arr_len):
        for j in range(i):
            if arr[j] <= arr[i] and subseq_lens[j] + 1 > subseq_lens[i]:
                subseq_lens[i] = subseq_lens[j] + 1
                prev_indices[i] = j

    end_index = np.argmax(subseq_lens)
    subseq = []
    subseq_indices = []
    i = end_index
    while i >= 0:
        subseq.append(arr[i])
        subseq_indices.append(i)
        i = prev_indices[i]

    return subseq[::-1], subseq_indices[::-1]
