from zope.interface import implements
from zope.configuration import config, xmlconfig
from zope.security.interfaces import IParticipation
from zope.security.management import system_user
import zope.processlifetime
from zope.event import notify

class SystemConfigurationParticipation(object):
    implements(IParticipation)

    principal = system_user
    interaction = None


def asSystemUser(func):
    def wrapper(*a, **kw):
        from zope.security.management import newInteraction
        from zope.security.management import endInteraction
        newInteraction(SystemConfigurationParticipation())
        result = func(*a, **kw)
        endInteraction()
        return result
    return wrapper

@asSystemUser
def load_configuration(zcml, features=()):
    context = config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    for feature in features:
        context.provideFeature(feature)
    context = xmlconfig.file(zcml, context=context, execute=True)
    return context

@asSystemUser
def bootstrap_database(zodb_uri):
    from repoze.zodbconn.uri import db_from_uri
    import zope.processlifetime
    import transaction
    db = db_from_uri(zodb_uri)
    try:
        notify(zope.processlifetime.DatabaseOpened(db))
    except:
        transaction.get().abort()
        raise
    else:
        transaction.get().commit()
