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

from ...views.common  import ColumnDT, DataTables    
from ...tools import dict_to_str
from datetime import datetime
from ..views import BaseView

def get_columns():
    columns = [
        ColumnDT(func.concat(Sppt.kd_propinsi,
                 func.concat(Sppt.kd_dati2,
                 func.concat(Sppt.kd_kecamatan,
                 func.concat(Sppt.kd_kelurahan,
                 func.concat(Sppt.kd_blok,
                 func.concat(Sppt.no_urut, 
                 func.concat(Sppt.kd_jns_op, 
                             Sppt.thn_pajak_sppt))))))), mData='id'),
        ColumnDT(func.concat(Sppt.kd_propinsi,
                 func.concat(Sppt.kd_dati2,
                 func.concat(Sppt.kd_kecamatan,
                 func.concat(Sppt.kd_kelurahan,
                 func.concat(Sppt.kd_blok,
                 func.concat(Sppt.no_urut, 
                             Sppt.kd_jns_op)))))), mData='nop'),
        ColumnDT(Sppt.thn_pajak_sppt,           mData='thn_pajak_sppt'),
        ColumnDT(Sppt.pbb_yg_harus_dibayar_sppt, mData='pbb_yg_harus_dibayar_sppt'),
        ColumnDT(func.to_char(Sppt.tgl_terbit_sppt,'DD-MM-YYYY'), mData='tgl_terbit_sppt'),
        ColumnDT(func.to_char(Sppt.tgl_cetak_sppt,'DD-MM-YYYY'), mData='tgl_cetak_sppt'),
        ColumnDT(Sppt.status_pembayaran_sppt,   mData='status_pembayaran_sppt'),
    ]    
    query = PbbDBSession.query().select_from(Sppt)
                
    return columns, query
    
