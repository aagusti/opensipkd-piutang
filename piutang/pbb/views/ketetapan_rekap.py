import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import not_, func, between
from sqlalchemy import case
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
import colander
from deform import (Form, widget, ValidationFailure, )
from ..models import pbbDBSession
from ..models.tap import SpptAkrual, SpptAkrual
from ...tools import dmy, ymd_to_date, ymd
from ..views import PbbView
from ...views.common import ColumnDT, DataTables
import re
import json
import requests
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)
 
SESS_ADD_FAILED  = 'Tambah Ketetapan gagal'
SESS_EDIT_FAILED = 'Edit Ketetapan gagal'

def deferred_jenis_id(node, kw):
    values = kw.get('jenis_id', [])
    return widget.SelectWidget(values=values)

def deferred_sumber_id(node, kw):
    values = kw.get('sumber_id', [])
    return widget.SelectWidget(values=values)

class KetetapanRekapView(PbbView):
    def _init__(self,request):
        super(KetetapanRekapView, self).__init__(request)
        
    @view_config(route_name="pbb-ketetapan-rekap", renderer="templates/ketetapan_rekap/list.pt",
                 permission="pbb-ketetapan-rekap")
    def view_list(self):
        return dict(project=self.project)

    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-ketetapan-rekap-act', renderer='json',
                 permission='pbb-ketetapan-rekap-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict

        if url_dict['id']=='grid':
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['id']=='grid':
                # defining columns
                #func.case(,SpptAkrual.pbb_yg_harus_dibayar_sppt,0)
                
                pxpr = func.sum(func.case([(SpptAkrual.pbb_yg_harus_dibayar_sppt>0, 
                             SpptAkrual.pbb_yg_harus_dibayar_sppt),],
                           else_ = 0))
                mxpr = func.sum(func.case([(SpptAkrual.pbb_yg_harus_dibayar_sppt>0, 
                             0),],
                           else_ = SpptAkrual.pbb_yg_harus_dibayar_sppt))
                columns = [
                    ColumnDT(SpptAkrual.thn_pajak_sppt, mData='id'),
                    ColumnDT(SpptAkrual.thn_pajak_sppt, mData='tahun'),
                    ColumnDT(func.sum(case([(SpptAkrual.pbb_yg_harus_dibayar_sppt>0, 
                                SpptAkrual.pbb_yg_harus_dibayar_sppt)],
                            else_ = 0)), mData='kenaikan', global_search=False),
                    ColumnDT(func.sum(case([(SpptAkrual.pbb_yg_harus_dibayar_sppt>0,
                                0)],
                            else_ = SpptAkrual.pbb_yg_harus_dibayar_sppt)), mData='penurunan', global_search=False),
                    ColumnDT(func.sum(SpptAkrual.pbb_yg_harus_dibayar_sppt), mData='jumlah', global_search=False),
                    ColumnDT(SpptAkrual.posted, mData='posted'),
                ]
                query = pbbDBSession.query().select_from(SpptAkrual).\
                          group_by(SpptAkrual.thn_pajak_sppt,
                              SpptAkrual.posted).\
                          filter(func.to_char(SpptAkrual.create_date,'YYYY-MM-DD').between(ymd(self.dt_awal), ymd(self.dt_akhir))).\
                          filter(SpptAkrual.posted==self.posted)
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()
                
    ###########
    # Posting #
    ###########
    @view_config(route_name='pbb-ketetapan-rekap-post', renderer='json',
                 permission='pbb-ketetapan-rekap-post')
    def view_posting(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        n_id_not_found = n_row_zero = n_posted = n_id = 0
        now = datetime.now()
        n_id = n_id_not_found = n_posted = 0
                
        if req.POST:
            controls = dict(req.POST.items())
            #GENERATOR rekap ketetapan
            #create_date disimpan sebagai datetime
            #untuk grouping di convert dulu menjadi YYYY-MM-DD
            adate = func.to_char(SpptAkrual.create_date,'YYYY-MM-DD') 
            if url_dict['id']=='gen': 
                query = pbbDBSession.query(
                            adate.label('tanggal'),
                            func.sum(SpptAkrual.pbb_yg_harus_dibayar_sppt).label('pokok')).\
                        filter(adate.between(ymd(self.dt_awal), ymd(self.dt_akhir))).\
                        filter(SpptAkrual.posted==0).\
                        group_by(adate)
                
                r = query.first()
                if not r:
                    return dict(success = False,
                                msg     = 'Tidak ada data yang di proses')
                    
                headers = r.keys()
                for row in query.all():
                    row_dicted = dict(zip(row.keys(), row))
                    row_dicted['uraian'] = "Penetapan Tanggal {tanggal}".\
                                           format(tanggal = dmy(ymd_to_date(row.tanggal)))
                    row_dicted['kode'] = "03-{tanggal}".\
                                         format(tanggal = row.tanggal)
                    row_dicted['posted'] = 0
                    row_dicted['tanggal'] = ymd_to_date(row.tanggal)
                    spptRekap = SpptAkrual()
                    spptRekap.from_dict(row_dicted)
                    pbbDBSession.add(spptRekap)
                    pbbDBSession.flush()
                    
                pbbDBSession.query(SpptAkrual).\
                             filter(SpptAkrual.posted == 0,
                                    adate.between(ymd(self.dt_awal), ymd(self.dt_akhir))).\
                             update({SpptAkrual.posted: 2}, synchronize_session=False)
                return dict(success = True,
                            msg     = 'Proses Berhasil')
                                
            elif url_dict['id']=='del': #Hapus data rekap
                for id in controls['id'].split(","):
                    q = query_id(id)
                    row    = q.first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if row.posted:
                        n_posted = n_posted + 1
                        continue
                        
                    n_id = n_id + 1
                    row_dicted = row.to_dict()
                    
                    pbbDBSession.query(SpptAkrual).\
                                 filter(SpptAkrual.create_date.between(row.tanggal,row.tanggal+timedelta(days=1)),
                                        SpptAkrual.posted == 2,).\
                                 update({SpptAkrual.posted:0}, synchronize_session=False)
                    q.delete()
                    pbbDBSession.flush()
                    
                if n_id_not_found > 0 or n_row_zero > 0 or n_posted>0:
                    return dict(success = False,
                                msg     = "Data tidak bisa dihapus %s records" % (n_id_not_found+n_row_zero+n_posted))
                
                return dict(success = True,
                            msg     = "Sukses Hapus %s record(s)" % n_id)
            #POSTING Data                
            elif url_dict['id']=='post': 
                controls = dict(req.POST.items())
                for id in controls['id'].split(","):
                    row    = query_id(id).first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if not row.pokok:
                        n_row_zero = n_row_zero + 1
                        continue

                    if url_dict['id']=='false' and row.posted:
                        n_posted = n_posted + 1
                        continue

                    if url_dict['id']=='true' and not row.posted:
                        n_posted = n_posted + 1
                        continue

                    n_id = n_id + 1
                    id = row.kode
                    ret = dict( id_trx            = id,
                                no_trx            = id,
                                tgl_pembukuan     = ymd(row.tanggal),
                                no_kohir          = id,
                                jns_trx           = "PenetapanSKRD",
                                no_bukti_trx      = id,
                                tgl_bukti_trx     = ymd(row.tanggal), 
                                tgl_awal_periode  = ymd(row.tanggal), #TO DO: Periode PBB?
                                tgl_akhir_periode = ymd(row.tanggal),
                                uraian_trx        = 'Rekap Ketetapan tgl %s' % dmy(row.tanggal),
                                nm_penyetor       = 'Rekap Ketetapan tgl %s' % dmy(row.tanggal),
                                alamat_penyetor   = '-', 
                                npwp_penyetor     = '-', 
                                kd_rekening       =  "4111001", #row.kd_rekening,
                                nm_rekening       =  "Pendapatan PBB", #row.nm_rekening,
                                jumlah            = row.pokok,
                                kd_denda          = "4140710", #row.kd_denda,
                                nm_denda          = "Pendapatan Denda PBB", #row.nm_denda,
                                jumlah_denda      = 0,
                                source            = 'PBB',
                                source_id         = id,
                                )
                    ret_json = json.dumps([ret])
                    url = "%s/ketetapan/%s/api" % (self.simral_url_gw, datetime.now().strftime('%Y%m%d'))
  
                    if self.posted:
                        result = requests.delete(url, data=ret_json)
                        if result.status_code==200:
                            row.posted = 0
                        else:
                            return dict(success = False,
                                        msg= "Error Unposting ID %s" %id) 
                    else:
                        result = requests.put(url, data=ret_json)
                        if result.status_code==200:
                            row.posted = 1
                        else:
                            return dict(success = False,
                                        msg= "Error Posting ID %s" %id) 
                        
                    pbbDBSession.add(row)
                    pbbDBSession.flush()
                    
                if n_id_not_found > 0 or n_row_zero > 0 or n_posted>0:
                    return dict(success = False,
                                msg     = "Data tidak bisa diposting %s records" % (n_id_not_found+n_row_zero+n_posted))
                
                return dict(success = True,
                            msg     = "Sukses %s %s record(s)" % (self.posted and 'Unposting' or 'Posting', n_id))
                        
        return dict(success = False,
                    msg     = 'Terjadi kesalahan proses')

    ##########
    # CSV #
    ##########
    @view_config(route_name='pbb-ketetapan-rekap-rpt',
                 permission='pbb-ketetapan-rekap-rpt')
    def view_csv(self):
        url_dict = self.req.matchdict
        query = pbbDBSession.query(SpptAkrual.id,
                        func.to_char(SpptAkrual.tanggal,'DD-MM-YYYY').label('tanggal'),
                        SpptAkrual.kode,
                        SpptAkrual.uraian, 
                        SpptAkrual.pokok,
                        SpptAkrual.posted,).\
                filter(SpptAkrual.tanggal.between(self.dt_awal, self.dt_akhir)).\
                filter(SpptAkrual.posted==self.posted)

        if url_dict['rpt']=='csv' :
            filename = 'ketetapan_rekap.csv'
            return csv_response(self.req, csv_rows(query), filename)

        if url_dict['rpt']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'static')
            print "XXXXXXXXXXXXXXXXXXX", os.path

            logo = os.path.abspath("pajak/static/img/logo.png")
            line = os.path.abspath("pajak/static/img/line.png")

            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/pbb_ketetapan_rekap.row.rml')
            
            rows=[]
            for r in query.all():
                s = rml_row.format(id=r.id, tanggal=r.tanggal, kode=r.kode,   
                                   uraian=r.uraian, pokok=r.pokok, posted=r.posted)
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/pbb_ketetapan_rekap.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = logo,
                                line = line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)

def route_list(request):
    return HTTPFound(location=request.route_url('pbb-ketetapan-rekap'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

########
# Edit #
########
def query_id(id):
    return pbbDBSession.query(SpptAkrual).\
           filter(SpptAkrual.id==id)

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)


