from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    String,
    SmallInteger,
    BigInteger,
    )
from ..models import PosPbbBase, pospbb_schema, CommonModel, POSPBB_ARGS

class Sppt(PosPbbBase, CommonModel):
    __tablename__  = 'sppt'
    __table_args__ = POSPBB_ARGS
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    siklus_sppt                          = Column(Integer)                 
    kd_kanwil                            = Column(String(2))
    kd_kantor                            = Column(String(2))
    kd_tp                                = Column(String(2))
    nm_wp_sppt                           = Column(String(30))
    jln_wp_sppt                          = Column(String(30))
    blok_kav_no_wp_sppt                  = Column(String(15))
    rw_wp_sppt                           = Column(String(2))
    rt_wp_sppt                           = Column(String(3))
    kelurahan_wp_sppt                    = Column(String(30))
    kota_wp_sppt                         = Column(String(30))
    kd_pos_wp_sppt                       = Column(String(5))
    npwp_sppt                            = Column(String(15))
    no_persil_sppt                       = Column(String(5))
    kd_kls_tanah                         = Column(String(3))
    thn_awal_kls_tanah                   = Column(String(4))
    kd_kls_bng                           = Column(String(3))
    thn_awal_kls_bng                     = Column(String(4))
    tgl_jatuh_tempo_sppt                 = Column(DateTime(timezone=False))
    luas_bumi_sppt                       = Column(BigInteger)
    luas_bng_sppt                        = Column(BigInteger)
    njop_bumi_sppt                       = Column(BigInteger)
    njop_bng_sppt                        = Column(BigInteger)
    njop_sppt                            = Column(BigInteger)
    njoptkp_sppt                         = Column(BigInteger)                
    pbb_terhutang_sppt                   = Column(BigInteger)
    faktor_pengurang_sppt                = Column(BigInteger)
    pbb_yg_harus_dibayar_sppt            = Column(BigInteger)
    status_pembayaran_sppt               = Column(String(1))
    status_tagihan_sppt                  = Column(String(1))
    status_cetak_sppt                    = Column(String(1))
    tgl_terbit_sppt                      = Column(DateTime(timezone=False))
    tgl_cetak_sppt                       = Column(DateTime(timezone=False))
    nip_pencetak_sppt                    = Column(String(18))
    #posted                               = Column(Integer)
    
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        fxSppt = FixSppt(id)
        return cls.query().filter(
                cls.kd_propinsi == fxSppt.kd_propinsi,
                cls.kd_dati2 == fxSppt.kd_dati2,
                cls.kd_kecamatan == fxSppt.kd_kecamatan,
                cls.kd_kelurahan == fxSppt.kd_kelurahan,
                cls.kd_blok == fxSppt.kd_blok,
                cls.no_urut == fxSppt.no_urut,
                cls.kd_jns_op == fxSppt.kd_jns_op,
                cls.thn_pajak_sppt == fxSppt.thn_pajak_sppt)
    
    @classmethod
    def query_data(cls):
        return cls.query()
        
    @classmethod
    def count(cls, p_kode):
        fxNop = FixNop(p_kode)
        query = pbbDBSession.query(func.count(cls.kd_propinsi))
        return query.filter(
                cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op).scalar()
                
    @classmethod
    def get_by_nop(cls, p_kode):
        fxNop = FixNop(p_kode)
        query = cls.query()
        return query.filter_by(
                cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op)
                
    @classmethod
    def get_by_nop_thn(cls, p_kode, p_tahun):
        return cls.query_id(p_kode+p_tahun)
                
    @classmethod
    def query_by_nop(cls, nop):
        return cls.get_by_nop(nop)
        
    @classmethod
    def piutang(cls, nop, tahun, tanggal):
        row = cls.query_id(nop+tahun).\
            filter(cls.thn_pajak_sppt == tahun,
                   cls.status_pembayaran_sppt<'2').first()
        if not row:
            return
        pokok = row.pbb_yg_harus_dibayar_sppt
        jatuh_tempo = row.tgl_jatuh_tempo_sppt    
        bayar = PembayaranSppt.get_bayar(nop,tahun).first()
        ke = 1
        if bayar.bayar or bayar.denda or bayar.ke:
            pokok -= (bayar.bayar - bayar.denda)
            ke = bayar.ke+1
        denda = hitung_denda(pokok, jatuh_tempo, tanggal)
        
        return dict(pokok = pokok,
                    denda = denda,
                    jatuh_tempo = jatuh_tempo,
                    ke = ke)
    @classmethod
    def get_bayar(cls, p_kode):
        fxNop = FixNop(p_kode)
        query = pbbDBSession.query(
              func.concat(cls.kd_propinsi, '.').\
                   concat(cls.kd_dati2).concat('-').\
                   concat(cls.kd_kecamatan).concat('.').\
                   concat(cls.kd_kelurahan).concat('-').\
                   concat(cls.kd_blok).concat('.').\
                   concat(cls.no_urut).concat('-').\
                   concat(cls.kd_jns_op).label('nop'), 
            cls.thn_pajak_sppt,
			cls.nm_wp_sppt,	cls.jln_wp_sppt, cls.blok_kav_no_wp_sppt,
			cls.rw_wp_sppt, cls.rt_wp_sppt, cls.kelurahan_wp_sppt,
            cls.kota_wp_sppt, cls.kd_pos_wp_sppt, cls.npwp_sppt, 
            cls.kd_kls_tanah, cls.kd_kls_bng, 
			cls.luas_bumi_sppt, cls.luas_bng_sppt, 
            cls.njop_bumi_sppt, cls.njop_bng_sppt, cls.njop_sppt,			
			cls.njoptkp_sppt, cls.pbb_terhutang_sppt, cls.faktor_pengurang_sppt,
			cls.status_pembayaran_sppt, 
            cls.tgl_jatuh_tempo_sppt,
			cls.pbb_yg_harus_dibayar_sppt.label('pokok'),
            func.max(PembayaranSppt.tgl_pembayaran_sppt).label('tgl_pembayaran_sppt'),
            func.sum(func.coalesce(PembayaranSppt.jml_sppt_yg_dibayar,0)).label('bayar'),
            func.sum(func.coalesce(PembayaranSppt.denda_sppt,0)).label('denda_sppt'),).\
			outerjoin(PembayaranSppt,and_(
                            cls.kd_propinsi==PembayaranSppt.kd_propinsi,
                            cls.kd_dati2==PembayaranSppt.kd_dati2,
                            cls.kd_kecamatan==PembayaranSppt.kd_kecamatan,
                            cls.kd_kelurahan==PembayaranSppt.kd_kelurahan,
                            cls.kd_blok==PembayaranSppt.kd_blok,
                            cls.no_urut==PembayaranSppt.no_urut,
                            cls.kd_jns_op==PembayaranSppt.kd_jns_op,
                            cls.thn_pajak_sppt==PembayaranSppt.thn_pajak_sppt
                            )).\
            group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan, 
                    cls.kd_blok, cls.no_urut, cls.kd_jns_op, cls.thn_pajak_sppt,
                    cls.nm_wp_sppt,	cls.jln_wp_sppt, cls.blok_kav_no_wp_sppt,
                    cls.rw_wp_sppt, cls.rt_wp_sppt, cls.kelurahan_wp_sppt,
                    cls.kota_wp_sppt, cls.kd_pos_wp_sppt, cls.npwp_sppt, 
                    cls.kd_kls_tanah, cls.kd_kls_bng, 
                    cls.luas_bumi_sppt, cls.luas_bng_sppt, 
                    cls.njop_bumi_sppt, cls.njop_bng_sppt, cls.njop_sppt,			
                    cls.njoptkp_sppt, cls.pbb_terhutang_sppt, cls.faktor_pengurang_sppt,
                    cls.status_pembayaran_sppt, 
                    cls.tgl_jatuh_tempo_sppt,
                    cls.pbb_yg_harus_dibayar_sppt.label('pokok'),)
            
        return query.filter(
                cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op)
                            
    @classmethod
    def set_status(cls, id, status):
        row = cls.query_id(id).first()
        if row:
            row.status_pembayaran_sppt = status
            pbbDBSession.add(row)
            pbbDBSession.flush()
        return row
        
    @classmethod
    def get_piutang(cls, p_kode, p_tahun, p_count):
        #Digunakan untuk menampilkan status sppt sesuai dengan jumah p_count
        fxNop = FixNop(p_kode)
        p_tahun_awal = str(int(p_tahun)-p_count+1)
               
        q1 = pbbDBSession.query(cls.thn_pajak_sppt,(cls.pbb_yg_harus_dibayar_sppt).label('pokok'), 
                                   cls.tgl_jatuh_tempo_sppt, cls.nm_wp_sppt,
                                   func.sum(PembayaranSppt.denda_sppt).label('denda_sppt'),
                                   func.sum(PembayaranSppt.jml_sppt_yg_dibayar).label('bayar'),
                                   func.sum(cls.pbb_yg_harus_dibayar_sppt-
                                            (PembayaranSppt.jml_sppt_yg_dibayar-
                                             PembayaranSppt.denda_sppt)).label('sisa')
                                    ).\
              outerjoin(PembayaranSppt, and_(
                  cls.kd_propinsi==PembayaranSppt.kd_propinsi,
                  cls.kd_dati2==PembayaranSppt.kd_dati2,
                  cls.kd_kecamatan==PembayaranSppt.kd_kecamatan,
                  cls.kd_kelurahan==PembayaranSppt.kd_kelurahan,
                  cls.kd_blok==PembayaranSppt.kd_blok,
                  cls.no_urut==PembayaranSppt.no_urut,
                  cls.kd_jns_op==PembayaranSppt.kd_jns_op,
                  cls.thn_pajak_sppt==PembayaranSppt.thn_pajak_sppt
                  )).\
              filter(
                    cls.kd_propinsi == fxNop.kd_propinsi,
                    cls.kd_dati2 == fxNop.kd_dati2,
                    cls.kd_kecamatan == fxNop.kd_kecamatan,
                    cls.kd_kelurahan == fxNop.kd_kelurahan,
                    cls.kd_blok == fxNop.kd_blok,
                    cls.no_urut == fxNop.no_urut,
                    cls.kd_jns_op == fxNop.kd_jns_op).\
              filter(cls.thn_pajak_sppt.between(p_tahun_awal,p_tahun)
                    ).\
              group_by(cls.thn_pajak_sppt, cls.pbb_yg_harus_dibayar_sppt, 
                      cls.tgl_jatuh_tempo_sppt, cls.nm_wp_sppt).subquery()
              
        query = pbbDBSession.query(func.sum(q1.c.pokok).label('pokok'),
                                    func.sum(q1.c.denda_sppt).label('denda_sppt'),
                                    func.sum(q1.c.bayar).label('bayar'),
                                    func.sum(q1.c.sisa).label('sisa'),
                                    )
        
        return query
        
