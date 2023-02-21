import unittest

from hard_rules import compare_versions, trim_version


class TestVersionFunctions(unittest.TestCase):
    def test_trim_version(self):
        self.assertEqual(trim_version("1.0.0"), ["1"])
        self.assertEqual(trim_version("1.2.3.0"), ["1", "2", "3"])
        self.assertEqual(trim_version("0"), ["0"])
        self.assertEqual(trim_version("0.0.0.0"), ["0"])
        self.assertEqual(trim_version("10.0"), ["10"])
        self.assertEqual(
            trim_version("1.2.3.4.5.6.7.8.9"),
            ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
        )

    def test_compare_versions(self):
        self.assertEqual(compare_versions("1", "2"), -1)
        self.assertEqual(compare_versions("1.0.0", "1.0"), 0)
        self.assertEqual(compare_versions("1.2.3", "1.2.3.0"), 0)
        self.assertEqual(compare_versions("1.2.3", "1.2.2"), 1)
        self.assertEqual(compare_versions("2.3.4", "1.3.4"), 1)
        self.assertEqual(compare_versions("1.2.3", "1.2.4"), -1)
        self.assertEqual(compare_versions("1.2.3", "1.2.3.4"), 0)
        self.assertEqual(compare_versions("1.2.3.4", "1.2.3"), 0)
        self.assertEqual(compare_versions("1.2.3.4", "1.2.3.4"), 0)
        self.assertEqual(compare_versions("0", "0.0"), 0)
        self.assertEqual(compare_versions("108.0.0.0", "108.1.5.3"), 0)
        self.assertEqual(compare_versions("108.3", "108.2.3.1"), 1)
