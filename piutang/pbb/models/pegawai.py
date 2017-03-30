from datetime import datetime, timedelta

from sqlalchemy import (
    Column, Integer, BigInteger, Float, Text, DateTime, ForeignKey, 
    UniqueConstraint, String, SmallInteger, types, func, ForeignKeyConstraint,
    literal_column, and_
    )
    
from ...models import CommonModel
from ..models import pbbBase, pbbDBSession, pbb_schema, PBB_ARGS

class Pegawai(pbbBase, CommonModel):
    __tablename__ = 'pegawai'
    nip = Column(String(18), primary_key=True)
    nm_pegawai = Column(String(30))
    __table_args__ = (PBB_ARGS,)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        return cls.query().\
                    filter(cls.nip == id,)

class DatLogin(pbbBase, CommonModel):
    __tablename__ = 'dat_login'
    nm_login = Column(String(18), primary_key=True)
    nip = Column(String(18))
    password = Column(String(50))
    __table_args__ = (PBB_ARGS,)
    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        return cls.query().\
                    filter(cls.nm_login == id,)

class PosisiPegawai(pbbBase, CommonModel):
    __tablename__ = 'posisi_pegawai'
    kd_kanwil = Column(String(2), primary_key=True)
    kd_kantor = Column(String(2), primary_key=True)
    nip = Column(String(18), primary_key=True)
    kd_seksi = Column(String(2))
    tgl_awal_berlaku = Column(DateTime(timezone=False))
    tgl_akhir_berlaku = Column(DateTime(timezone=False))
    kd_wewenang = Column(String(2))
    kd_jabatan = Column(String(2))
    __table_args__ = (
        ForeignKeyConstraint([nip], [Pegawai.nip]),
        PBB_ARGS,)

    @classmethod
    def query(cls):
        return pbbDBSession.query(cls)
        
    @classmethod
    def query_id(cls,id):
        return cls.query().\
                    filter(cls.nip == id,)

    @classmethod
    def get_ttd_restitusi_kompensasi(cls, kantor):
        sekarang = datetime.now().strftime("%Y-%m-%d")
        return Pegawai.query().\
                    filter(cls.nip == Pegawai.nip).\
                    filter(cls.kd_kanwil == kantor['kd_kanwil']).\
                    filter(cls.kd_kantor == kantor['kd_kantor']).\
                    filter(cls.kd_jabatan == '10', cls.kd_wewenang == '10').\
                    filter(cls.tgl_awal_berlaku <= func.to_date(sekarang, 'YYYY-MM-DD'), 
                        cls.tgl_akhir_berlaku >= func.to_date(sekarang, 'YYYY-MM-DD')).\
                    first()
#END OF SCRIPT    