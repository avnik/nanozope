from zope.interface import Interface
from zope.schema import BytesLine, Bool
from zope.component import getGlobalSiteManager
from zope.configuration.config import toargs
from zope.component.hooks import setHooks

from nanozope.interfaces import ZODB_CONNECTION_KEY
from nanozope.interfaces import IConfiguration
from nanozope.bootstrap import load_configuration, bootstrap_database

class IPasterVariables(Interface):
    configure_zcml = BytesLine(title=u"configure.zcml")
    zodb_connection = BytesLine(title=u"ZODB connection key",
        required=True, default=ZODB_CONNECTION_KEY)
    bootstrap_database = Bool(title=u"send bootstrap events",
        required=True, default=True)
    zodb_uri = BytesLine(title=u"ZODB URI")
    root_name = BytesLine(title=u"ZODB Root name",
        required=True, default="Application")


IPasterVariables.setTaggedValue('keyword_arguments', True)

class Configuration(object):
    def __init__(self, paster_variables):
        setHooks()

        self.paster = toargs(self, IPasterVariables, paster_variables)

        getGlobalSiteManager().registerUtility(provided=IConfiguration,
            component=self)
        
        load_configuration(self.paster['configure_zcml'])

        

