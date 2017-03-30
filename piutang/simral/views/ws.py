import sys
import logging
import traceback
from StringIO import StringIO
from ...ws_tools import (
    auth_from_rpc, CODE_NOT_FOUND, CODE_DATA_INVALID)

from pyramid.view import (view_config,view_defaults)
from pyramid.renderers import render_to_response
from datetime import datetime
from pyramid.httpexceptions import (HTTPOk, HTTPException, HTTPError)
from pyramid.response import Response
import re
import json
from ..models import (DBSession, SimralSts, SimralStsDetail, SimralKetetapan,
                      SimralRealisasi)
from sqlalchemy import func
from ..tools import FixLength
from ..views import BaseView
log = logging.getLogger(__name__)

def show_error():
    f = StringIO()
    traceback.print_exc(file=f)
    log.error(f.getvalue())
    f.close()
    
def row_not_found():
    return dict(code = CODE_NOT_FOUND,
            message = 'DATA TIDAK DITEMUKAN')
            
def invalid_params():
    return dict(code = CODE_DATA_INVALID,
            message = 'INVALID PARAMETER')
            
################################################################################
#REST FULL
################################################################################
@view_defaults(route_name='simral-ws-sts-api', renderer='json')
class SimralStsApiViews(object):
    def __init__(self, request):
        self.request = request 

    @view_config(request_method='GET')
    def get(self):
        resp = dict(code = 0)
        #resp,user = auth_from_rpc(request)
        if resp['code'] != 0:
            return resp    
        request = self.request
        tanggal = re.sub('\D',"",request.matchdict['tgl'])
        if not tanggal or len(tanggal)!=8:
            return invalid_params()
        
        query = DBSession.query(SimralSts.id_trx, SimralSts.no_trx, SimralSts.no_sts, 
                    func.to_char(SimralSts.tgl_pembukuan,'YYYY-MM-DD').label('tgl_pembukuan'), 
                    func.to_char(SimralSts.tgl_bukti_trx,'YYYY-MM-DD').label('tgl_bukti_trx'), 
                    SimralSts.jns_trx, SimralSts.uraian_trx, SimralSts.cara_penyetoran,
                    SimralSts.no_bukti_trx, 
                    SimralSts.nm_penandatangan_sts, SimralSts.jab_penandatangan_sts, 
                    SimralSts.nip_penandatangan_sts)
        query = query.filter(func.to_char(SimralSts.tgl_pembukuan,'YYYYMMDD')==tanggal)
        row  =  query.first()
        if not row:
            return row_not_found()
            
        fields = row.keys()
        rows = query.all()
        ret_data = []
        for row in rows:
            ret = dict(zip(fields,row))
            ret['rincian_trx'] = []
            id_trx = row.id_trx
            sts_detail = DBSession.query(SimralStsDetail.no_kohir,
                            SimralStsDetail.jumlah).\
                            filter_by(sts_id_trx = id_trx)
            sts_detail_row = sts_detail.first()
            if sts_detail_row:
                sts_detail_fields = sts_detail_row.keys()
                sts_detail_rows = sts_detail.all()
                for sts_detail_row in sts_detail_rows:
                    ret['rincian_trx'].append(dict(zip(sts_detail_fields,sts_detail_row)))
            ret_data.append(ret)
        return ret_data
        
