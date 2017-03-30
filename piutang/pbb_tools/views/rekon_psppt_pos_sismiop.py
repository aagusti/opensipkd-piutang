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
    PembayaranSppt as PosPembayaranSppt,
    Sppt as PosSppt
    )

from ...pbb.models import (
    pbbDBSession as PbbDBSession
    )
from ...pbb.models.tap import (
    PembayaranSppt,Sppt
    )
    
    
from sqlalchemy import func, String, tuple_
from sqlalchemy.sql.expression import between

from ...views.common  import ColumnDT, DataTables    
from datetime import datetime
from ..views import BaseView
from ..tools import FixBayar        

def get_columns():
    columns = [ColumnDT( func.concat(PosPembayaranSppt.kd_propinsi,
                         func.concat(PosPembayaranSppt.kd_dati2,
                         func.concat(PosPembayaranSppt.kd_kecamatan,
                         func.concat(PosPembayaranSppt.kd_kelurahan,
                         func.concat(PosPembayaranSppt.kd_blok,
                         func.concat(PosPembayaranSppt.no_urut, 
                         func.concat(PosPembayaranSppt.kd_jns_op, 
                         func.concat(PosPembayaranSppt.thn_pajak_sppt, 
                         func.concat(PosPembayaranSppt.pembayaran_sppt_ke,
                         func.concat(PosPembayaranSppt.kd_kanwil, 
                         func.concat(PosPembayaranSppt.kd_kantor, 
                                PosPembayaranSppt.kd_tp, 
                                ))))))))))), mData='id'),
        ColumnDT(func.concat(PosPembayaranSppt.kd_propinsi,
                         func.concat(PosPembayaranSppt.kd_dati2,
                         func.concat(PosPembayaranSppt.kd_kecamatan,
                         func.concat(PosPembayaranSppt.kd_kelurahan,
                         func.concat(PosPembayaranSppt.kd_blok,
                         func.concat(PosPembayaranSppt.no_urut, PosPembayaranSppt.kd_jns_op)))))), mData='nop'),
        ColumnDT(func.concat(PosPembayaranSppt.kd_kanwil,
                         func.concat(PosPembayaranSppt.kd_kantor, 
                                PosPembayaranSppt.kd_tp)), mData="kd_bank"),
        ColumnDT(PosPembayaranSppt.thn_pajak_sppt, mData='thn_pajak_sppt'),
        ColumnDT(PosPembayaranSppt.pembayaran_sppt_ke, mData='pembayaran_sppt_ke'),
        ColumnDT(PosPembayaranSppt.denda_sppt, mData='denda_sppt'),
        ColumnDT(PosPembayaranSppt.jml_sppt_yg_dibayar, mData='jml_sppt_yg_dibayar'),
        ColumnDT(func.to_char(PosPembayaranSppt.tgl_pembayaran_sppt,'DD-MM-YYYY'), mData='tgl_pembayaran_sppt')
        ]

    query = PosPbbDBSession.query().select_from(PosPembayaranSppt)
    return columns, query

