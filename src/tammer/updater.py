import time
import os
from git_analyzer import GitAnalyzer

HOUR = 60 * 60


class RepositoryUpdater(object):
    def __init__(self):
        self.counter = 0
        self.git_analyzer = GitAnalyzer()
        self.repositories = dict()

    def update(self):
        self._update_active_repositories_list()
        self._update_repository()
        time.sleep(2)

    def _update_active_repositories_list(self):
        (_, repos, _) = os.walk("repos").next()
        for repo in repos:
            if repo not in self.repositories:
                self.repositories[repo] = 0

    def _update_repository(self):
        current_time = time.time()
        for repo, timestamp in self.repositories.iteritems():
            if current_time - timestamp > HOUR or timestamp == 0:
                self.git_analyzer.init_from_path("repos/" + repo)
                self.repositories[repo] = time.time()
