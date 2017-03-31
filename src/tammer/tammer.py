
import json
import os
import datetime

import tornado.web
import tornado.ioloop
from tornado import gen
from tornado.concurrent import run_on_executor
from tornado.log import enable_pretty_logging

import sys
from git_analyzer import GitAnalyzer

from updater import RepositoryUpdater
import Settings


from concurrent.futures import ThreadPoolExecutor

enable_pretty_logging()


EX_OK = getattr(os, "EX_OK", 0)
EX_USAGE = getattr(os, "EX_USAGE", 64)


class UsageError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/update", UpdateHandler),
            (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": Settings.JAVASCRIPT_PATH}),
            (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": Settings.CSS_PATH}),
            (r"/?$", HomeHandler),
            (r"(.*\.json)", JsonHandler),
            (r"/repository/(.*)", RepoHandler),
        ]

        tornado.web.Application.__init__(self, handlers)

        self.git_analyzer = GitAnalyzer()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.updating = False

    @run_on_executor
    def repo_updater(self):
        self.updating = True
        updater = RepositoryUpdater()
        while self.updating:
            updater.update()


class BaseHandler(tornado.web.RequestHandler):
    @property
    def git_analyzer(self):
        return self.application.git_analyzer

    @property
    def executor(self):
        return self.application.executor

    @run_on_executor
    def analyze_repo(self, path):
        self.git_analyzer.init_from_url(path)


class HomeHandler(BaseHandler):
    def get(self):
        self.render("static/home.html", title="Omenia Tammer Home")

    @gen.coroutine
    def post(self):
        path = self.get_argument("repo_url")
        url = self.create_url(path)
        self.executor.submit(self.analyze_repo(path))
        self.redirect(url)

    def create_url(self, path):
        url = path.split("/")
        url = "repository/" + "/".join(url[-2:]).replace(".git", "/")
        if not os.path.exists("static/" + url):
            os.makedirs("static/" + url)
        return url


class JsonHandler(BaseHandler):
    def get(self, file_path):
        path = os.getcwd() + "/static" + file_path
        if os.path.exists(path):
            with open(path, "r") as json_file:
                self.write(json_file.read())


class RepoHandler(BaseHandler):
    def get(self, url):
        self.render("static/index.html", title="Repo")


class UpdateHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        "hello"


class MainHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                repo_url = json_data['repo_url']
            except ValueError:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message)  # Bad Request
                return

            self.executor.submit(self.analyze_repo(repo_url))


def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        if len(argv) != 1:
            raise UsageError("Usage:  %s" % sys.argv[0])

        app = Application()
        app.repo_updater()
        app.listen(3880)
        tornado.ioloop.IOLoop.current().start()

        return EX_OK

    except (UsageError, KeyboardInterrupt):
        app.updating = False
        print "Shutting down backround updater..."
        return EX_USAGE


if __name__ == "__main__":
    sys.exit(main())
