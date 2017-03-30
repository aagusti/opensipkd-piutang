create table pbb.keluaran_pst 
(kd_jns_pelayanan character(2) not null, 
sppt_pelayanan int not null default(0), 
stts_pelayanan int not null default(0), 
dhkp_pelayanan int not null default(0), 
sk_pelayanan int not null default(0));

create unique index CONCURRENTLY kl_pst on pbb.keluaran_pst(kd_jns_pelayanan);

alter table pbb.keluaran_pst add constraint pkey_kl_pst primary key using index kl_pst;


