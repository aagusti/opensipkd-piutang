CREATE TABLE pbb.posisi_pegawai
(
  kd_kanwil character varying(2) NOT NULL,
  kd_kantor character varying(2) NOT NULL,
  nip character varying(18) NOT NULL,
  kd_seksi character varying(2),
  tgl_awal_berlaku date,
  tgl_akhir_berlaku date,
  kd_wewenang character varying(2),
  kd_jabatan character varying(2)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pbb.posisi_pegawai
  OWNER TO tatangs;

CREATE UNIQUE INDEX posisi_pegawai_kd_kanwil_kd_kantor_nip_idx
  ON pbb.posisi_pegawai
  USING btree
  (kd_kanwil COLLATE pg_catalog."default", kd_kantor COLLATE pg_catalog."default", nip COLLATE pg_catalog."default");

