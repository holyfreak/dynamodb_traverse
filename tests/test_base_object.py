import unittest

from dynamodb_traverse.base import Base


class TestBaseObject(unittest.TestCase):
    def setUp(self) -> None:
        self.test_subject = Base()

    def test_logger(self):
        self.test_subject.info('test message')
