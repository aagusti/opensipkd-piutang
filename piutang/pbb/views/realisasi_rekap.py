import os
import re
import json
import requests
import colander

from datetime import datetime, timedelta
from sqlalchemy import not_, func, between, or_
from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
from deform import (Form, widget, ValidationFailure, )

from ..models import pbbDBSession
from ..models.tap import PembayaranSppt
from ..tools import FixBank
from ...tools import dmy, ymd_to_date, ymd
from ..views import PbbView
from ...views.common import ColumnDT, DataTables
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)
 
SESS_ADD_FAILED  = 'Tambah Realisasi rekap gagal'
SESS_EDIT_FAILED = 'Edit Realisasi rekap  gagal'

class RealisasiRekapView(PbbView):
    def _init__(self,request):
        super(RealisasiRekap, self).__init__(request)
        
    @view_config(route_name="pbb-realisasi-rekap", renderer="templates/realisasi_rekap/list.pt",
                 permission="pbb-realisasi-rekap")
    def view_list(self):
        req = self.req
        ses = req.session
        params = req.params
        now = datetime.now()
        return dict(project=self.project)

    ##########
    # Action #
    ##########
    @view_config(route_name='pbb-realisasi-rekap-act', renderer='json',
                 permission='pbb-realisasi-rekap-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        awal  = self.dt_awal
        akhir = self.dt_akhir
        if url_dict['id']=='grid':
            #pk_id = 'id' in params and params['id'] and int(params['id']) or 0
            if url_dict['id']=='grid':
                # defining columns
                columns = [
                    ColumnDT(PembayaranSppt.thn_pajak_sppt, mData='id'),
                    ColumnDT(PembayaranSppt.thn_pajak_sppt, mData='tahun'),
                    ColumnDT(func.sum(PembayaranSppt.denda_sppt), mData='denda', global_search=False),
                    ColumnDT(func.sum(PembayaranSppt.jml_sppt_yg_dibayar), mData='bayar', global_search=False),
                    ColumnDT(func.sum(PembayaranSppt.jml_sppt_yg_dibayar-PembayaranSppt.denda_sppt), mData='pokok', global_search=False),
                ]
                query = pbbDBSession.query().select_from(PembayaranSppt).\
                                     filter(PembayaranSppt.tgl_pembayaran_sppt.between(awal,akhir)).\
                                     group_by(PembayaranSppt.thn_pajak_sppt)
                rowTable = DataTables(req.GET, query, columns)
                return rowTable.output_result()
                
    ###########
    # Posting #
    ###########
    @view_config(route_name='pbb-realisasi-rekap-post', renderer='json',
                 permission='pbb-realisasi-rekap-post')
    def view_post(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict
        n_id_not_found = n_row_zero = n_posted = n_id = 0
        adate = func.to_char(PembayaranSppt.tgl_rekam_byr_sppt,'YYYY-MM-DD')
        if req.POST:
            controls = dict(req.POST.items())
            awal  = self.dt_awal
            akhir = self.dt_akhir
            if url_dict['id']=='gen': #GENERATOR rekap penerimaan
                # Data diambil dari tanggal rekam bayar karena yang aktual adalah tgl tersebut
                rows = pbbDBSession.query(
                                PembayaranSppt.tgl_pembayaran_sppt.label('tanggal'),
                                adate.label('tgl_buku'),
                                PembayaranSppt.thn_pajak_sppt.label('tahun'),
                                PembayaranSppt.kd_kanwil,
                                PembayaranSppt.kd_kantor,
                                PembayaranSppt.kd_tp,
                                func.sum(PembayaranSppt.denda_sppt).label('denda'),
                                func.sum(PembayaranSppt.jml_sppt_yg_dibayar).label('bayar'),).\
                            filter(
                                adate.between(ymd(awal),ymd(akhir)),
                                PembayaranSppt.posted==0).\
                            group_by(
                                PembayaranSppt.tgl_pembayaran_sppt,
                                adate, PembayaranSppt.thn_pajak_sppt, 
                                PembayaranSppt.kd_kanwil,
                                PembayaranSppt.kd_kantor, 
                                PembayaranSppt.kd_tp,)
                r = rows.first()
                if not r:
                    return dict(success = False,
                                msg     = 'Tidak ada data yang di proses')
                    
                headers = r.keys()
                bank = FixBank("")
                for row in rows.all():
                    row_dicted = dict(zip(row.keys(), row))
                    bank.from_dict(row_dicted)
                    row_dicted['uraian'] = "Pembukuan tgl {tgl_buku} Atas Tgl {tanggal} Tahun {tahun} Bank {bank}".\
                                           format(tanggal = dmy(row.tanggal),
                                                  tgl_buku = dmy(ymd_to_date(row.tgl_buku)),
                                                  tahun = row.tahun,
                                                  bank = bank.get_raw())
                    row_dicted['kode'] = "03-{tgl_buku}-{tanggal}-{tahun}-{bank}".\
                                         format(
                                            tgl_buku = re.sub("\D","",row.tgl_buku)[-6:],
                                            tanggal = re.sub("\D","",ymd(row.tanggal))[-6:],
                                                
                                                bank = bank.get_raw(),
                                                tahun = row.tahun)
                    row_dicted['posted'] = 0
                    row_dicted['tgl_buku'] = ymd_to_date(row.tgl_buku)
                    
                    pembayaranRekap = PembayaranRekap()
                    pembayaranRekap.from_dict(row_dicted)
                    pbbDBSession.add(pembayaranRekap)
                    pbbDBSession.flush()

                pbbDBSession.query(PembayaranSppt).\
                                filter(PembayaranSppt.posted == 0,
                                        adate.between(ymd(awal),ymd(akhir))).\
                                update({PembayaranSppt.posted: 2}, synchronize_session=False)
                return dict(success = True,
                                msg     = 'Proses Berhasil')
                                
            elif url_dict['id']=='del': #Hapus data rekap
                controls = dict(req.POST.items())
                n_id_not_found = n_posted = 0
                #unposting data di Pembayaran SPPT
                for id in controls['id'].split(","):
                    q = query_id(id)
                    for r in q.all():
                        print 'ID=', r.id
                        
                    row    = q.first()
                    if not row:
                        n_id_not_found = n_id_not_found + 1
                        continue

                    if row.posted:
                        n_posted = n_posted + 1
                        continue
                    n_id = n_id + 1
                    row_dicted = row.to_dict()
                    start_pos = -6
                    bank = FixBank(row_dicted['kode'][start_pos:])
                    pbbDBSession.query(PembayaranSppt).\
                                 filter(PembayaranSppt.tgl_pembayaran_sppt == row.tanggal,
                                        PembayaranSppt.posted == 2,
                                        PembayaranSppt.kd_kanwil==bank.kd_kanwil,
                                        PembayaranSppt.kd_kantor==bank.kd_kantor,
                                        PembayaranSppt.kd_tp==bank.kd_tp,
                                        adate == ymd(row.tgl_buku)).\
                                 update({PembayaranSppt.posted:0}, synchronize_session=False)
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

                    if not row.bayar:
                        n_row_zero = n_row_zero + 1
                        continue

                    if not self.posted and row.posted:
                        n_posted = n_posted + 1
                        continue

                    if self.posted and not row.posted:
                        n_posted = n_posted + 1
                        continue

                    n_id = n_id + 1

                    #id_inv = row.id
                    id_inv = row.kode
                    pendapatan_thn_lalu = row.tahun < row.tgl_buku.year and 2 or 0 #0 tahun ini 1 tahun lalu 2 tahun lalu piutang
                    cara_pembayaran = 1 #0 kasda 1 Bendahara Penerimaan
                    ret = dict( id_trx            = id_inv,
                                no_trx            = row.kode,
                                tgl_pembukuan     = ymd(row.tgl_buku),
                                no_kohir          = row.kode,
                                jns_trx           = "PenetapanSKRD",
                                no_bukti_trx      = id_inv,
                                tgl_bukti_trx     = ymd(row.tanggal),
                                uraian_trx        = row.uraian,
                                tgl_awal_periode  = ymd(row.tanggal),
                                tgl_akhir_periode = ymd(row.tanggal),
                                #no_dpa            = row.no_dpa,
                                #no_sub_kegiatan   = row.no_sub_kegiatan,
                                nm_penyetor       = row.uraian[-11:],
                                alamat_penyetor   = '-', #row.wp_alamat,
                                npwp_penyetor     = '-', #row.wp_npwp,
                                
                                cara_pembayaran        = cara_pembayaran, #0 kasda 1 bendahara
                                pendapatan_thn_lalu    = pendapatan_thn_lalu,
                                pendapatan_dtrm_dimuka = 0, #row.pendapatan_dtrm_dimuka,
                                #trx_pengakuan_pdpt_id  = id_inv,
                                kd_rekening       =  "4111001", #row.kd_rekening,
                                nm_rekening       =  "Pendapatan PBB", #row.nm_rekening,
                                jumlah            = row.bayar-row.denda,
                                kd_denda          = "4140710", #row.kd_denda,
                                nm_denda          = "Pendapatan Denda PBB", #row.nm_denda,
                                jumlah_denda      = row.denda,
                                source            = 'PBB',
                                source_id         = row.kode
                                )
                    ret_json = json.dumps([ret])
                    url = "%s/realisasi/%s/api" % (self.simral_url_gw, datetime.now().strftime('%Y%m%d'))
                    if self.posted:
                        result = requests.delete(url, data=ret_json)
                        if result.status_code==200:
                            row.posted = 0 
                    else:
                        result = requests.put(url, data=ret_json)
                        if result.status_code==200:
                            row.posted = 1     
                    
                    if result.status_code!=200:
                        print result.text
                        return dict(success = False,
                                msg     = "Data tidak bisa diposting/unposting ID# %s" % (row.kode))
                            
                    pbbDBSession.add(row)
                    pbbDBSession.flush()
                    
                if n_id_not_found > 0 or n_row_zero > 0 or n_posted>0:
                    return dict(success = False,
                                msg     = "Data tidak bisa diposting %s records" % (n_id_not_found+n_row_zero+n_posted))
                
                return dict(success = True,
                            msg     = "Sukses Posting %s record(s)" % n_id)

    ##########
    # CSV #
    ##########
    @view_config(route_name='pbb-realisasi-rekap-rpt', 
                 permission='pbb-realisasi-rekap-rpt')
    def view_csv(self):
        url_dict = self.req.matchdict
        query = pbbDBSession.query(PembayaranRekap.tanggal,
                               PembayaranRekap.kode,
                               PembayaranRekap.uraian,
                               (PembayaranRekap.bayar - PembayaranRekap.denda).label("pokok"),
                               PembayaranRekap.denda,
                               PembayaranRekap.bayar).\
                      filter(PembayaranRekap.tanggal.between(self.dt_awal,self.dt_akhir),
                             PembayaranRekap.posted == self.posted)
        
        if url_dict['rpt']=='csv' :
            filename = 'pbb-realisasi-rekap.csv'
            return csv_response(self.req, csv_rows(query), filename)
                               
        if url_dict['rpt']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'static')

            logo = os.path.abspath("pajak/static/img/logo.png")
            line = os.path.abspath("pajak/static/img/line.png")

            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/pbb_realisasi_rekap.row.rml')
            
            rows=[]
            for r in query.all():
                s = rml_row.format(tanggal=r.tanggal, kode=r.kode, uraian=r.uraian, pokok=r.pokok,   
                                   denda=r.denda, bayar=r.bayar)
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/pbb_realisasi_rekap.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = logo,
                                line = line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)
                
def route_list(request):
    return HTTPFound(location=request.route_url('pbb-realisasi-rekap'))

def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

########
# Edit #
########
def query_id(id):
    return pbbDBSession.query(PembayaranRekap).\
           filter(PembayaranRekap.id==id)

def id_not_found(request):
    msg = 'User ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)


