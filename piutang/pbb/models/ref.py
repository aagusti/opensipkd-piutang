import sys
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Float,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    String,
    SmallInteger,
    types,
    func,
    ForeignKeyConstraint,
    literal_column,
    and_
    )
from sqlalchemy.orm import aliased

from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import (
    relationship,
    backref,
    #primary_join
    )
import re
from ...tools import as_timezone, FixLength
from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, PBB_ARGS

class TempatPembayaran(pbbBase, CommonModel):
    __tablename__ = 'tempat_pembayaran'
    kd_kanwil = Column(String(2), primary_key=True)
    kd_kantor = Column(String(2), primary_key=True)
    kd_tp = Column(String(2), primary_key=True)
    nm_tp = Column(String(30))
    alamat_tp = Column(String(50))
    no_rek_tp = Column(String(15))
    __table_args__ = (PBB_ARGS,)
    
class Propinsi(pbbBase, CommonModel):
    __tablename__ = 'ref_propinsi'
    kd_propinsi = Column(String(2), primary_key=True)
    nm_propinsi = Column(String(30))
    __table_args__ = (PBB_ARGS,)
    
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)

    @classmethod
    def query_id(cls, id):
        return cls.query().\
                    filter(cls.kd_propinsi == id)
    
class Dati2(pbbBase, CommonModel):
    __tablename__ = 'ref_dati2'
    kd_propinsi = Column(String(2), ForeignKey('pbb.ref_propinsi.kd_propinsi'), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    nm_dati2 = Column(String(30))
    __table_args__ = (
                ForeignKeyConstraint([kd_propinsi], [Propinsi.kd_propinsi]),
                PBB_ARGS)

    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)

    @classmethod
    def query_id(cls, id):
        return cls.query().\
                    filter(cls.kd_propinsi == id[0], cls.kd_dati2 == id[1])

class Kecamatan(pbbBase, CommonModel):
    __tablename__ = 'ref_kecamatan'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    nm_kecamatan = Column(String(30))
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2], [Dati2.kd_propinsi, Dati2.kd_dati2]),
                PBB_ARGS)

class Kelurahan(pbbBase, CommonModel):
    __tablename__ = 'ref_kelurahan'
    kd_propinsi = Column(String(2), primary_key=True)
    kd_dati2 = Column(String(2), primary_key=True)
    kd_kecamatan = Column(String(3), primary_key=True)
    kd_kelurahan = Column(String(3), primary_key=True)
    kd_sektor = Column(String(2))
    nm_kelurahan = Column(String(30))
    no_kelurahan = Column(Integer)
    kd_pos_kelurahan = Column(String(5))
    __table_args__ = (
        ForeignKeyConstraint([kd_propinsi, kd_dati2, kd_kecamatan], 
                             [Kecamatan.kd_propinsi, Kecamatan.kd_dati2, Kecamatan.kd_kecamatan]),
                             PBB_ARGS)

class JenisPelayanan(pbbBase, CommonModel):
    __tablename__ = 'ref_jns_pelayanan'
    kd_jns_pelayanan = Column(String(2), primary_key=True)
    nm_jenis_pelayanan = Column(String(50))
    __table_args__ = (PBB_ARGS)

class Kantor(pbbBase, CommonModel):
    __tablename__ = 'ref_kantor'
    kd_kanwil = Column(String(2), primary_key=True)
    kd_kantor = Column(String(2), primary_key=True)
    nm_kantor = Column(String(30))
    al_kantor = Column(String(50))
    kota_terbit = Column(String(30))
    no_faksimili = Column(String(50))
    no_telpon = Column(String(50))
    __table_args__ = (PBB_ARGS)

    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls, id):
        return cls.query().\
                    filter(cls.kd_kanwil == id[0], cls.kd_kantor == id[1])

class Seksi(pbbBase, CommonModel):
    __tablename__ = 'ref_seksi'
    kd_seksi = Column(String(2), primary_key=True)
    nm_seksi = Column(String(75))
    no_srt_seksi = Column(String(2))
    kode_surat_1 = Column(String(5))
    kode_surat_2 = Column(String(5))
    
    __table_args__ = (PBB_ARGS)

    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)

    @classmethod
    def query_id(cls, id):
        return cls.query().\
                    filter(cls.kd_seksi == id)