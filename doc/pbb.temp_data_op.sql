CREATE TABLE pbb.temp_data_op
(
  kd_kanwil character varying(2) NOT NULL,
  kd_kantor character varying(2) NOT NULL,
  thn_pelayanan character varying(4) NOT NULL,
  bundel_pelayanan character varying(4) NOT NULL,
  no_urut_pelayanan character varying(3) NOT NULL,
  kd_propinsi_pemohon character varying(2) NOT NULL,
  kd_dati2_pemohon character varying(2) NOT NULL,
  kd_kecamatan_pemohon character varying(3) NOT NULL,
  kd_kelurahan_pemohon character varying(3) NOT NULL,
  kd_blok_pemohon character varying(3) NOT NULL,
  no_urut_pemohon character varying(4) NOT NULL,
  kd_jns_op_pemohon character varying(1) NOT NULL,
  temp_jns_data character varying(1) NOT NULL,
  temp_siklus_sppt double precision NOT NULL DEFAULT 0,
  temp_nm_wp character varying(30) NOT NULL,
  temp_jalan_op character varying(30) NOT NULL,
  temp_blok_kav_no_op character varying(15),
  temp_rw_op character varying(2),
  temp_rt_op character varying(3),
  temp_jalan_wp character varying(30) NOT NULL,
  temp_blok_kav_no_wp character varying(15),
  temp_rw_wp character varying(2),
  temp_rt_wp character varying(3),
  temp_kelurahan_wp character varying(30),
  temp_kota_wp character varying(30),
  temp_kd_pos_wp character varying(5),
  temp_npwp character varying(15),
  temp_subjek_pajak_id character varying(30) NOT NULL,
  kd_kls_tanah character varying(3) NOT NULL,
  thn_awal_kls_tanah character varying(4) NOT NULL,
  kd_kls_bng character varying(3) NOT NULL,
  thn_awal_kls_bng character varying(4) NOT NULL,
  temp_luas_bumi double precision NOT NULL DEFAULT 0,
  temp_luas_bangunan double precision NOT NULL DEFAULT 0,
  temp_njop_bumi double precision NOT NULL DEFAULT 0,
  temp_njop_bangunan double precision NOT NULL DEFAULT 0,
  temp_njop double precision NOT NULL DEFAULT 0,
  temp_njoptkp double precision NOT NULL DEFAULT 0,
  temp_pbb_terhutang double precision NOT NULL DEFAULT 0,
  temp_besar_denda double precision NOT NULL DEFAULT 0,
  temp_faktor_pengurang double precision NOT NULL DEFAULT 0,
  temp_pbb_yg_harus_dibayar double precision NOT NULL DEFAULT 0,
  temp_tgl_jatuh_tempo date NOT NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pbb.temp_data_op
  OWNER TO tatangs;

CREATE UNIQUE INDEX tempdop_key
  ON pbb.temp_data_op
  USING btree
  (kd_kanwil COLLATE pg_catalog."default", kd_kantor COLLATE pg_catalog."default", thn_pelayanan COLLATE pg_catalog."default", bundel_pelayanan COLLATE pg_catalog."default", no_urut_pelayanan COLLATE pg_catalog."default", kd_propinsi_pemohon COLLATE pg_catalog."default", kd_dati2_pemohon COLLATE pg_catalog."default", kd_kecamatan_pemohon COLLATE pg_catalog."default", kd_kelurahan_pemohon COLLATE pg_catalog."default", kd_blok_pemohon COLLATE pg_catalog."default", no_urut_pemohon COLLATE pg_catalog."default", kd_jns_op_pemohon COLLATE pg_catalog."default", temp_jns_data COLLATE pg_catalog."default");
ALTER TABLE pbb.temp_data_op CLUSTER ON tempdop_key;

