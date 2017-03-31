import unittest
from updater import RepositoryUpdater
from mock import Mock, patch
import os  # NOQA
import time  # NOQA


class TestUpdater(unittest.TestCase):
    def setUp(self):
        self.sut = RepositoryUpdater()
        self.git_analyzer_mock = Mock()
        self.sut.git_analyzer = self.git_analyzer_mock

    @patch('os.walk')
    @patch('time.sleep')
    @patch('time.time')
    def test_update_repositories_first_time(self, mock_time,
                                            mock_sleep, mock_walk):
        mock_walk.return_value = iter([
                ('/repos', ('bar',), ('baz'))
                ])
        mock_time.side_effect = [0, 1]

        self.sut.update()

        mock_sleep.assert_called_once_with(2)
        self.git_analyzer_mock.init_from_path.assert_called_once_with(
                'repos/bar')
        self.assertEqual(2, mock_time.call_count)
        self.assertEqual(1, self.sut.repositories['bar'])

    @patch('os.walk')
    @patch('time.sleep')
    @patch('time.time')
    def test_update_repositories_again_in_less_than_hour(self, mock_time,
                                                         mock_sleep,
                                                         mock_walk):
        mock_walk.side_effect = [
                iter([('/repos', ('bar',), ('baz'))]),
                iter([('/repos', ('bar',), ('baz'))])
                ]
        mock_time.side_effect = [0, 1, 60 * 60]

        self.sut.update()
        self.sut.update()

        self.assertEqual(2, mock_sleep.call_count)
        self.git_analyzer_mock.init_from_path.assert_called_once_with(
                'repos/bar')
        self.assertEqual(3, mock_time.call_count)
        self.assertEqual(1, self.sut.repositories['bar'])

    @patch('os.walk')
    @patch('time.sleep')
    @patch('time.time')
    def test_update_repositories_again_in_more_than_hour(self, mock_time,
                                                         mock_sleep,
                                                         mock_walk):
        mock_walk.side_effect = [
                iter([('/repos', ('bar',), ('baz'))]),
                iter([('/repos', ('bar',), ('baz'))])
                ]
        mock_time.side_effect = [0, 1, 60 * 60 + 2, 60 * 60 + 3]

        self.sut.update()
        self.sut.update()

        self.assertEqual(2, mock_sleep.call_count)
        self.assertEqual(2, self.git_analyzer_mock.init_from_path.call_count)
        self.git_analyzer_mock.init_from_path.assert_any_call(
                'repos/bar')
        self.assertEqual(4, mock_time.call_count)
        self.assertEqual(60 * 60 + 3, self.sut.repositories['bar'])
