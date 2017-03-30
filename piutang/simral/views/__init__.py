from ...views.base_views import BaseView
from ...views.common import DataTables, ColumnDT
class SimralView(BaseView):
    def _init__(self,request):
        self.project='Integrasi SIMRAL'
        super(SimralView, self).__init__(request)

JENIS_TRX = (
           ('', '- Select -'),
           ('PengakuanPiutang', 'Pengakuan Piutang'), 
           ('PenerbitanSKRD', 'Penerbitan SKRD'),
           ('PengakuanPdptTrmDmk', 'Pengakuan Pendapatan Dimuka'),
          )
CARA_SETOR =(
             ('', '- Select -'),
             (0, 'Melalui Bendahara'),
             (1, 'Langsung Kasda'),
            )

PENDAPATAN_THN_LALU = (
                      ('', '- Select -'),
                      (0, 'Tidak'),
                      (1, 'Ya'),
                      (2, 'Ya Atas Piutang'),
                      )
                      
PENDAPATAN_DIMUKA = (
                       ('', '- Select -'),
                       (0, 'Tidak'),
                       (1, 'Ya'))