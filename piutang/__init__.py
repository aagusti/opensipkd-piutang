import sys
import locale
from types import (
    StringType,
    UnicodeType,
    )
from urllib import (
    urlencode,
    quote,
    quote_plus,
    )    
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.events import subscriber
from pyramid.events import BeforeRender
from pyramid.interfaces import IRoutesMapper
from pyramid.httpexceptions import (
    default_exceptionresponse_view,
    HTTPFound,
    )
from pyramid.renderers import JSON 
import datetime
from sqlalchemy import engine_from_config
from security import (
    group_finder,
    get_user,
    )
from models import (
    DBSession,
    Base,
    init_model,
    Route
    )
from tools import (
    DefaultTimeZone,
    money,
    should_int,
    thousand,
    as_timezone,
    split,
    )



# http://stackoverflow.com/questions/9845669/pyramid-inverse-to-add-notfound-viewappend-slash-true    
class RemoveSlashNotFoundViewFactory(object):
    def __init__(self, notfound_view=None):
        if notfound_view is None:
            notfound_view = default_exceptionresponse_view
        self.notfound_view = notfound_view

    def __call__(self, context, request):
        if not isinstance(context, Exception):
            # backwards compat for an append_notslash_view registered via
            # config.set_notfound_view instead of as a proper exception view
            context = getattr(request, 'exception', None) or context
        path = request.path
        registry = request.registry
        mapper = registry.queryUtility(IRoutesMapper)
        if mapper is not None and path.endswith('/'):
            noslash_path = path.rstrip('/')
            for route in mapper.get_routes():
                if route.match(noslash_path) is not None:
                    qs = request.query_string
                    if qs:
                        noslash_path += '?' + qs
                    return HTTPFound(location=noslash_path)
        return self.notfound_view(context, request)
    
# https://groups.google.com/forum/#!topic/pylons-discuss/QIj4G82j04c
def has_permission_(request, perm_names):
    if type(perm_names) in [UnicodeType, StringType]:
        perm_names = [perm_names]
    for perm_name in perm_names:
        if request.has_permission(perm_name):
            return True

@subscriber(BeforeRender)
def add_global(event):
     event['has_permission'] = has_permission_
     event['urlencode'] = urlencode
     event['quote_plus'] = quote_plus
     event['quote'] = quote   
     event['money'] = money
     event['should_int'] = should_int  
     event['thousand'] = thousand
     event['as_timezone'] = as_timezone
     event['split'] = split

def get_title(request):
    route_name = request.matched_route.name
    return titles[route_name]

def get_company(request):
    from tools import get_settings
    settings = get_settings()
    company = 'company' in settings and settings['company'] or 'DEMO'
    return company.upper()

def get_departement(request):
    from tools import get_settings
    settings = get_settings()
    departement = 'departement' in settings and settings['departement'] or 'DIVISI DEMO'
    return departement

def get_address(request):
    from tools import get_settings
    settings = get_settings()
    address = 'address' in settings and settings['address'] or 'JATIASIH - BEKASI'
    return address
    
