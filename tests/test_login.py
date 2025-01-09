import unittest
from streamlit.testing.v1 import AppTest


class LoginTest(unittest.TestCase):
    def test_login(self):
        at = AppTest.from_file("C:/Users/jumacp/PycharmProjects/dp_db/login.py")
        at.run()
        assert not at.exception


if __name__ == '__main__':
    unittest.main()
