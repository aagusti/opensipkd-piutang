from datetime import datetime
from sqlalchemy import (
    Column,
    Integer, BigInteger,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    String,
    SmallInteger,
    ForeignKeyConstraint
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    relationship,
    backref
    )
from ...models import DBSession, Base, CommonModel
ARGS = {'extend_existing':True,  
        'schema': 'simral'}   
     
class SimralRekening(CommonModel, Base):
    __tablename__ = 'rekening'
    kd_rek_akun        = Column(String(30), primary_key=True)
    nm_rek_akun        = Column(String(255))
    kd_rek_kelompok    = Column(String(30), primary_key=True)
    nm_rek_kelompok    = Column(String(255))
    kd_rek_jenis       = Column(String(30), primary_key=True)
    nm_rek_jenis       = Column(String(255))
    kd_rek_obj         = Column(String(30), primary_key=True)
    nm_rek_obj         = Column(String(255))
    kd_rek_rincian_obj = Column(String(30), primary_key=True)
    nm_rek_rincian_obj = Column(String(255))
    __table_args__ = (ARGS,)
     
class SimralSts(CommonModel, Base):
    __tablename__ = 'sts'
    id_trx                 = Column(String(30), primary_key=True)
    no_trx                 = Column(String(30))
    no_sts                 = Column(String(30))
    tgl_pembukuan          = Column(DateTime(timezone=False))
    jns_trx                = Column(String(30))
    uraian_trx             = Column(String(250))
    no_bukti_trx           = Column(String(60))
    tgl_bukti_trx          = Column(DateTime(timezone=False))
    cara_penyetoran        = Column(String(1))
    nm_penandatangan_sts   = Column(String(60))
    jab_penandatangan_sts  = Column(String(100))
    nip_penandatangan_sts  = Column(String(30))
    __table_args__ = (ARGS,)
    
    @classmethod
    def query(cls):
        return DBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        return cls.query().filter_by(id_trx=id)
        
    @classmethod
    def row_id(cls,id):
        return cls.query_id(id).first()
        
class SimralStsDetail(CommonModel, Base):
    __tablename__ = 'sts_detail'
    sts_id_trx  = Column(String(30), primary_key=True)
    no_kohir    = Column(String(30), primary_key=True)
    jumlah      = Column(BigInteger)
    sts         = relationship("SimralSts", backref = "sts_detail")
    __table_args__ = (
            ForeignKeyConstraint([sts_id_trx], [SimralSts.id_trx]),
            ARGS)
    @classmethod
    def query(cls):
        return DBSession.query(cls)
        
class SimralKetetapan(CommonModel, Base):
    __tablename__ = 'ketetapan'
    id_trx         = Column(String(30), primary_key=True)
    no_trx         = Column(String(30))
    tgl_pembukuan  = Column(DateTime(timezone=False))
    jns_trx        = Column(String(30))  #PengakuanPiutang, PenerbitanSKRD PengakuanPdptTrmDmk
    uraian_trx     = Column(String(250)) #changed
    no_bukti_trx   = Column(String(30))
    tgl_bukti_trx  = Column(DateTime(timezone=False))
    tgl_awal_periode = Column(DateTime(timezone=False))
    tgl_akhir_periode = Column(DateTime(timezone=False))
    no_dpa            = Column(String(30), nullable=True)
    no_sub_kegiatan   = Column(String(30), nullable=True)
    nm_penyetor       = Column(String(250)) #changed
    alamat_penyetor   = Column(String(250)) #changed
    npwp_penyetor     = Column(String(30))
    kd_rekening       = Column(String(30))
    nm_rekening       = Column(String(250)) #changed
    jumlah            = Column(BigInteger)
    kd_denda          = Column(String(30))
    nm_denda          = Column(String(250)) #changed
    jumlah_denda      = Column(BigInteger)
    source            = Column(String(30))
    source_id         = Column(String(30))
    __table_args__ = (ARGS)
    
    @classmethod
    def query(cls):
        return DBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        return cls.query().filter_by(id_trx=id)
            
class SimralRealisasi(CommonModel, Base):
    __tablename__ = 'realisasi'
    id_trx         = Column(String(30), primary_key=True)
    no_trx         = Column(String(30))
    no_kohir       = Column(String(30))
    tgl_pembukuan  = Column(DateTime(timezone=False))
    jns_trx        = Column(String(30))  #PengakuanPiutang, PenerbitanSKRD PengakuanPdptTrmDmk
    uraian_trx     = Column(String(250))                  
    no_bukti_trx   = Column(String(30))
    tgl_bukti_trx  = Column(DateTime(timezone=False))
    cara_pembayaran  = Column(Integer)  #0 Melalui Bendahara, 1 Langsung Kasda
    pendapatan_thn_lalu   = Column(Integer) # 0 Tidadk, 1 Ya, 2 Ya Atas Piutang
    pendapatan_dtrm_dimuka = Column(Integer) # 0 Tidak, 1 Ya 
    tgl_awal_periode = Column(DateTime(timezone=False))
    tgl_akhir_periode = Column(DateTime(timezone=False))
    no_dpa            = Column(String(30), nullable=True)
    no_sub_kegiatan   = Column(String(30), nullable=True)
    nm_penyetor       = Column(String(30))
    alamat_penyetor   = Column(String(30))
    npwp_penyetor     = Column(String(30))
    trx_pengakuan_pdpt_id =  Column(String(30))
    kd_rekening       = Column(String(30))
    nm_rekening       = Column(String(30))
    jumlah            = Column(BigInteger)
    kd_denda          = Column(String(30))
    nm_denda          = Column(String(30))
    jumlah_denda      = Column(BigInteger)
    source            = Column(String(30))
    source_id         = Column(String(30))
    __table_args__ = (ARGS)

    @classmethod
    def query(cls):
        return DBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        return cls.query().filter_by(id_trx=id)
    