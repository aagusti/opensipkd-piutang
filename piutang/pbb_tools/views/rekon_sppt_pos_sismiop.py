from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
    
from ..models import (
    PosPbbDBSession,
    )
from ..models.pos_pbb import (
    Sppt as PosSppt
    )

from ...pbb.models import (
    pbbDBSession as PbbDBSession
    )
from ...pbb.models.tap import (
    Sppt
    )
from ..tools import FixSppt    
    
    
from sqlalchemy import func, String, tuple_
from sqlalchemy.sql.expression import between

from ...views.common import ColumnDT, DataTables    
from ...tools import dict_to_str
from datetime import datetime
from ..views import BaseView

def get_columns():
    columns = [
        ColumnDT(func.concat(PosSppt.kd_propinsi,
                                              PosSppt.kd_dati2,
                                              PosSppt.kd_kecamatan,
                                              PosSppt.kd_kelurahan,
                                              PosSppt.kd_blok,
                                              PosSppt.no_urut, 
                                              PosSppt.kd_jns_op, 
                                              PosSppt.thn_pajak_sppt), mData='id'),
        ColumnDT(func.concat(PosSppt.kd_propinsi,
                                              PosSppt.kd_dati2,
                                              PosSppt.kd_kecamatan,
                                              PosSppt.kd_kelurahan,
                                              PosSppt.kd_blok,
                                              PosSppt.no_urut, 
                                              PosSppt.kd_jns_op), mData='nop'),
        ColumnDT(PosSppt.thn_pajak_sppt,           mData='thn_pajak_sppt'),
        ColumnDT(PosSppt.pbb_yg_harus_dibayar_sppt, mData='pbb_yg_harus_dibayar_sppt'),
        ColumnDT(func.to_char(PosSppt.tgl_terbit_sppt,'DD-MM-YYYY'), mData='tgl_terbit_sppt'),
        ColumnDT(func.to_char(PosSppt.tgl_cetak_sppt,'DD-MM-YYYY'),  mData='tgl_cetak_sppt'),
        ColumnDT(PosSppt.status_pembayaran_sppt,   mData='status_pembayaran_sppt'),
    ]
        
    query = PosPbbDBSession.query().select_from(PosSppt)
    return columns, query
