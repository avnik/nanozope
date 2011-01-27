from zope.interface import implements
from zope.component import getUtility, getGlobalSiteManager
from zope.component import queryMultiAdapter
from zope.component.interfaces import ISite
from zope.publisher.interfaces import IPublication, IPublishTraverse, IRequest
from zope.publisher.interfaces.http import IHTTPException
from zope.publisher.interfaces.http import MethodNotAllowed
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.publish import mapply
from zope.security.management import newInteraction, endInteraction
from zope.security.checker import ProxyFactory
from zope.event import notify
from zope.traversing.publicationtraverse import PublicationTraverser
from zope.publisher.interfaces import EndRequestEvent
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.authentication.interfaces import IFallbackUnauthenticatedPrincipal
from zope.authentication.interfaces import IAuthentication
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import BeforeTraverseEvent
from interfaces import AfterCallEvent

# Name choosed to be compatible with standard zopepublisher
ZODB_ANNOTATION_KEY = "ZODB.interfaces.IConnection"

class MinimalisticPublisher(object):
    implements(IPublication)
    def __init__(self, root_name):
        self.root_name = root_name
        self.traverser = PublicationTraverser()

    def getApplication(self, request):
        #Yep, we think we know implementation details here
        #but whole package is big optimisation hack
        return request.annotations[ZODB_ANNOTATION_KEY]

    def proxy(self, ob):
        """Security-proxy an object

        Subclasses may override this to use a different proxy (or
        checker) implementation or to not proxy at all.
        """
        return ProxyFactory(ob)

    def getDefaultTraversal(self, request, ob):
        if IBrowserPublisher.providedBy(ob):
            # ob is already proxied, so the result of calling a method will be
            return ob.browserDefault(request)
        else:
            adapter = queryMultiAdapter((ob, request), IBrowserPublisher)
            if adapter is not None:
                ob, path = adapter.browserDefault(request)
                ob = self.proxy(ob)
                return ob, path
            else:
                # ob is already proxied
                return ob, None


    def publish(self, request):
        request.processInputs()
        self.beforeTraversal(request)

        obj = self.getApplication(request)
        obj = request.traverse(obj)
        self.afterTraversal(request, obj)
        
        result = self.callObject(request, obj)
        
        response = request.response
        if result is not response:
           response.setResult(result)

        self.afterCall(request, obj)


    def callObject(self, request, ob):
        # Exception handling, dont try to call request.method
        orig = ob
        #if not IHTTPException.providedBy(ob):
        #    ob = getattr(ob, request.method, None)
        #    if ob is None:
        #        raise MethodNotAllowed(orig, request)
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request, obj):
        if request.method == 'HEAD':
           request.response.setResult('')

        notify(AfterCallEvent(request, obj))
        endInteraction()

    def traverseName(self, request, obj, name):
        return self.traverser.traverseName(request, obj, name)

    def beforeTraversal(self, request):
        self.authenticate(request, getGlobalSiteManager(), fallback=True)
        newInteraction(request)

    def callTraversalHooks(self, request, ob):
        # Call __before_publishing_traverse__ hooks
        notify(BeforeTraverseEvent(ob, request))
        # This is also a handy place to try and authenticate.
        self._maybePlacefullyAuthenticate(request, ob)

    def afterTraversal(self, request, ob):
        self._maybePlacefullyAuthenticate(request, ob)

    def _maybePlacefullyAuthenticate(self, request, ob):
        if not IUnauthenticatedPrincipal.providedBy(request.principal):
            # We've already got an authenticated user. There's nothing to do.
            # Note that beforeTraversal guarentees that user is not None.
            return

        if not ISite.providedBy(ob):
            # We won't find an authentication utility here, so give up.
            return

        sm = removeSecurityProxy(ob).getSiteManager()
        self.authenticate(request, sm)

    def authenticate(self, request, sm, fallback=False):
        principal = None
        auth = sm.queryUtility(IAuthentication)
        if auth is not None:

            # Try to authenticate against the auth utility
            principal = auth.authenticate(request)
            if principal is None:
                principal = auth.unauthenticatedPrincipal()

        if principal is None:
            # nothing to do here
            if not fallback:
                return
            principal = getUtility(IFallbackUnauthenticatedPrincipal)

        request.setPrincipal(principal)
