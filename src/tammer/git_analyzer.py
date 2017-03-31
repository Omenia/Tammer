#!/usr/bin/env python
import hashlib

import git
import json
import sys
import os
import shutil
import time


EX_OK = getattr(os, "EX_OK", 0)
EX_USAGE = getattr(os, "EX_USAGE", 64)


class UsageError(Exception):
    def __init__(self, msg):
        self.msg = msg

registry = []


class RegisteringType(type):
    def __init__(cls, name, bases, attrs):
        for key, val in attrs.iteritems():
            column = getattr(val, 'column', None)
            if column is not None:
                registry.append((column, val))


def column(column_id):
    def decorator(func):
        func.column = column_id
        return func
    return decorator


class GitAnalyzer(object):
    __metaclass__ = RegisteringType

    def __init__(self):
        self.url = None
        self.path = None

        self.repo = None

        self.data = {
            "charts": {
                "Original": [['ID', 'Gap', 'Inventory', 'Conflicts']],
                "Prototype": [['ID', 'Age', 'Gap', 'Conflicts', 'Inventory']],
            },
        }

    def init_from_url(self, url):
        self.url = url

        md5 = hashlib.md5(url).hexdigest()
        self.path = os.path.join("repos", md5)

        if os.path.exists(self.path):
            shutil.rmtree(self.path)

        try:
            self.repo = git.Repo.clone_from(url, self.path)
        except git.exc.GitCommandError:
            return None

        self._create_dataset()
        self.write_data_to_file(self._create_path(url))
        print "Wrote data to: ", self._create_path(url)

    def _create_path(self, url):
        url = url.split("/")
        return "repository/" + "/".join(url[-2:]).replace(".git", "/")

    def init_from_path(self, path):
        self.path = path
        self.repo = git.Repo(path)
        self.url = self.repo.config_reader().get('remote "origin"', "url")

        self._create_dataset()

    def write_data_to_file(self, filename):
        self.data["url"] = self.url

        with open(os.getcwd() + "/static/" + filename + "data.json", "w") as data:
            data.write(json.dumps(self.data))

    def clean_repo_state(self):
        self.repo.git.checkout('origin/master')

    def _create_dataset(self):
        if not self.repo:
            raise UsageError("Repository must be initialized from url or folder")

        self.repo.git.checkout('origin/master')

        branches = self.repo.git.branch('-r', '--no-merged', 'origin/master').split()

        for idx, branch in enumerate(branches):
            print "Processing %d / %d" % (idx, len(branches))
            branch_data = {col: func(self, branch) for col, func in registry}

            for values in self.data["charts"].values():
                values.append([branch_data[col] for col in values[0]])

        self.clean_repo_state()

    @column("ID")
    def get_id(self, branch_name):
        return branch_name

    @column("Committer")
    def get_last_committer(self, branch_name):
        return self.repo.git.log('-1', '--pretty=%an', branch_name)

    @column("Commit Date")
    def get_last_commit_date(self, branch_name):
        return self.repo.git.log('-1', '--date=local', '--pretty=%cd', branch_name)

    @column("Age")
    def calculate_age(self, branch_name):
        a = self.repo.git.log('-1', '--pretty=%at', branch_name)
        if not a:
            return 0
        a = time.time() - float(a)
        a /= (60 * 60 * 24)
        return int(a)

    @column("Conflicts")
    def calculate_conflicts(self, branch):
            file_list = self._find_conflicting_files(branch, 'origin/master').splitlines()
            if len(file_list) >= 3:
                return len(file_list)/3
            return 0

    def _find_conflicting_files(self, branch, starting_point):
        unmerged = ''
        try:
            self.repo.git.merge('--no-commit', '--no-ff', branch)
        except git.exc.GitCommandError:
            unmerged = self.repo.git.ls_files('-u')

        self.repo.git.reset('--hard', starting_point)
        return unmerged

    @column("Inventory")
    def calculate_inventory(self, branch_name):
        try:
            master_hash = self.repo.git.merge_base("origin/master", branch_name)
            diff = self.repo.git.diff("--shortstat", branch_name+".."+master_hash)
            return self._quantify_diff(diff)
        except git.exc.GitCommandError:
            print "%s" % (sys.exc_info()[0])
            return 0


    @column("Gap")
    def calculate_gap(self, branch_name):
        diff = self.repo.git.diff("--shortstat", branch_name+"..origin/master")
        return self._quantify_diff(diff)

    @staticmethod
    def _quantify_diff(diff):
        try:
            insertions = int(diff.split(',')[1].split()[0])
            deletions = int(diff.split(',')[2].split()[0])
            return insertions + deletions
        except IndexError:
            return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        if len(argv) != 2:
            raise UsageError("Usage:  %s git_url" % sys.argv[0])

        git_analyzer = GitAnalyzer()
        git_analyzer.init_from_path(argv[1])

        print json.dumps(git_analyzer.data, sort_keys=True, indent=4)

        return EX_OK

    except UsageError, err:
        print >>sys.stderr, err.msg
        return EX_USAGE


if __name__ == "__main__":
    sys.exit(main())