class RekonSpptPosSismiopView(BaseView):
########                    
# List #
########    

    @view_config(route_name='pbb-rekon-sppt-pos-sismiop', renderer='templates/rekon/sppt_pos_sismiop.pt',
                 permission='pbb-rekon-sppt-pos-sismiop',)
    def view_list(self):
        #rows = DBSession.query(Group).order_by('group_name')
        return dict(project='PBB Tools')


    ########                    
    # ACT #
    ########      
    @view_config(route_name='pbb-rekon-sppt-pos-sismiop-act', renderer='json',
                 permission='=pbb-rekon-sppt-pos-sismiop-act',)
    def view_grid(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict 
        if url_dict['act'] == 'grid':
            columns, query = get_columns()
            query = query.filter(PosSppt.tgl_cetak_sppt.between(self.dt_awal, self.dt_akhir))
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()

        elif url_dict['act'] == 'rekon':
            query = PosPbbDBSession.query(PosSppt.kd_propinsi,
                                          PosSppt.kd_dati2,
                                          PosSppt.kd_kecamatan,
                                          PosSppt.kd_kelurahan,
                                          PosSppt.kd_blok,
                                          PosSppt.no_urut, 
                                          PosSppt.kd_jns_op, 
                                          PosSppt.thn_pajak_sppt).\
                        filter(PosSppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rows = query.all()
        
            queryPbb = PbbDBSession.query(Sppt.kd_propinsi,
                                          Sppt.kd_dati2,
                                          Sppt.kd_kecamatan,
                                          Sppt.kd_kelurahan,
                                          Sppt.kd_blok,
                                          Sppt.no_urut, 
                                          Sppt.kd_jns_op, 
                                          Sppt.thn_pajak_sppt).\
                        filter(Sppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rowPbbs = queryPbb.all()
            rowNotFound = []
            if len(rows) != len(rowPbbs):
                rowNotFound = list(set(rows) - set(rowPbbs))
            #print "**DEBUG**", len(rows), len(rowPbbs)
            
            columns,query = get_columns()
            qry = query.filter(tuple_(PosSppt.kd_propinsi,
                                      PosSppt.kd_dati2,
                                      PosSppt.kd_kecamatan,
                                      PosSppt.kd_kelurahan,
                                      PosSppt.kd_blok,
                                      PosSppt.no_urut, 
                                      PosSppt.kd_jns_op, 
                                      PosSppt.thn_pajak_sppt).in_(rowNotFound[:100]))
                        
            rowTable = DataTables(req.GET, qry, columns)
            return rowTable.output_result()
            
        elif url_dict['act'] == 'update':
            bayar = FixSppt(req.params['id'])
            query = PosPbbDBSession.query(PosSppt).\
                        filter_by(kd_propinsi    = bayar['kd_propinsi'],
                                  kd_dati2       = bayar['kd_dati2'],
                                  kd_kecamatan   = bayar['kd_kecamatan'],
                                  kd_kelurahan   = bayar['kd_kelurahan'],
                                  kd_blok        = bayar['kd_blok'],
                                  no_urut        = bayar['no_urut'], 
                                  kd_jns_op      = bayar['kd_jns_op'], 
                                  thn_pajak_sppt = bayar['thn_pajak_sppt'])
            row = query.first()
            if row:
                rowPbb = Sppt()
                rowPbb.from_dict(row.to_dict())
 
                try:
                    PbbDBSession.add(rowPbb)
                    PbbDBSession.flush()
                except:
                    return dict(success=0,message='Gagal %s' %bayar.get_raw())
            return dict(success=1,message='Sukses')                

    ########                    
    # CSV #
    ########          
    @view_config(route_name='pbb-rekon-sppt-pos-sismiop-csv', renderer='csv',
                 permission='pbb-rekon-sppt-pos-sismiop-csv')
    def view_csv(self):
        req = self.req
        ses = req.session
        params = req.params
        url_dict = req.matchdict 
        qry = PosPbbDBSession.query(
                          func.concat(PosSppt.kd_propinsi,
                          func.concat(PosSppt.kd_dati2,
                          func.concat(PosSppt.kd_kecamatan,
                          func.concat(PosSppt.kd_kelurahan,
                          func.concat(PosSppt.kd_blok,
                          func.concat(PosSppt.no_urut, PosSppt.kd_jns_op)))))).label('nop'),
                          PosSppt.thn_pajak_sppt, 
                          PosSppt.pbb_yg_harus_dibayar_sppt,
                          PosSppt.tgl_terbit_sppt,
                          PosSppt.tgl_cetak_sppt,
                          PosSppt.status_pembayaran_sppt)  
        
        if url_dict['csv'] == 'rekon':
            query = PosPbbDBSession.query(PosSppt.kd_propinsi,
                                          PosSppt.kd_dati2,
                                          PosSppt.kd_kecamatan,
                                          PosSppt.kd_kelurahan,
                                          PosSppt.kd_blok,
                                          PosSppt.no_urut, 
                                          PosSppt.kd_jns_op, 
                                          PosSppt.thn_pajak_sppt).\
                        filter(PosSppt.pbb_yg_harus_dibayar_sppt>0,
                                PosSppt.status_pembayaran_sppt<'2',
                                PosSppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rows = query.all()

            queryPbb = PbbDBSession.query(Sppt.kd_propinsi,
                                          Sppt.kd_dati2,
                                          Sppt.kd_kecamatan,
                                          Sppt.kd_kelurahan,
                                          Sppt.kd_blok,
                                          Sppt.no_urut, 
                                          Sppt.kd_jns_op, 
                                          Sppt.thn_pajak_sppt).\
                        filter(Sppt.pbb_yg_harus_dibayar_sppt>0,
                                Sppt.status_pembayaran_sppt<'2',
                                Sppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
                        
            rowPbbs = queryPbb.all()
            rowNotFound = []
            if len(rows) != len(rowPbbs):
                rowNotFound = list(set(rows) - set(rowPbbs))
            
            
            qry = qry.filter(tuple_(PosSppt.kd_propinsi,
                                      PosSppt.kd_dati2,
                                      PosSppt.kd_kecamatan,
                                      PosSppt.kd_kelurahan,
                                      PosSppt.kd_blok,
                                      PosSppt.no_urut, 
                                      PosSppt.kd_jns_op, 
                                      PosSppt.thn_pajak_sppt).in_(rowNotFound[:100]))
            
            r = qry.first()
            if not r:
                return dict(header = ['Data Tidak Ada'],
                            rows = [['None']])
            header = r.keys()
            query = qry.all()
            rows = []
            for item in query:
                rows.append(list(item))


            # override attributes of response
            filename = 'rekon%s%s.csv' %(ses['awal'], ses['akhir'])
            self.req.response.content_disposition = 'attachment;filename=' + filename

            return {
              'header': header,
              'rows'  : rows,
            }        
            
        elif url_dict['csv'] == 'transaksi':
            qry = qry.filter(PosSppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            r = qry.first()
            if not r:
                return dict(header = ['Data Tidak Ada'],
                            rows = [['None']])            
            header = r.keys()
            query = qry.all()
            rows = []
            for item in query:
                rows.append(list(item))

            # override attributes of response
            filename = 'transaksi%s%s.csv' %(ses['awal'], ses['akhir'])
            req.response.content_disposition = 'attachment;filename=' + filename

            return {
              'header': header,
              'rows'  : rows,
            }        
            
