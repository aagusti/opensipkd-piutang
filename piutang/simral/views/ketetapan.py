import os
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
from sqlalchemy import func, String    
from ..views import SimralView, ColumnDT, DataTables
from ..models import SimralKetetapan, DBSession
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)

class KetetapanView(SimralView):
    @view_config(route_name="simral-ketetapan", renderer="templates/ketetapan/list.pt",
                 permission="simral-ketetapan")
    def view(self):
        return dict(project=self.project)
        
    @view_config(route_name="simral-ketetapan-act", renderer="json",
                 permission="simral-ketetapan-act")
    def act(self):
        req = self.req
        ses = req.session
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = [
                ColumnDT(SimralKetetapan.id_trx, mData='id'),
                ColumnDT(SimralKetetapan.no_trx, mData='no_trx'),
                ColumnDT(func.to_char(SimralKetetapan.tgl_pembukuan,'DD-MM-YYYY'), mData='tgl_pembukuan'),
                ColumnDT(SimralKetetapan.jns_trx, mData='jns_trx'),
                ColumnDT(SimralKetetapan.no_bukti_trx, mData='no_bukti_trx'),
                ColumnDT(func.to_char(SimralKetetapan.tgl_bukti_trx,'DD-MM-YYYY'), mData='tgl_bukti_trx'),
                ColumnDT(SimralKetetapan.nm_penyetor, mData='nm_penyetor'),
                ColumnDT(SimralKetetapan.kd_rekening, mData='kd_rekening'),
                ColumnDT(SimralKetetapan.jumlah, mData='jumlah'),
                ColumnDT(SimralKetetapan.kd_denda, mData='kd_denda'),
                ColumnDT(SimralKetetapan.jumlah_denda, mData='denda'),
                ColumnDT(SimralKetetapan.source, mData='source'),
            ]
            query = DBSession.query().select_from(SimralKetetapan).\
                    filter(SimralKetetapan.tgl_pembukuan.between(self.dt_awal, self.dt_akhir))
                    
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()

        elif url_dict['act']=='csv' :
            filename = 'ketetapan.csv'
            query = query_rpt().\
                        filter(SimralKetetapan.tgl_pembukuan.between(self.dt_awal, self.dt_akhir))
            return csv_response(self.req, csv_rows(query), filename)
        elif url_dict['act']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/ketetapan.row.rml')
            query = query_rpt().\
                        filter(SimralKetetapan.tgl_pembukuan.between(self.dt_awal, self.dt_akhir))
            rows=[]
            for r in query.all():
                s = rml_row.format(
                        id_trx        = r.id_trx,
                        no_trx        = r.no_trx,
                        tgl_pembukuan = r.tgl_pembukuan,
                        jns_trx       = r.jns_trx,
                        no_bukti_trx  = r.no_bukti_trx,
                        tgl_bukti_trx = r.tgl_bukti_trx,
                        nm_penyetor   = r.nm_penyetor,
                        kd_rekening   = r.kd_rekening,
                        jumlah        = r.jumlah,
                        kd_denda      = r.kd_denda,
                        jumlah_denda  = r.jumlah_denda,
                        source        = r.source,
                )
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/ketetapan.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = self.logo,
                                line = self.line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)
            
def query_rpt():
    return DBSession.query(SimralKetetapan.id_trx, SimralKetetapan.no_trx, 
            func.to_char(SimralKetetapan.tgl_pembukuan,'DD-MM-YYYY').label('tgl_pembukuan'),
            SimralKetetapan.jns_trx, SimralKetetapan.no_bukti_trx, 
            func.to_char(SimralKetetapan.tgl_bukti_trx,'DD-MM-YYYY').label('tgl_bukti_trx'), 
            SimralKetetapan.nm_penyetor, SimralKetetapan.kd_rekening, SimralKetetapan.jumlah, 
            SimralKetetapan.kd_denda, SimralKetetapan.jumlah_denda, SimralKetetapan.source)
        
