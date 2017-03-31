import string
import random

import psutil
from robot.libraries.BuiltIn import BuiltIn


class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)

    __setattr__ = dict.__setitem__


class TestUtils:
    ###############################
    # TEST DATA GENERATION
    ###############################

    def create_data_dict(self, *args):
        data = DotDict()

        for arg in args:
            name, value = self._parse_data(arg)
            data[name] = value

        print "*INFO* %r" % data
        return data

    def generate_test_data(self, *args):
        data = []

        for arg in args:
            name, value = self._parse_data(arg)
            data += [value]
            if name:
                self._set_robot_variable(name, value)

        print "*INFO* %s" % data

        return data[0] if len(data) == 1 else data

    def _parse_data(self, arg):
        arg = str(arg)

        name, value = arg.split("=") if "=" in arg else (None, arg)
        value = self._parse_value(value)

        return name, value

    def _parse_value(self, value):
        if len(value) > 1 and value[0] == value[-1] == '"':
            return str(value[1:-1])
        else:
            candidates = []
            for token in value.split(","):
                if len(token) > 1 and token[0] == token[-1] == '"':
                    candidates += [token[1:-1]]
                elif token == "text":
                    candidates += [''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))]
                elif "->" in token:
                    start, end = token.split("->")
                    candidates += range(int(start), int(end)+1)
                else:
                    candidates += [token]

            return str(random.choice(candidates))

    def _set_robot_variable(self, name, value):
        scope, variable = name.split(".") if "." in name else ("test", name)

        if scope == "test":
            BuiltIn().set_test_variable("${%s}" % variable, value)
        elif scope == "suite":
            BuiltIn().set_suite_variable("${%s}" % variable, value)
        elif scope == "global":
            BuiltIn().set_global_variable("${%s}" % variable, value)
        else:
            scope = "???"

        print("*INFO* %s=%s [%s]" % (variable, value, scope))

    def close_os_browsers(self):
        selenium = BuiltIn().get_library_instance("Selenium2Library")

        try:
            selenium.close_all_browsers()
        except:
            pass

        # me = psutil.Process()
        # for proc in psutil.process_iter():
        #     if self._ancestor_and_descendant(me, proc):
        #         print "***INFO*** killed %i %s %r" % (proc.pid, proc.name(), proc.cmdline())
        #         proc.kill()
        #         proc.wait()

    def _ancestor_and_descendant(self, ancestor, descendant):
        while descendant:
            descendant = descendant.parent()
            if descendant == ancestor:
                return True
        return False