class SpptSismiopPosView(BaseView):
    ########                    
    # List #
    ########    
    @view_config(route_name='pbb-rekon-sppt-sismiop-pos', renderer='templates/rekon/sppt_sismiop_pos.pt',
                 permission='pbb-rekon-sppt-sismiop-pos')
    def view_list(self):
        #rows = DBSession.query(Group).order_by('group_name')
        return dict(project="PBB Tools")



    ########                    
    # ACT #
    ########      
    @view_config(route_name='pbb-rekon-sppt-sismiop-pos-act', renderer='json',
                 permission='pbb-rekon-sppt-sismiop-pos-act')
    def view_grid(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict 
        if url_dict['act'] == 'grid':
            columns, query = get_columns()
            query = query.filter(Sppt.tgl_cetak_sppt.between(self.dt_awal, self.dt_akhir))
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act'] == 'rekon':
            query = PbbDBSession.query(Sppt.kd_propinsi,
                                       Sppt.kd_dati2,
                                       Sppt.kd_kecamatan,
                                       Sppt.kd_kelurahan,
                                       Sppt.kd_blok,
                                       Sppt.no_urut, 
                                       Sppt.kd_jns_op, 
                                       Sppt.thn_pajak_sppt).\
                        filter(Sppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rows = query.all()
        
            queryPbb = PosPbbDBSession.query(PosSppt.kd_propinsi,
                                             PosSppt.kd_dati2,
                                             PosSppt.kd_kecamatan,
                                             PosSppt.kd_kelurahan,
                                             PosSppt.kd_blok,
                                             PosSppt.no_urut, 
                                             PosSppt.kd_jns_op, 
                                             PosSppt.thn_pajak_sppt).\
                        filter(PosSppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rowPbbs = queryPbb.all()
            rowNotFound = []
            if len(rows) != len(rowPbbs):
                rowNotFound = list(set(rows) - set(rowPbbs))
            print "**DEBUG**", len(rows), len(rowPbbs)
            columns,query = get_columns()
            qry = query.filter(tuple_(Sppt.kd_propinsi,
                                      Sppt.kd_dati2,
                                      Sppt.kd_kecamatan,
                                      Sppt.kd_kelurahan,
                                      Sppt.kd_blok,
                                      Sppt.no_urut, 
                                      Sppt.kd_jns_op, 
                                      Sppt.thn_pajak_sppt).in_(rowNotFound[:100]))
                        
            rowTable = DataTables(req.GET, qry, columns)
            return rowTable.output_result()
            
        elif url_dict['act'] == 'update':
            bayar = FixSppt(req.params['id'])
            query = PbbDBSession.query(Sppt).\
                        filter_by(kd_propinsi    = bayar['kd_propinsi'],
                                  kd_dati2       = bayar['kd_dati2'],
                                  kd_kecamatan   = bayar['kd_kecamatan'],
                                  kd_kelurahan   = bayar['kd_kelurahan'],
                                  kd_blok        = bayar['kd_blok'],
                                  no_urut        = bayar['no_urut'], 
                                  kd_jns_op      = bayar['kd_jns_op'], 
                                  thn_pajak_sppt = bayar['thn_pajak_sppt'])
            #print '***DEBUG**********', bayar
            row = query.first()
            if row:
                rowPbb = PosSppt()
                rowPbb.from_dict(row.to_dict())
                 
                try:
                    PosPbbDBSession.add(rowPbb)
                    PosPbbDBSession.flush()
                except:
                    return dict(success=0,message='Gagal %s' %bayar.get_raw())
            return dict(success=1,message='Sukses')                

    ########                    
    # CSV #
    ########          
    @view_config(route_name='pbb-rekon-sppt-sismiop-pos-csv', renderer='csv',
                 permission='pbb-rekon-sppt-sismiop-pos-csv')
    def view_csv(self):
        req = self.req
        ses = req.session
        params = req.params
        url_dict = req.matchdict 
        qry = PbbDBSession.query(
                          func.concat(Sppt.kd_propinsi,
                          func.concat(Sppt.kd_dati2,
                          func.concat(Sppt.kd_kecamatan,
                          func.concat(Sppt.kd_kelurahan,
                          func.concat(Sppt.kd_blok,
                          func.concat(Sppt.no_urut, Sppt.kd_jns_op)))))).label('nop'),
                          Sppt.thn_pajak_sppt, 
                          Sppt.pbb_yg_harus_dibayar_sppt,
                          Sppt.tgl_terbit_sppt,
                          Sppt.tgl_cetak_sppt,
                          Sppt.status_pembayaran_sppt)        
                          
        if url_dict['csv'] == 'rekon':
            query = PbbDBSession.query(Sppt.kd_propinsi,
                                       Sppt.kd_dati2,
                                       Sppt.kd_kecamatan,
                                       Sppt.kd_kelurahan,
                                       Sppt.kd_blok,
                                       Sppt.no_urut, 
                                       Sppt.kd_jns_op, 
                                       Sppt.thn_pajak_sppt).\
                        filter(Sppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rows = query.all()

            queryPbb = PosPbbDBSession.query(PosSppt.kd_propinsi,
                                             PosSppt.kd_dati2,
                                             PosSppt.kd_kecamatan,
                                             PosSppt.kd_kelurahan,
                                             PosSppt.kd_blok,
                                             PosSppt.no_urut, 
                                             PosSppt.kd_jns_op, 
                                             PosSppt.thn_pajak_sppt).\
                        filter(PosSppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
                        
            rowPbbs = queryPbb.all()
            rowNotFound = []
            if len(rows) != len(rowPbbs):
                rowNotFound = list(set(rows) - set(rowPbbs))
            
  

            qry = qry.filter(tuple_(Sppt.kd_propinsi,
                                      Sppt.kd_dati2,
                                      Sppt.kd_kecamatan,
                                      Sppt.kd_kelurahan,
                                      Sppt.kd_blok,
                                      Sppt.no_urut, 
                                      Sppt.kd_jns_op, 
                                      Sppt.thn_pajak_sppt).in_(rowNotFound[:100]))
            
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
            req.response.content_disposition = 'attachment;filename=' + filename

            return {
              'header': header,
              'rows'  : rows,
            }        
            
        elif url_dict['csv'] == 'transaksi':
            qry = qry.filter(Sppt.tgl_cetak_sppt.between(ses['dt_awal'],ses['dt_akhir']))
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
            