@view_defaults(route_name='simral-ws-ketetapan-api')
class SimralKetetapanApiViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET', renderer='json')
    def get(self):
        request = self.request
        resp = dict(code = 0)
        #resp,user = auth_from_rpc(request)
        if resp['code'] != 0:
            return resp    
        tanggal = re.sub('\D',"",request.matchdict['tgl'])
        if not tanggal or len(tanggal)!=8:
            return invalid_params()
        
        query = DBSession.query(SimralKetetapan.id_trx, SimralKetetapan.no_trx,
                    func.to_char(SimralKetetapan.tgl_pembukuan, 'YYYY-MM-DD').label('tgl_pembukuan'),
                    SimralKetetapan.jns_trx, SimralKetetapan.no_bukti_trx, SimralKetetapan.uraian_trx,
                    func.to_char(SimralKetetapan.tgl_bukti_trx, 'YYYY-MM-DD').label('tgl_bukti_trx'),
                    func.to_char(SimralKetetapan.tgl_awal_periode, 'YYYY-MM-DD').label('tgl_awal_periode'), 
                    func.to_char(SimralKetetapan.tgl_akhir_periode, 'YYYY-MM-DD').label('tgl_akhir_periode'),
                    SimralKetetapan.no_dpa, SimralKetetapan.no_sub_kegiatan, 
                    SimralKetetapan.nm_penyetor, SimralKetetapan.alamat_penyetor, 
                    SimralKetetapan.npwp_penyetor, SimralKetetapan.kd_rekening,
                    SimralKetetapan.nm_rekening, SimralKetetapan.jumlah, 
                    SimralKetetapan.kd_denda, SimralKetetapan.nm_denda, 
                    SimralKetetapan.jumlah_denda)
        query = query.filter(func.to_char(SimralKetetapan.tgl_pembukuan,'YYYYMMDD')==tanggal)
        row  =  query.first()
        if not row:
            return row_not_found()
            
        fields = row.keys()
        rows = query.all()
        ret_data = []
        for row in rows:
            if row.jumlah+row.jumlah_denda<1:
                continue
            ret = dict( id_trx            = row.id_trx,
                        no_trx            = row.no_trx,
                        tgl_pembukuan     = row.tgl_pembukuan,
                        jns_trx           = row.jns_trx,
                        uraian_trx        = row.uraian_trx,
                        no_bukti_trx      = row.no_bukti_trx,
                        tgl_bukti_trx     = row.tgl_bukti_trx,
                        tgl_awal_periode  = row.tgl_awal_periode,
                        tgl_akhir_periode = row.tgl_akhir_periode,
                        no_dpa            = row.no_dpa,
                        no_sub_kegiatan   = row.no_sub_kegiatan,
                        nm_penyetor       = row.nm_penyetor,
                        alamat_penyetor   = row.alamat_penyetor,
                        npwp_penyetor     = row.npwp_penyetor,
                        rincian_trx       = []
                    )
            if row.jumlah>0:         
                ret['rincian_trx'].append(dict(
                    kd_rekening       = row.kd_rekening,
                    nm_rekening       = row.nm_rekening,
                    jumlah            = row.jumlah,
                    )
                )
            if row.jumlah_denda>0:         
                ret['rincian_trx'].append(dict(
                    kd_rekening       = row.kd_denda,
                    nm_rekening       = row.nm_denda,
                    jumlah            = row.jumlah_denda,
                    )
                )
            ret_data.append(ret)
        return ret_data

    @view_config(request_method='PUT')
    def put(self):
        request = self.request
        resp = dict(code = 0)
        #resp,user = auth_from_rpc(request)
        if resp['code'] != 0:
            return resp    
        data = request.body
        params = json.loads(data)
        if not params:
            return invalid_params()
        print '###################'
            
        for par in params:
            row = SimralKetetapan.query_id(par['id_trx']).first()
            if not row:
                row = SimralKetetapan()
            row.from_dict(par)
            try:
                DBSession.add(row)
                DBSession.flush()
            except Exception as e :
                raise HTTPError(str(e))            
        return Response('ok') #HTTPOk


    @view_config(request_method='DELETE')
    def delete(self):
        request = self.request
        resp = dict(code = 0)
        #resp,user = auth_from_rpc(request)
        if resp['code'] != 0:
            return resp    
        data = request.body
        params = json.loads(data)
        if not params:
            return invalid_params()
        for par in params:
            q = SimralKetetapan.query_id(par['id_trx'])
            row = q.first()
            if row: # and not row.posted:
                q.delete()
                try:
                    DBSession.flush()
                except Exception as e :
                    raise HTTPError               
        return Response('ok') #HTTPOk
                     
