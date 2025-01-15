import unittest
from parameterized import parameterized
from src.utils import helper


class TestHelperMethods(unittest.TestCase):

    @parameterized.expand([
        ["normal", [0, 3, 1], ["0 to 1", "1 to 2", "2 to 3"]]
    ])
    def test_create_bin_ranges(self, test_input, expected_output):
        output = helper.create_bin_ranges(*test_input)
        self.assertEqual(output, expected_output)
