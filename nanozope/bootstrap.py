import logging
from zope.interface import implements
from zope.configuration import config, xmlconfig
from zope.security.interfaces import IParticipation
from zope.security.management import system_user
from zope.site.folder import rootFolder
from zope import site
import zope.lifecycleevent
import zope.processlifetime
from zope.event import notify
import transaction

logger = logging.getLogger('nanozope')

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
    logging.info('Loading configuration from %s' % zcml)
    context = config.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    for feature in features:
        context.provideFeature(feature)
    context = xmlconfig.file(zcml, context=context, execute=True)
    return context

def _bootstrap_zodb(conn, root_name):
    root = conn.root()
    created = False
    if not root_name in root:
        root_folder = rootFolder()
        notify(zope.lifecycleevent.ObjectCreatedEvent(root_folder))
        root[root_name] = root_folder
        if not zope.component.interfaces.ISite.providedBy(root_folder):
            site_manager = site.LocalSiteManager(root_folder)
            root_folder.setSiteManager(site_manager)
        transaction.commit()
        created = True
        try:
            from z3c.configurator import configure
        except ImportError:
            pass
        else:
            logging.info('We have z3c.configurator, fire his events!')
            configure(root_folder, {})
    logging.info('Firing events...')
    notify(zope.processlifetime.DatabaseOpenedWithRoot(conn.db()))
    return created

@asSystemUser
def bootstrap_database(conn, root_name):
    import zope.processlifetime
    import transaction
    try:
        logging.info('Bootstrapping ZODB')
        created = _bootstrap_zodb(conn, root_name)
    except:
        logging.error('database bootstrap failed')
        transaction.get().abort()
        raise
    else:
        logging.info('Commiting bootstrap transaction')
        transaction.get().commit()
        logging.info('done')

def bootstrap_database_from_paster(zodb_uri, root_name):
    from repoze.zodbconn.uri import db_from_uri
    db = db_from_uri(zodb_uri)
    conn = db.open()
    bootstrap_database(conn, root_name)
    conn.close()