@view_defaults(route_name='simral-ws-realisasi-api')
class SimralRealisasiApiViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET', renderer='json')
    def get(self):
        request = self.request
        resp = dict(code = 0)
        #resp,user = auth_from_rpc(request)
        if resp['code'] != 0:
            return resp    
        tanggal = re.sub('\D',"",request.matchdict['tgl'])
        if not tanggal or len(tanggal)!=8:
            return invalid_params()
        
        query = DBSession.query(SimralRealisasi.id_trx, SimralRealisasi.no_trx,
                    func.to_char(SimralRealisasi.tgl_pembukuan, 'YYYY-MM-DD').label('tgl_pembukuan'),
                    SimralRealisasi.no_kohir,
                    SimralRealisasi.jns_trx, SimralRealisasi.no_bukti_trx, 
                    func.to_char(SimralRealisasi.tgl_bukti_trx, 'YYYY-MM-DD').label('tgl_bukti_trx'),
                    func.to_char(SimralRealisasi.tgl_awal_periode, 'YYYY-MM-DD').label('tgl_awal_periode'), 
                    func.to_char(SimralRealisasi.tgl_akhir_periode, 'YYYY-MM-DD').label('tgl_akhir_periode'),
                    SimralRealisasi.uraian_trx,
                    SimralRealisasi.no_dpa, SimralRealisasi.no_sub_kegiatan, 
                    SimralRealisasi.nm_penyetor, SimralRealisasi.alamat_penyetor, 
                    SimralRealisasi.npwp_penyetor, SimralRealisasi.kd_rekening,
                    SimralRealisasi.nm_rekening, SimralRealisasi.jumlah, 
                    SimralRealisasi.kd_denda, SimralRealisasi.nm_denda, 
                    SimralRealisasi.jumlah_denda,
                    SimralRealisasi.cara_pembayaran,
                    SimralRealisasi.pendapatan_thn_lalu,   
                    SimralRealisasi.pendapatan_dtrm_dimuka, 
                    SimralRealisasi.trx_pengakuan_pdpt_id,
                    )
        query = query.filter(func.to_char(SimralRealisasi.tgl_pembukuan,'YYYYMMDD')==tanggal)
        row  =  query.first()
        if not row:
            return row_not_found()
            
        fields = row.keys()
        rows = query.all()
        ret_data = []
        for row in rows:
            if row.jumlah+row.jumlah_denda<1:
                continue
            ret = dict( id_trx            = row.id_trx,
                        no_trx            = row.no_trx,
                        tgl_pembukuan     = row.tgl_pembukuan,
                        no_kohir          = row.no_kohir,
                        jns_trx           = row.jns_trx,
                        no_bukti_trx      = row.no_bukti_trx,
                        tgl_bukti_trx     = row.tgl_bukti_trx,
                        uraian_trx        = row.uraian_trx,
                        tgl_awal_periode  = row.tgl_awal_periode,
                        tgl_akhir_periode = row.tgl_akhir_periode,
                        no_dpa            = row.no_dpa,
                        no_sub_kegiatan   = row.no_sub_kegiatan,
                        nm_penyetor       = row.nm_penyetor,
                        alamat_penyetor   = row.alamat_penyetor,
                        npwp_penyetor     = row.npwp_penyetor,
                        cara_pembayaran        = row.cara_pembayaran,
                        pendapatan_thn_lalu   = row.pendapatan_thn_lalu,
                        pendapatan_dtrm_dimuka = row.pendapatan_dtrm_dimuka,
                        trx_pengakuan_pdpt_id  = row.trx_pengakuan_pdpt_id,
                        rincian_trx       = []
                        )
            if row.jumlah>0:         
                ret['rincian_trx'].append(dict(
                    kd_rekening       = row.kd_rekening,
                    nm_rekening       = row.nm_rekening,
                    jumlah            = row.jumlah,
                    )
                )
            if row.jumlah_denda>0:         
                ret['rincian_trx'].append(dict(
                    kd_rekening       = row.kd_denda,
                    nm_rekening       = row.nm_denda,
                    jumlah            = row.jumlah_denda,
                    )
                )
            ret_data.append(ret)
        return ret_data
        
    @view_config(request_method='PUT')
    def put(self):
        request = self.request
        resp = dict(code = 0)
        #resp,user = auth_from_rpc(request)
        if resp['code'] != 0:
            return resp    
        data = request.body
        params = json.loads(data)
        if not params:
            return invalid_params()
        for par in params:
            row = SimralRealisasi.query_id(par['id_trx']).first()
            if not row:
                row = SimralRealisasi()
            row.from_dict(par)
            try:
                DBSession.add(row)
                DBSession.flush()
            except Exception as e :
                raise HTTPError(str(e))
        return Response('ok') #HTTPOk

    @view_config(request_method='DELETE')
    def delete(self):
        request = self.request
        resp = dict(code = 0)
        #resp,user = auth_from_rpc(request)
        if resp['code'] != 0:
            return resp    
        data = request.body
        params = json.loads(data)
        if not params:
            return invalid_params()
        for par in params:
            q = SimralKetetapan.query_id(par['id_trx'])
            row = q.first()
            if row: # and not row.posted:
                q.delete()
                try:
                    DBSession.flush()
                except Exception as e :
                    raise HTTPError(str(e))
        return Response('ok') #HTTPOk
