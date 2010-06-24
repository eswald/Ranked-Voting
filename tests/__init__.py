r'''Ranked-Pairs Voting Test Suite
    These hacks are required to test within Google App Engine.
    In addition, easy_install WebTest and unittest2,
    and run unit2 or nosetests with PYTHONPATH=../google_appengine
'''#"""#'''

import sys
from os.path import abspath, dirname, join

root_path = dirname(dirname(abspath((__file__))))
google_path = join(dirname(root_path), "google_appengine")
sys.path.insert(0, join(google_path, "lib", "yaml", "lib"))
sys.path.insert(0, join(google_path, "lib", "antlr3"))
sys.path.insert(0, join(google_path, "lib", "ipaddr"))
sys.path.insert(0, join(google_path, "lib", "webob"))
sys.path.insert(0, google_path)

from google.appengine.tools import dev_appserver
from google.appengine.tools.dev_appserver_main import *

option_dict = DEFAULT_ARGS.copy()
option_dict[ARG_CLEAR_DATASTORE] = True

def setup():
    logging.basicConfig(level=option_dict[ARG_LOG_LEVEL],
        format="%(levelname)-8s %(asctime)s %(filename)s] %(message)s")
    config, matcher = dev_appserver.LoadAppConfig(root_path, {})
    dev_appserver.SetupStubs(config.application, **option_dict)
