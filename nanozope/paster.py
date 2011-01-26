from paste.script.appinstall import Installer
from nanozope.bootstrap import bootstrap_database_from_paster
from nanozope.config import Configuration

class ZopeInstaller(Installer):
    def setup_config(self, command, filename, section, vars):
        self._call_setup_app(self._bootstrap_zope, 
            command, filename, section, vars)

    def _bootstrap_zope(self, dummy, conf, vars):
        c = Configuration(conf)
        bootstrap_database_from_paster(c.paster['zodb_uri'], 
            c.paster['root_name'])