class PspptSismiopPosView(BaseView):
    @view_config(route_name='pbb-rekon-psppt-pos-sismiop', renderer='templates/rekon/psppt_pos_sismiop.pt')
    def view_list(self):
        #rows = DBSession.query(Group).order_by('group_name')
        return dict(project='PBB Tools')

    ########                    
    # ACT #
    ########      
    @view_config(route_name='pbb-rekon-psppt-pos-sismiop-act', renderer='json')
    def view_grid(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict 
        
        if url_dict['act'] == 'grid':
            columns, query = get_columns()
            qry = query.filter(PosPembayaranSppt.tgl_pembayaran_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rowTable = DataTables(req.GET, qry, columns)
            return rowTable.output_result()

        elif url_dict['act'] == 'rekon':
            
            query = PosPbbDBSession.query(PosPembayaranSppt.kd_propinsi,
                                             PosPembayaranSppt.kd_dati2,
                                             PosPembayaranSppt.kd_kecamatan,
                                             PosPembayaranSppt.kd_kelurahan,
                                             PosPembayaranSppt.kd_blok,
                                             PosPembayaranSppt.no_urut, 
                                             PosPembayaranSppt.kd_jns_op, 
                                             PosPembayaranSppt.thn_pajak_sppt, 
                                             PosPembayaranSppt.pembayaran_sppt_ke).\
                                        filter(PosPembayaranSppt.tgl_pembayaran_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rows = query.all()
            
            queryPbb = PbbDBSession.query(PembayaranSppt.kd_propinsi,
                                       PembayaranSppt.kd_dati2,
                                       PembayaranSppt.kd_kecamatan,
                                       PembayaranSppt.kd_kelurahan,
                                       PembayaranSppt.kd_blok,
                                       PembayaranSppt.no_urut, 
                                       PembayaranSppt.kd_jns_op, 
                                       PembayaranSppt.thn_pajak_sppt, 
                                       PembayaranSppt.pembayaran_sppt_ke).\
                                filter(PembayaranSppt.tgl_pembayaran_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rowPbbs = queryPbb.all()
                    
            rowNotFound = []
            if len(rows) != len(rowPbbs):
                rowNotFound = list(set(rows) - set(rowPbbs))
            #print "**DEBUG**", len(rows), len(rowPbbs)
            
            columns, query = get_columns()
            qry = query.filter(tuple_(PosPembayaranSppt.kd_propinsi,
                                      PosPembayaranSppt.kd_dati2,
                                      PosPembayaranSppt.kd_kecamatan,
                                      PosPembayaranSppt.kd_kelurahan,
                                      PosPembayaranSppt.kd_blok,
                                      PosPembayaranSppt.no_urut, 
                                      PosPembayaranSppt.kd_jns_op, 
                                      PosPembayaranSppt.thn_pajak_sppt, 
                                      PosPembayaranSppt.pembayaran_sppt_ke).in_(rowNotFound[:100]))
                        
            rowTable = DataTables(req.GET, qry, columns)
            return rowTable.output_result()
            
        elif url_dict['act'] == 'update':
            
            bayar = FixBayar('id' in params and params['id'])
            query = PbbDBSession.query(PosPembayaranSppt).\
                        filter_by(kd_propinsi        = bayar['kd_propinsi'],
                                  kd_dati2           = bayar['kd_dati2'],
                                  kd_kecamatan       = bayar['kd_kecamatan'],
                                  kd_kelurahan       = bayar['kd_kelurahan'],
                                  kd_blok            = bayar['kd_blok'],
                                  no_urut            = bayar['no_urut'], 
                                  kd_jns_op          = bayar['kd_jns_op'], 
                                  thn_pajak_sppt     = bayar['thn_pajak_sppt'],
                                  pembayaran_sppt_ke = bayar['pembayaran_sppt_ke'])
            row = query.first()
            if row:
                rowPbb = PembayaranSppt()
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
    @view_config(route_name='pbb-rekon-psppt-pos-sismiop-csv', renderer='csv')
    def view_csv(self):
        req = self.req
        ses = req.session
        params   = req.params
        url_dict = req.matchdict 
        qry = PbbDBSession.query(func.concat(PembayaranSppt.kd_propinsi,
                         func.concat(PembayaranSppt.kd_dati2,
                         func.concat(PembayaranSppt.kd_kecamatan,
                         func.concat(PembayaranSppt.kd_kelurahan,
                         func.concat(PembayaranSppt.kd_blok,
                         func.concat(PembayaranSppt.no_urut, 
                         func.concat(PembayaranSppt.kd_jns_op, 
                         func.concat(PembayaranSppt.thn_pajak_sppt, 
                         func.concat(PembayaranSppt.kd_kanwil, 
                         func.concat(PembayaranSppt.kd_kantor, 
                         func.concat(PembayaranSppt.kd_tp, 
                                PembayaranSppt.pembayaran_sppt_ke))))))))))).label('id'),
                         func.concat(PembayaranSppt.kd_propinsi,
                         func.concat(PembayaranSppt.kd_dati2,
                         func.concat(PembayaranSppt.kd_kecamatan,
                         func.concat(PembayaranSppt.kd_kelurahan,
                         func.concat(PembayaranSppt.kd_blok,
                         func.concat(PembayaranSppt.no_urut, PembayaranSppt.kd_jns_op)))))).label('nop'),
                         PembayaranSppt.thn_pajak_sppt, 
                         PembayaranSppt.kd_kanwil, 
                         PembayaranSppt.kd_kantor, 
                         PembayaranSppt.kd_tp, 
                         PembayaranSppt.pembayaran_sppt_ke, 
                         PembayaranSppt.denda_sppt, 
                         PembayaranSppt.jml_sppt_yg_dibayar,
                         PembayaranSppt.tgl_pembayaran_sppt)    
            
        if url_dict['csv'] == 'rekon':
            query = PbbDBSession.query(PembayaranSppt.kd_propinsi,
                                       PembayaranSppt.kd_dati2,
                                       PembayaranSppt.kd_kecamatan,
                                       PembayaranSppt.kd_kelurahan,
                                       PembayaranSppt.kd_blok,
                                       PembayaranSppt.no_urut, 
                                       PembayaranSppt.kd_jns_op, 
                                       PembayaranSppt.thn_pajak_sppt, 
                                       PembayaranSppt.pembayaran_sppt_ke).\
                                 filter(PembayaranSppt.tgl_pembayaran_sppt.between(ses['dt_awal'],ses['dt_akhir']))
            rows = query.all()

            queryPbb = PosPbbDBSession.query(PosPembayaranSppt.kd_propinsi,
                                             PosPembayaranSppt.kd_dati2,
                                             PosPembayaranSppt.kd_kecamatan,
                                             PosPembayaranSppt.kd_kelurahan,
                                             PosPembayaranSppt.kd_blok,
                                             PosPembayaranSppt.no_urut, 
                                             PosPembayaranSppt.kd_jns_op, 
                                             PosPembayaranSppt.thn_pajak_sppt, 
                                             PosPembayaranSppt.pembayaran_sppt_ke).\
                                       filter(PosPembayaranSppt.tgl_pembayaran_sppt.between(ses['dt_awal'],ses['dt_akhir']))
                        
            rowPbbs = queryPbb.all()
            rowNotFound = []
            if len(rows) != len(rowPbbs):
                rowNotFound = list(set(rows) - set(rowPbbs))
            
            columns,query = get_columns()
            qry = qry.filter(tuple_(PembayaranSppt.kd_propinsi,
                                      PembayaranSppt.kd_dati2,
                                      PembayaranSppt.kd_kecamatan,
                                      PembayaranSppt.kd_kelurahan,
                                      PembayaranSppt.kd_blok,
                                      PembayaranSppt.no_urut, 
                                      PembayaranSppt.kd_jns_op, 
                                      PembayaranSppt.thn_pajak_sppt, 
                                      PembayaranSppt.pembayaran_sppt_ke).in_(rowNotFound[:100]))
            
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
              'rows': rows,
            }        
            
        elif url_dict['csv'] == 'transaksi':
            qry = qry.filter(PembayaranSppt.tgl_pembayaran_sppt.between(ses['dt_awal'],ses['dt_akhir']))
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
            