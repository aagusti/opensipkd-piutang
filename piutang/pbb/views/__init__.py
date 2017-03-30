from datetime import datetime
from ...views.base_views import BaseView
from ...pbb.tools import FixKantor
from ...tools import get_settings
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    )

class PbbView(BaseView):
    def __init__(self, request):
        super(PbbView, self).__init__(request)
        self.kd_kantor = 'kd_kantor' in self.ses and self.ses['kd_kantor'] or '01'
        self.kd_kanwil = 'kd_kanwil' in self.ses and self.ses['kd_kanwil'] or '01'
        self.ses['kd_kantor'] = self.kd_kantor
        self.ses['kd_kanwil'] = self.kd_kanwil
        settings = get_settings()
        self.simral_url_gw = 'simral.url_gw' in settings and settings['simral.url_gw'] or\
                        "http://192.168.56.2:6543/simral/ws"        
        self.verifikasi_date = 'verifikasi_date' in self.ses and self.ses['verifikasi_date'] or '-1'
        self.verifikasi_date = 'verifikasi_date' in self.params and self.params['verifikasi_date'] or self.verifikasi_date
        self.ses['verifikasi_date'] = self.verifikasi_date
        self.verifikasi_bphtb_date = 'verifikasi_bphtb_date' in self.ses and self.ses['verifikasi_bphtb_date'] or '-1'
        self.verifikasi_bphtb_date = 'verifikasi_bphtb_date' in self.params and self.params['verifikasi_bphtb_date'] or self.verifikasi_bphtb_date
        self.ses['verifikasi_bphtb_date'] = self.verifikasi_bphtb_date
        self.bphtb_posted = 'bphtb_posted' in self.ses and self.ses['bphtb_posted'] or '-1'
        self.bphtb_posted = 'bphtb_posted' in self.params and self.params['bphtb_posted'] or self.bphtb_posted
        self.ses['bphtb_posted'] = self.bphtb_posted
        self.jns_mutasi = 'jns_mutasi' in self.ses and self.ses['jns_mutasi'] or '-1'
        self.jns_mutasi = 'jns_mutasi' in self.params and self.params['jns_mutasi'] or self.jns_mutasi
        self.ses['jns_mutasi'] = self.jns_mutasi
            
########
# Home #
########
class HomeView(PbbView):
    def __init__(self, request):
        super(HomeView, self).__init__(request)

    @view_config(route_name='F100000', renderer='templates/home.pt',
                 permission='')
    def view_home(self):
        return dict(project='pbb')

            