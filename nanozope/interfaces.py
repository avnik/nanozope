from zope.interface import Interface, implements

ZODB_CONNECTION_KEY = 'zodb.connection'

class IConfiguration(Interface):
    """Utility marker"""

class IAfterCallEvent(Interface):
    """Marker for subscription"""

class AfterCallEvent(object):
    implements(IAfterCallEvent)
    def __init__(self, request, obj):
        self.request = request
        self.obj = obj
