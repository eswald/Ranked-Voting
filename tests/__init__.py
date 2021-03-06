r'''Ranked-Pairs Voting Test Suite
    These hacks are required to test within Google App Engine.
    In addition, easy_install WebTest and unittest2,
    and run unit2 or nosetests with PYTHONPATH=../google_appengine
'''#"""#'''

try:
    import unittest2 as unittest
except ImportError:
    import unittest

def fixpaths():
    import sys
    from os.path import abspath, dirname, join
    from warnings import filterwarnings
    
    # Disable the DeprecationWarnings for use of the md5 and sha modules.
    filterwarnings("ignore", category=DeprecationWarning)
    
    # Add AppEngine-specific paths to the import path.
    root_path = dirname(dirname(abspath((__file__))))
    google_path = join(dirname(root_path), "google_appengine")
    sys.path.insert(0, join(google_path, "lib", "yaml", "lib"))
    sys.path.insert(0, join(google_path, "lib", "antlr3"))
    sys.path.insert(0, join(google_path, "lib", "ipaddr"))
    sys.path.insert(0, join(google_path, "lib", "django"))
    sys.path.insert(0, join(google_path, "lib", "fancy_urllib"))
    sys.path.insert(0, join(google_path, "lib", "webob"))
    sys.path.insert(0, google_path)
    
    return root_path
root_path = fixpaths()

def setup():
    from google.appengine.tools import dev_appserver
    from google.appengine.tools.dev_appserver_main import (
        ARG_CLEAR_DATASTORE,
        ARG_LOG_LEVEL,
        DEFAULT_ARGS,
        logging,
    )
    
    option_dict = DEFAULT_ARGS.copy()
    option_dict[ARG_CLEAR_DATASTORE] = True
    
    logging.basicConfig(level=option_dict[ARG_LOG_LEVEL],
        format="%(levelname)-8s %(asctime)s %(filename)s] %(message)s")
    config, matcher = dev_appserver.LoadAppConfig(root_path, {})
    dev_appserver.SetupStubs(config.application, **option_dict)

class VotingTestCase(unittest.TestCase):
    def setUp(self):
        from google.appengine.ext import testbed
        self.logout()
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
    
    def login(self, email="test@somewhere.com", admin=False):
        from os import environ
        from google.appengine.api.users import User
        
        #environ["USER_IS_ADMIN"] = str(int(bool(admin)))
        environ["USER_IS_ADMIN"] = ("1" if admin else "0")
        environ["USER_EMAIL"] = email
        return User(email=email)
    
    def logout(self):
        from os import environ
        
        fields = [
            "USER_IS_ADMIN",
            "USER_EMAIL",
            "USER_ID",
            "FEDERATED_IDENTITY",
            "FEDERATED_PROVIDER",
        ]
        
        for field in fields:
            try:
                del environ[field]
            except KeyError:
                pass
