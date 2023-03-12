import unittest

import numpy as np

from lnds import longest_non_decreasing_subsequence


class TestLongestNonDecreasingSubsequence(unittest.TestCase):
    def test_general_case(self):
        arr1 = np.array([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])
        self.assertEqual(longest_non_decreasing_subsequence(arr1), [3, 4, 5, 5, 5])

    def test_empty_array(self):
        arr2 = np.array([])
        self.assertEqual(longest_non_decreasing_subsequence(arr2), [])

    def test_array_one_element(self):
        arr3 = np.array([5])
        self.assertEqual(longest_non_decreasing_subsequence(arr3), [5])

    def test_array_decreasing_order(self):
        arr4 = np.array([9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual(longest_non_decreasing_subsequence(arr4), [9])

    def test_array_all_elements_same(self):
        arr5 = np.array([2, 2, 2, 2, 2, 2, 2])
        self.assertEqual(
            longest_non_decreasing_subsequence(arr5), [2, 2, 2, 2, 2, 2, 2]
        )

    def test_array_some_repeated_elements(self):
        arr6 = np.array([1, 2, 2, 2, 3, 10, 3, 4, 1, 4, 5, 6])
        self.assertEqual(
            longest_non_decreasing_subsequence(arr6), [1, 2, 2, 2, 3, 3, 4, 4, 5, 6]
        )


if __name__ == "__main__":
    unittest.main()
