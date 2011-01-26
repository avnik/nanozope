from paste.script.appinstall import Installer

class ZopeInstaller(Installer):
    def setup_config(self, command, filename, section, vars):
        self._call_setup_app(self._bootstrap_zope, 
            command, filename, section, vars)

    def _bootstrap_zope(self, dummy, conf, vars):
        print conf
