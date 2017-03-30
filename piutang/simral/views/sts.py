from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
from pyramid.renderers import render_to_response
import os
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )

from sqlalchemy import func, String, and_  
from ..views import SimralView, ColumnDT, DataTables, JENIS_TRX, CARA_SETOR
from ..models import DBSession, SimralSts, SimralStsDetail, SimralRealisasi
from ..tools import dmy, dmy_to_date, ymd
from ...report_tools import (
        open_rml_row, open_rml_pdf, pdf_response, 
        csv_response, csv_rows)


SESS_ADD_FAILED = 'STS gagal tambah'
SESS_EDIT_FAILED = 'STS gagal edit'

# @colander.deferred
# def deferred_jns_trx(node, kw):
    # values = kw.get('daftar_jns_trx', [])
    # return widget.SelectWidget(values=values)
    
# @colander.deferred
# def deferred_cara_setor(node, kw):
    # values = kw.get('daftar_cara_setor', [])
    # return widget.SelectWidget(values=values)
     
                        
class KetetapanView(SimralView):
    @view_config(route_name="simral-sts", renderer="templates/sts/list.pt",
                 permission="simral-sts")
    def view(self):
        return dict(project=self.project)
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='simral-sts-act', renderer='json',
                 permission='simral-sts-act')
    def view_act(self):
        req = self.req
        ses = req.session
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = [
                ColumnDT(SimralSts.id_trx, mData='id'),
                ColumnDT(SimralSts.no_trx, mData='no_trx'),
                ColumnDT(SimralSts.no_sts, mData='no_sts'),
                ColumnDT(func.to_char(SimralSts.tgl_pembukuan,'DD-MM-YYYY'), mData='tgl_pembukuan'),
                ColumnDT(SimralSts.jns_trx, mData='jns_trx'),
                ColumnDT(SimralSts.uraian_trx, mData='uraian_trx'),
                ColumnDT(SimralSts.no_bukti_trx, mData='no_bukti_trx'),
                ColumnDT(func.to_char(SimralSts.tgl_bukti_trx,'DD-MM-YYYY'), mData='tgl_bukti_trx'),
                ColumnDT(SimralSts.cara_penyetoran, mData='cara_penyetoran'),
                ColumnDT(func.cast(func.sum(SimralStsDetail.jumlah),String), global_search=False, mData='jumlah'),
            ]
            query = DBSession.query().select_from(SimralSts,SimralStsDetail).outerjoin(SimralStsDetail).\
                    group_by(SimralSts.id_trx, SimralSts.no_trx, SimralSts.no_sts,
                             SimralSts.tgl_pembukuan, SimralSts.jns_trx, SimralSts.uraian_trx,
                             SimralSts.no_bukti_trx, SimralSts.tgl_bukti_trx, SimralSts.cara_penyetoran).\
                    filter(SimralSts.tgl_pembukuan.between(self.dt_awal, self.dt_akhir))
                    
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()
        
        elif url_dict['act']=='gridItem':
            sts_id_trx = 'sts_id_trx' in params and params['sts_id_trx'] or ""
            columns = [
                ColumnDT(SimralStsDetail.sts_id_trx, mData='id'),
                ColumnDT(SimralStsDetail.no_kohir, mData='no_kohir'),
                ColumnDT(SimralStsDetail.jumlah, mData='invoice'),
                ColumnDT(SimralStsDetail.jumlah, mData='jumlah'),
                
            ]
            query = DBSession.query().select_from(SimralStsDetail).\
                filter(SimralStsDetail.sts_id_trx==sts_id_trx)
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act']=='saveItem':
            if req.POST:
                controls = req.POST.items()
                control_dicted = dict(controls)
                if control_dicted["old_no_kohir"]:
                    query = SimralStsDetail.query().\
                            filter(
                                SimralStsDetail.sts_id_trx==control_dicted['sts_id_trx'],
                                SimralStsDetail.no_kohir==control_dicted['old_no_kohir'],)
                    row = query.first()
                    if not row:
                        return dict(succes=False,
                                msg = "Gagal Update Data, ID# %s tidak ditemukan" % control_dicted['no_kohir'])
                
                else:
                    #Cek kalau tambah dan datanya sudah ada di return gagal tambah
                    query = SimralStsDetail.query().\
                            filter(
                                SimralStsDetail.sts_id_trx==control_dicted['sts_id_trx'],
                                SimralStsDetail.no_kohir==control_dicted['no_kohir'],)
                    row = query.first()
                    if row:
                        return dict(succes=False,
                                    msg = "Gagal Tambah Data, ID# %s sudah ada dalam database" % control_dicted['no_kohir'])
                
                save_item_request(dict(controls), req, row)
                
                return dict(success = True,
                            msg = "Sukses Simpan Item")
            
        elif url_dict['act']=='delItem':
            if req.POST:
                controls = req.POST.items()
                control_dicted = dict(controls)
                query = SimralStsDetail.query().\
                        filter(
                            SimralStsDetail.sts_id_trx==control_dicted['sts_id_trx'],
                            SimralStsDetail.no_kohir==control_dicted['no_kohir'],)
                row = query.first()
                if not row:
                    return dict(succes=False,
                                msg = "Gagal Hapus Data, ID# %s tidak ditemukan" % control_dicted['no_kohir'])
                
                query.delete()
                DBSession.flush()
                return dict(success = True,
                            msg = "Sukses Hapus Item")
            
        elif url_dict['act']=='gridTbp':
            tgl_bukti_trx = 'tgl_bukti_trx' in params and ymd(dmy_to_date(params['tgl_bukti_trx'])) or self.tanggal
            tbp = SimralRealisasi.jumlah+SimralRealisasi.jumlah_denda
            bayar = func.sum(func.coalesce(SimralStsDetail.jumlah,0))
            columns = [
                ColumnDT(SimralRealisasi.id_trx, mData='id'),
                ColumnDT(SimralRealisasi.uraian_trx, mData='uraian'),
                ColumnDT(tbp, mData='jumlah', global_search=True,),
                ColumnDT(func.cast(bayar,String), mData='sts', global_search=False,),
                ColumnDT(SimralRealisasi.source, mData='src'),
            ]
            query = DBSession.query().select_from(SimralRealisasi).\
                outerjoin(SimralStsDetail, and_(SimralRealisasi.id_trx==SimralStsDetail.no_kohir)).\
                filter(func.to_char(SimralRealisasi.tgl_bukti_trx, "YYYY-MM-DD")==tgl_bukti_trx,).\
                group_by(SimralRealisasi.id_trx, SimralRealisasi.uraian_trx, tbp).\
                having((tbp - bayar)>0)
                
            rowTable = DataTables(req.GET, query, columns)
            return rowTable.output_result()            
        
        elif url_dict['act']=='csv' :
            filename = 'sts.csv'
            query = query_rpt().\
                        filter(SimralSts.tgl_pembukuan.between(self.dt_awal, self.dt_akhir))
            return csv_response(self.req, csv_rows(query), filename)           
        elif url_dict['act']=='pdf' :
            _here = os.path.dirname(__file__)
            path = os.path.join(os.path.dirname(_here), 'reports')
            rml_row = open_rml_row(path+'/sts.row.rml')
            query = query_rpt().\
                        filter(SimralSts.tgl_pembukuan.between(self.dt_awal, self.dt_akhir))
            rows=[]
            for r in query.all():
                s = rml_row.format(
                        id_trx        = r.id_trx,
                        no_trx        = r.no_trx,
                        tgl_pembukuan = r.tgl_pembukuan,
                        jns_trx       = r.jns_trx,
                        no_bukti_trx  = r.no_bukti_trx,
                        tgl_bukti_trx = r.tgl_bukti_trx,
                        uraian_trx    = r.uraian_trx,
                        jumlah        = r.jumlah,
                )
                rows.append(s)
            
            pdf, filename = open_rml_pdf(path+'/sts.rml', rows=rows, 
                                company=self.req.company,
                                departement = self.req.departement,
                                logo = self.logo,
                                line = self.line,
                                address = self.req.address)
            return pdf_response(self.req, pdf, filename)      
            
    @view_config(route_name='simral-sts-add', renderer='templates/sts/add.pt',
                 permission='simral-sts-add')
    def view_add(self):
        request = self.req
        form = get_form(request, AddSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form)
                    return HTTPFound(location=request.route_url('simral-sts-add'))
                save_request(dict(controls), request)
            return route_list(request)
        elif SESS_ADD_FAILED in request.session:
            return session_failed(request, SESS_ADD_FAILED)
        return dict(form=form)

    @view_config(route_name='simral-sts-edit', renderer='templates/sts/edit.pt',
                 permission='simral-sts-edit')
    def view_edit(self):
        request = self.req
        id = request.matchdict['id']
        row = SimralSts.query_id(id).first()
        if not row:
            return id_not_found(request)
        form = get_form(request, EditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    #return dict(form=form)
                    request.session[SESS_EDIT_FAILED] = e.render()               
                    return HTTPFound(location=request.route_url('simral-sts-edit',
                                      id=row.id))
                save_request(dict(controls), request, row)
            return route_list(request)
        elif SESS_EDIT_FAILED in request.session:
            return session_failed(request, SESS_EDIT_FAILED)
        values = row.to_dict()
        values['id'] = id
        values['tgl_pembukuan'] = dmy(row.tgl_pembukuan)
        values['tgl_bukti_trx'] = dmy(row.tgl_bukti_trx)
        form.set_appstruct(values)
        return dict(form=form)
        
class AddSchema(colander.Schema):
    id_trx          = colander.SchemaNode(
                        colander.String(),
                        oid="id_trx")
    no_trx          = colander.SchemaNode(
                        colander.String())
    no_sts          = colander.SchemaNode(
                        colander.String())
    tgl_pembukuan   = colander.SchemaNode(
                        colander.String(),
                        oid = 'tgl_pembukuan')
    jns_trx         = colander.SchemaNode(
                        colander.String(),
                        #widget=deferred_jns_trx
                        widget=widget.SelectWidget(values=JENIS_TRX)
                        )
    uraian_trx      = colander.SchemaNode(
                        colander.String())
    no_bukti_trx    = colander.SchemaNode(
                        colander.String())
    tgl_bukti_trx   = colander.SchemaNode(
                        colander.String(),
                        oid = 'tgl_bukti_trx')
    cara_penyetoran = colander.SchemaNode(
                        colander.Integer(),
                        widget=widget.SelectWidget(values=CARA_SETOR)
                        )
    nm_penandatangan_sts  = colander.SchemaNode(
                                colander.String())
    jab_penandatangan_sts = colander.SchemaNode(
                                colander.String())
    nip_penandatangan_sts = colander.SchemaNode(
                                colander.String())
                                
class EditSchema(AddSchema):
    id = colander.SchemaNode(
            colander.String(),
            oid='id')

def form_validator(form, value):
    pass
    
def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    #schema = schema.bind(daftar_jns_trx=JENIS_TRX)
    #schema = schema.bind(daftar_cara_setor=CARA_SETOR)
    schema.request = request
    return Form(schema, buttons=('save','cancel'))

def save(values, user, row=None):
    if not row:
        row = SimralSts()
    row.from_dict(values)
    DBSession.add(row)
    DBSession.flush()
    return row
    
def save_request(values, request, row=None):
    values['tgl_pembukuan'] = dmy_to_date(values['tgl_pembukuan'])
    values['tgl_bukti_trx'] = dmy_to_date(values['tgl_bukti_trx'])

    row = save(values, request.user, row)
    request.session.flash('STS %s berhasil disimpan.' % row.no_sts)

def save_item(values, user, row=None):
    if not row:
        row = SimralStsDetail()
    row.from_dict(values)
    DBSession.add(row)
    DBSession.flush()
    return row
    
def save_item_request(values, request, row=None):
    row = save_item(values, request.user, row)
    return row
    
def route_list(request):
    return HTTPFound(location=request.route_url('simral-sts'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r

def query_rpt():
    return DBSession.query(SimralSts.id_trx, SimralSts.no_trx, SimralSts.no_sts, 
                    func.to_char(SimralSts.tgl_pembukuan,'DD-MM-YYYY').label('tgl_pembukuan'),
                    SimralSts.jns_trx, SimralSts.uraian_trx, SimralSts.no_bukti_trx, 
                    func.to_char(SimralSts.tgl_bukti_trx,'DD-MM-YYYY').label('tgl_bukti_trx'),
                    SimralSts.cara_penyetoran, 
                    func.sum(SimralStsDetail.jumlah).label('jumlah')).\
                group_by(SimralSts.id_trx, SimralSts.no_trx, SimralSts.no_sts,
                            SimralSts.tgl_pembukuan, SimralSts.jns_trx, 
                            SimralSts.uraian_trx, SimralSts.no_bukti_trx, 
                            SimralSts.tgl_bukti_trx, SimralSts.cara_penyetoran)