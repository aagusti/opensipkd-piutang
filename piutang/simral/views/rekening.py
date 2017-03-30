import os
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
from ..views import SimralView, ColumnDT, DataTables
#import json
from ..models import SimralRekening, DBSession
from ..tools import dmy, dmy_to_date
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)
from ...ws_tools import WsClientApi

SESS_ADD_FAILED = 'STS gagal tambah'
SESS_EDIT_FAILED = 'STS gagal edit'

class RekeningView(SimralView):
    @view_config(route_name="simral-rekening", renderer="templates/rekening/list.pt",
                 permission="simral-rekening")
    def view(self):
        return dict(project=self.project)
        
    @view_config(route_name="simral-rekening-act", renderer = "json",
                 permission="simral-rekening-act")
    def act(self):
        req = self.req
        ses = req.session
        params = req.params
        url_dict = req.matchdict
        def  query_rpt():
            return DBSession.query(SimralRekening.kd_rek_rincian_obj.label('kode'), 
                                    SimralRekening.nm_rek_rincian_obj.label('uraian'))

        if url_dict['act']=='grid':
            columns = [
                ColumnDT(SimralRekening.kd_rek_rincian_obj, mData='kode'),
                ColumnDT(SimralRekening.nm_rek_rincian_obj, mData='uraian'),
            ]
            query = DBSession.query().select_from(SimralRekening)
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()

        elif url_dict['act']=='import' :
            data = WsClientApi()
            try:
                url = '/sikd/getKdRekening'
                rows = data.request(url)
            except  Exception, e:
                from ...tools import get_settings
                settings = get_settings()
                url =  settings['simral.api']+url
                req.session.flash(url +"# "+str(e),'error')
                return route_list(req)
            for r in rows:
                row = DBSession.query(SimralRekening).\
                    filter_by(kd_rek_rincian_obj=row.kd_rek_rincian_obj).first()
                if not row:
                    row = SimralRekening()
                row.from_dict(row)
                DBSession.add(row)
                DBSession.flush()
            return route_list(req)

        elif url_dict['act']=='csv':
            filename = 'rekening.csv'
            return csv_response(self.req, csv_rows(query_rpt()), filename)
                            
        elif url_dict['act']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'static')
            logo = os.path.abspath("pajak/static/img/logo.png")
            line = os.path.abspath("pajak/static/img/line.png")

            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/rekening.row.rml')
            rows=[]
            for r in query_rpt().all():
                s = rml_row.format(kode=r.kode, uraian=r.uraian)
                rows.append(s)
            pdf, filename = open_rml_pdf(path+'/rekening.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = logo,
                                line = line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)

def route_list(request):
    return HTTPFound(location=request.route_url('simral-rekening'))