class PembayaranSppt(PosPbbBase, CommonModel):
    __tablename__  = 'pembayaran_sppt'
    __table_args__ = (
                      # ForeignKeyConstraint(['kd_propinsi','kd_dati2','kd_kecamatan','kd_kelurahan',
                              # 'kd_blok', 'no_urut','kd_jns_op', 'thn_pajak_sppt'], 
                              # ['sppt.kd_propinsi', 'sppt.kd_dati2',
                               # 'sppt.kd_kecamatan','sppt.kd_kelurahan',
                               # 'sppt.kd_blok', 'sppt.no_urut',
                               # 'sppt.kd_jns_op','sppt.thn_pajak_sppt']),
                      POSPBB_ARGS)
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_blok = Column(String(3), primary_key=True)
    no_urut = Column(String(4), primary_key=True)
    kd_jns_op = Column(String(1), primary_key=True)
    thn_pajak_sppt = Column(String(4), primary_key=True)
    pembayaran_sppt_ke = Column(Integer, primary_key=True)
    kd_kanwil           = Column(String(2)) 
    kd_kantor           = Column(String(2)) 
    kd_tp               = Column(String(2)) 
    denda_sppt          = Column(BigInteger) 
    jml_sppt_yg_dibayar = Column(BigInteger) 
    tgl_pembayaran_sppt = Column(DateTime(timezone=False)) 
    tgl_rekam_byr_sppt  = Column(DateTime(timezone=False))
    nip_rekam_byr_sppt  = Column(String(18)) 
    posted              = Column(Integer) 

    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        fxBayar = FixBayar(id)
        return cls.query().filter(
                cls.kd_propinsi == fxBayar.kd_propinsi,
                cls.kd_dati2 == fxBayar.kd_dati2,
                cls.kd_kecamatan == fxBayar.kd_kecamatan,
                cls.kd_kelurahan == fxBayar.kd_kelurahan,
                cls.kd_blok == fxBayar.kd_blok,
                cls.no_urut == fxBayar.no_urut,
                cls.kd_jns_op == fxBayar.kd_jns_op,
                cls.thn_pajak_sppt == fxBayar.thn_pajak_sppt,
                cls.thn_pajak_sppt==fxBayar.thn_pajak_sppt,
                cls.kd_kanwil==fxBayar.kd_kanwil,
                cls.kd_kantor==fxBayar.kd_kantor,
                cls.kd_tp==fxBayar.kd_tp,
                cls.pembayaran_sppt_ke==fxBayar.pembayaran_sppt_ke,)
    
    @classmethod
    def query_by_nop(cls, nop):
        fxNop = FixNop(nop)
        return cls.query().\
            filter(cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op)
    
    @classmethod
    def query_by_nop_thn(cls, nop, thn):
        fxNop = FixNop(nop)
        return cls.query().\
            filter(cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op,
                cls.thn_pajak_sppt == thn)
                
    @classmethod
    def query_bayar(cls, nop, tahun):
        fxNop = FixNop(nop)
        q = pbbDBSession.query(func.sum(cls.denda_sppt).label("denda"),
                                 func.sum(cls.jml_sppt_yg_dibayar).label("bayar"),
                                 func.max(cls.pembayaran_sppt_ke).label("ke")).\
            filter(cls.kd_propinsi == fxNop.kd_propinsi,
                cls.kd_dati2 == fxNop.kd_dati2,
                cls.kd_kecamatan == fxNop.kd_kecamatan,
                cls.kd_kelurahan == fxNop.kd_kelurahan,
                cls.kd_blok == fxNop.kd_blok,
                cls.no_urut == fxNop.no_urut,
                cls.kd_jns_op == fxNop.kd_jns_op,
                cls.thn_pajak_sppt == tahun)
        if not q:
            return
        return q
        
    @classmethod
    def reversal(cls, id):
        fxBayar = FixBayar(id)
        q = cls.query_id(id)
        row = q.first()
        if row:
            row.denda_sppt = 0
            row.jml_sppt_yg_dibayar = 0
            pbbDBSession.add(row)
            pbbDBSession.flush()
            Sppt.set_status(id,0)
            
        return row
        