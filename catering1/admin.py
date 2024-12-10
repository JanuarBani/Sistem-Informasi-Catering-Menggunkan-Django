"""Module providing a function printing python version."""

from django.contrib import admin
from .models import Pelanggan, CateringMenu, NoTelepon, Acara, Categori, PemesananPelanggan, DetailPemesanan, PemesananAcara, DetailPemesananAcara, CategoriMenu


# Register your models with the customized admin classes
admin.site.register(Pelanggan)
admin.site.register(Acara)
admin.site.register(Categori)
admin.site.register(CateringMenu)
admin.site.register(NoTelepon)
admin.site.register(PemesananPelanggan)
admin.site.register(DetailPemesanan)
admin.site.register(PemesananAcara)
admin.site.register(DetailPemesananAcara)
admin.site.register(CategoriMenu)
