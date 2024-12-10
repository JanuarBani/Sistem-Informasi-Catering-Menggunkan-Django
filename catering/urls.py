from django.contrib import admin
from django.urls import path
from catering1.views import home, create_pelanggan, laporan, menu_list, pemesanan, laporan_pekerjaan, laporan_kategori_acara, laporan_waktu_pesanan, laporan_menu_pemesan_paling_sedikit, jenislaporan, login_view, pemesanan_list, laporan_pemesanan_acara

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Halaman utama
    path('laporan/', laporan, name='laporan'),  # Laporan
    path('menu/', menu_list, name='menu_list'),  # Pemesanan
    path('pemesanan/', pemesanan, name='pemesanan'),
    path('laporan_pekerjaan/', laporan_pekerjaan, name='laporan_pekerjaan'),
    path('laporan_kategori_acara/', laporan_kategori_acara,
         name='laporan_kategori_acara'),
    path('laporan_waktu_pesanan/', laporan_waktu_pesanan,
         name='laporan_waktu_pesanan'),
    path('jenislaporan/', jenislaporan, name='jenislaporan'),
    path('laporan_menu_pemesan_paling_sedikit/', laporan_menu_pemesan_paling_sedikit,
         name='laporan_menu_pemesan_paling_sedikit'),
    path('create_pelanggan/', create_pelanggan, name='create_pelanggan'),
    path('login_view/', login_view, name='login_view'),
    path('laporan-pemesanan-acara/', laporan_pemesanan_acara,
         name='laporan-pemesanan-acara'),
    path('pemesanan_list/', pemesanan_list, name='pemesanan_list'),
]
