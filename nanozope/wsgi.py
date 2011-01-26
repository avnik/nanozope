from zope.publisher.browser import BrowserRequest
from zope.publisher.http import HTTPRequest
from zope.publisher.skinnable import setDefaultSkin
from nanozope.publisher import MinimalisticPublisher
from nanozope.publisher import ZODB_ANNOTATION_KEY
from bootstrap import load_configuration, bootstrap_database
from config import Configuration

browser_methods = set(('HEAD', 'GET', 'POST'))

ZODB_CONNECTION_KEY = 'zodb.connection'

class ZopeWSGI(object):
    def __init__(self, confvars):
        config = Configuration(confvars)
        self.root_name = config.paster['root_name']
        self.zodb_key = config.paster['zodb_connection']
        self.publication = MinimalisticPublisher(self.root_name)

    def setup(self, request, environ):
        """Should be in subscriber?"""
        request.setPublication(self.publication)

    def setup_zodb(self, request, environ):
        """Must be in "plugin" or subscriber"""
        conn = environ[self.zodb_key]
        root = conn.root()
        rootsite = root.get(self.root_name, None)
        if rootsite is None:
            raise RuntimeError("Can't found %s in ZODB" % self.roon_name)
        #hack to pass connection obtained from repoze.zodbconn
        request.annotations[ZODB_ANNOTATION_KEY] = rootsite


    def __call__(self, environ, start_response):
        request = self.request(environ)
        self.setup(request, environ)
        self.setup_zodb(request, environ)

        # Let's support post-mortem debugging
        handle_errors = environ.get('wsgi.handleErrors', True)

        self.publication.publish(request)
        response = request.response

        # Start the WSGI server response
        start_response(response.getStatusString(), response.getHeaders())

        # Return the result body iterable.
        return response.consumeBodyIter()

    def request(self, environ):
        method = environ.get('REQUEST_METHOD', 'GET').upper()
        if method in browser_methods:
            request_factory = BrowserRequest
        else:
            request_factory = HTTPRequest
        req =  request_factory(environ['wsgi.input'], environ)
        setDefaultSkin(req)
        return req

def make_wsgi_app(global_conf, **local_conf):
    global_conf.update(local_conf)
    return ZopeWSGI(global_conf)
