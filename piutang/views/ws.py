import sys
import logging
import traceback
from StringIO import StringIO
from ..ws_tools import (
    auth_from_rpc,
    LIMIT,
    CODE_OK,
    CODE_NOT_FOUND,
    CODE_DATA_INVALID, 
    CODE_INVALID_LOGIN,
    CODE_NETWORK_ERROR,
    MSG_OK,
    MSG_DATA_INVALID,
    )
from pyramid_rpc.jsonrpc import jsonrpc_method
from pyramid.view import (view_config,)
from pyramid.renderers import render_to_response
from datetime import datetime
import re
#from ..models import pbbDBSession
#from ..models.tap import (
#    Sppt,
#    )
#from ..models.pendataan import DatObjekPajak
    
from ..tools import FixLength
from ..views.base_views import BaseView
log = logging.getLogger(__name__)

def show_error():
    f = StringIO()
    traceback.print_exc(file=f)
    log.error(f.getvalue())
    f.close()
    
class WsView(BaseView):
    def _init__(self,request):
        super(WsView, self).__init__(request)
        
    @view_config(route_name="ws")
    def view(self):
        #from ..tools import to_dict
        #print self.req.application_url
        vars = dict(project="WS")
        if 'ws' in self.req.params and self.req.params['ws']:
            return render_to_response("templates/ws-simral.pt",vars,request=self.req)
        return render_to_response("templates/ws.pt", vars, request=self.req)