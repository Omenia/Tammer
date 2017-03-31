import unittest
from mock import Mock, patch

from git_analyzer import GitAnalyzer
import git  # NOQA


class TestGitAnalyzer(unittest.TestCase):
    def setUp(self):
        self.sut = GitAnalyzer()
        self.file_mock = Mock()
        self.sut.write_data_to_file = self.file_mock

    @patch('git.Repo')
    def test_init_repo_from_url(self, git_repo_mock):
        repo_mock = Mock()
        git_repo_mock.clone_from.return_value = repo_mock
        repo_mock.git.branch.return_value = 'foo'
        repo_mock.git.log.side_effect = ['baz', 1, 10, 15, 20]
        repo_mock.git.merge_base.return_value = '123'
        diff = '762 files changed, 125541 insertions(+), 19439 deletions(-)'
        repo_mock.git.diff.side_effect = [(diff), (diff)]

        self.sut.init_from_url('http://sample.git')

        self.assertEqual(2, repo_mock.git.checkout.call_count)
        repo_mock.git.checkout.assert_any_call(
                'origin/master')

        repo_mock.git.branch.assert_called_once_with(
                '-r', '--no-merged', 'origin/master')

        repo_mock.git.log.assert_any_call(
                '-1', '--pretty=%an', 'foo')
        repo_mock.git.log.assert_any_call(
                '-1', '--date=local', '--pretty=%cd', 'foo')
        repo_mock.git.log.assert_any_call(
                '-1', '--pretty=%at', 'foo')

        repo_mock.git.merge.assert_called_once_with(
                '--no-commit', '--no-ff', 'foo')

        self.assertTrue(repo_mock.git.reset.called)

        repo_mock.git.merge_base.assert_called_once_with(
                "origin/master", 'foo')

        self.assertEqual(2, repo_mock.git.diff.call_count)
        repo_mock.git.diff.assert_any_call("--shortstat", 'foo..123')

        file_called = {
                'charts': {
                        'Prototype': [
                            ['ID', 'Age', 'Gap', 'Conflicts', 'Inventory'],
                            ['foo', 16892, 144980, 0, 144980]
                        ],
                        'Original': [
                            ['ID', 'Gap', 'Inventory', 'Conflicts'],
                            ['foo', 144980, 144980, 0]
                        ]
                    }
                }
        self.file_mock.assert_called_once_with("repository//sample/")
        self.assertEqual(file_called, self.sut.data)