main_title = 'opensipkd-piutang'
titles = {}

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.', 
                pool_size=settings['pool_size'],
                max_overflow = settings['max_overflow'])
    #engine.pool_size = settings['pool_size']
    #engine.
    
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    init_model()

    if 'sipkd.url' in settings and settings['sipkd.url']:
        from sipkd.models import sipkdDBSession, sipkdBase
        engineSipkd = engine_from_config(settings, 'sipkd.')
        sipkdDBSession.configure(bind=engineSipkd, 
                pool_size=settings['pool_size'],
                max_overflow = settings['max_overflow'])
        sipkdBase.metadata.bind = engineSipkd
    
    #added 09-08-2016
    if 'pdl.url' in settings and settings['pdl.url']:
        from pdl.models import pdlDBSession, pdlBase
        enginePdl = engine_from_config(settings, 'pdl.', 
                pool_size=settings['pool_size'],
                max_overflow = settings['max_overflow'])
    
        pdlDBSession.configure(bind=enginePdl)
        pdlBase.metadata.bind = enginePdl
        pdl_schema = 'schema.pdl' in settings and settings['schema.pdl'] or 'public'

    if 'pbb.url' in settings and settings['pbb.url']:
        from pbb.models import pbbDBSession, pbbBase, pbb_schema
        enginePbb = engine_from_config(settings, 'pbb.', 
                pool_size=settings['pool_size'],
                max_overflow = settings['max_overflow'])
        pbbDBSession.configure(bind=enginePbb)
        pbbBase.metadata.bind = enginePbb
        pbb_schema = 'schema.pbb' in settings and settings['schema.pbb'] or 'pbb'
        
    if 'bphtb.url' in settings and settings['bphtb.url']:
        from bphtb.models import bphtbDBSession, bphtbBase, bphtb_schema
        engineBphtb = engine_from_config(settings, 'bphtb.', 
                pool_size=settings['pool_size'],
                max_overflow = settings['max_overflow'])
        bphtbDBSession.configure(bind=engineBphtb)
        bphtbBase.metadata.bind = engineBphtb
        bphtb_schema = 'schema.bphtb' in settings and settings['schema.bphtb'] or 'bphtb'
    if 'esppt.url' in settings and settings['esppt.url']:
        from esppt.models import EsDBSession, EsBase, es_schema
        engineEsppt = engine_from_config(settings, 'esppt.', 
                pool_size=settings['pool_size'],
                max_overflow = settings['max_overflow'])
        EsDBSession.configure(bind=engineEsppt)
        EsBase.metadata.bind = engineEsppt
        es_schema = 'schema.esppt' in settings and settings['schema.esppt'] or 'esppt'
        
    if 'im.url' in settings and settings['im.url']:
        from im.models import ImDBSession, ImBase, im_schema
        engineIm = engine_from_config(settings, 'im.', 
                pool_size=settings['pool_size'],
                max_overflow = settings['max_overflow'])
        ImDBSession.configure(bind=engineIm)
        ImBase.metadata.bind = engineIm
        im_schema = 'schema.im' in settings and settings['schema.im'] or 'im'

    if 'pospbb.url' in settings and settings['pospbb.url']:
        from pbb_tools.models import PosPbbDBSession, PosPbbBase, pospbb_schema
        enginePosPbb = engine_from_config(settings, 'pospbb.', 
                pool_size=settings['pool_size'],
                max_overflow = settings['max_overflow'])
        PosPbbDBSession.configure(bind=enginePosPbb)
        PosPbbBase.metadata.bind = enginePosPbb
        im_schema = 'schema.pospbb' in settings and settings['schema.pospbb'] or 'pbb'
        
    session_factory = session_factory_from_settings(settings)
    #session_factory.pool_size=settings['pool_size']
    #session_factory.max_overflow = settings['max_overflow']
    
    #if 'localization' not in settings:
    #    settings['localization'] = 'id_ID.UTF-8'
    #locale.setlocale(locale.LC_ALL, settings['localization'])

    #handling bug di locale.setlocale
    localID = locale.normalize('id');
    if 'localization' not in settings:
        settings['localization'] = localID
    if settings['localization'] != localID:
        settings['localization'] = localID
    #locale.setlocale(locale.LC_ALL, settings['localization'])
    #bug : unsupported locale setting 
    locale.setlocale(locale.LC_ALL, '')
    
    if 'timezone' not in settings:
        settings['timezone'] = DefaultTimeZone
    config = Configurator(settings=settings,
                          root_factory='piutang.models.RootFactory',
                          session_factory=session_factory)
    config.include('pyramid_beaker')                          
    config.include('pyramid_chameleon')

    authn_policy = AuthTktAuthenticationPolicy('sosecret',
                    callback=group_finder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()                          
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(get_user, 'user', reify=True)
    config.add_request_method(get_title, 'title', reify=True)
    config.add_request_method(get_company, 'company', reify=True)
    config.add_request_method(get_departement, 'departement', reify=True)
    config.add_request_method(get_address, 'address', reify=True)
    config.add_notfound_view(RemoveSlashNotFoundViewFactory())        
                          
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform_static', 'deform:static')
    config.add_static_view('files', settings['static_files'])    
    
    config.add_renderer('csv', '.tools.CSVRenderer')
    
    routes = DBSession.query(Route.kode, Route.path, Route.nama).all()
    for route in routes:
        #if route.factory and route.factory != 'None': 
        #    config.add_route(route.kode, route.path) #(route.factory).encode("utf8"))
        #else:
        config.add_route(route.kode, route.path)
            
        if route.nama:
            titles[route.kode] = route.nama

    ############################################################################
    config.include('pyramid_rpc.jsonrpc') # JSON RPC
    json_renderer = JSON()
    json_renderer.add_adapter(datetime.datetime, lambda v, request: v.isoformat())
    json_renderer.add_adapter(datetime.date, lambda v, request: v.isoformat())
    config.add_renderer('myjson', json_renderer)
    config.add_jsonrpc_endpoint('ws_pbb', '/pbb/ws/api', default_renderer="myjson")
    config.add_jsonrpc_endpoint('ws_keuangan', '/ws/keuangan', default_renderer="myjson")
    config.add_jsonrpc_endpoint('ws_simral', '/simral/ws/api', default_renderer="myjson")
    config.add_jsonrpc_endpoint('ws_user', '/ws/user', default_renderer="myjson")
    
    ############################################################################
 
    config.scan()
    app = config.make_wsgi_app()
    from paste.translogger import TransLogger
    app = TransLogger(app, setup_console_handler=False)    
    return app
