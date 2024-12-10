# Generated by Django 5.1.1 on 2024-10-29 13:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categori',
            fields=[
                ('idKategori', models.CharField(max_length=15, primary_key=True, serialize=False, verbose_name='ID Kategori')),
                ('namaKategori', models.CharField(max_length=100, verbose_name='Nama Kategori')),
            ],
            options={
                'verbose_name': 'Kategori Acara',
                'verbose_name_plural': 'Kategori Acara',
            },
        ),
        migrations.CreateModel(
            name='Pelanggan',
            fields=[
                ('idPelanggan', models.CharField(max_length=15, primary_key=True, serialize=False, verbose_name='ID Pelanggan')),
                ('nama', models.CharField(max_length=35, verbose_name='Nama')),
                ('alamat', models.CharField(max_length=100, verbose_name='Alamat')),
                ('pekerjaan', models.CharField(max_length=100, verbose_name='Pekerjaan')),
            ],
            options={
                'verbose_name_plural': 'Pelanggan',
            },
        ),
        migrations.CreateModel(
            name='CateringMenu',
            fields=[
                ('idMenu', models.CharField(max_length=15, primary_key=True, serialize=False, verbose_name='ID Menu')),
                ('namaMenu', models.CharField(max_length=35, verbose_name='Nama Menu')),
                ('harga', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Harga')),
                ('deskripsi', models.CharField(max_length=100, verbose_name='Deskripsi')),
                ('stok', models.PositiveIntegerField(verbose_name='Stok')),
                ('idKategori', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='catering1.categori', verbose_name='ID Kategori')),
            ],
            options={
                'verbose_name_plural': 'CateringMenu',
            },
        ),
        migrations.CreateModel(
            name='NoTelepon',
            fields=[
                ('idNoTelp', models.CharField(max_length=15, primary_key=True, serialize=False, verbose_name='ID Telepon')),
                ('noTelp', models.CharField(max_length=35, verbose_name='No Telepon')),
                ('idPelanggan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='no_telepon', to='catering1.pelanggan')),
            ],
            options={
                'verbose_name': 'Nomor Telepon',
                'verbose_name_plural': 'Nomor Telepon',
            },
        ),
        migrations.CreateModel(
            name='Acara',
            fields=[
                ('idAcara', models.AutoField(primary_key=True, serialize=False, verbose_name='ID Acara')),
                ('namaAcara', models.CharField(max_length=30, verbose_name='Nama Acara')),
                ('deskripsi', models.CharField(max_length=120, verbose_name='Deskripsi')),
                ('lokasi', models.CharField(max_length=120, verbose_name='Lokasi')),
                ('tanggalAcara', models.DateField(verbose_name='Tanggal Acara')),
                ('kapasitas', models.PositiveIntegerField(verbose_name='Kapasitas')),
                ('idKategori', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='acara', to='catering1.categori', verbose_name='idCategori')),
                ('idPelanggan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catering1.pelanggan', verbose_name='id Pelanggan')),
            ],
            options={
                'verbose_name': 'Acara',
                'verbose_name_plural': 'Acara',
            },
        ),
        migrations.CreateModel(
            name='PemesananAcara',
            fields=[
                ('idPemesanan', models.AutoField(primary_key=True, serialize=False, verbose_name='ID Pemesanan')),
                ('totalHarga', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Total Harga')),
                ('jumlahTotal', models.PositiveIntegerField(verbose_name='Jumlah Total')),
                ('status', models.CharField(max_length=100, verbose_name='Status Pesanan')),
                ('tanggalPemesanan', models.DateField(verbose_name='Tanggal Pemesanan')),
                ('waktuPengantaran', models.DateTimeField(verbose_name='Waktu Pengantaran')),
                ('idPelanggan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catering1.pelanggan', verbose_name='ID Pelanggan')),
            ],
            options={
                'verbose_name': 'Pemesanan Acara',
                'verbose_name_plural': 'Pemesanan Acara',
            },
        ),
        migrations.CreateModel(
            name='DetailPemesananAcara',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID Detail Pemesanan')),
                ('jumlahItemMenu', models.PositiveIntegerField(default=0, verbose_name='Jumlah Item Menu')),
                ('idMenu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catering1.cateringmenu', verbose_name='ID Menu')),
                ('idPemesanan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catering1.pemesananacara', verbose_name='ID Pemesanan')),
            ],
            options={
                'verbose_name': 'Detail Pemesanan Acara',
                'verbose_name_plural': 'Detail Pemesanan Acara',
            },
        ),
        migrations.CreateModel(
            name='PemesananPelanggan',
            fields=[
                ('idPemesanan', models.AutoField(primary_key=True, serialize=False, verbose_name='ID Pemesanan')),
                ('totalHarga', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Total Harga')),
                ('jumlahTotal', models.PositiveIntegerField(verbose_name='Jumlah Total')),
                ('status', models.CharField(max_length=100, verbose_name='Status Pesanan')),
                ('tanggalPemesanan', models.DateField(verbose_name='Tanggal Pemesanan')),
                ('waktuPengantaran', models.DateTimeField(verbose_name='Waktu Pengantaran')),
                ('idPelanggan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catering1.pelanggan', verbose_name='ID Pelanggan')),
            ],
            options={
                'verbose_name': 'Pemesanan Pelanggan',
                'verbose_name_plural': 'Pemesanan Pelanggan',
            },
        ),
        migrations.CreateModel(
            name='DetailPemesanan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID Detail Pemesanan')),
                ('jumlahItemMenu', models.PositiveIntegerField(default=0, verbose_name='Jumlah Item Menu')),
                ('idMenu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catering1.cateringmenu', verbose_name='ID Menu')),
                ('idPemesanan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catering1.pemesananpelanggan', verbose_name='ID Pemesanan')),
            ],
            options={
                'verbose_name': 'Detail Pemesanan Pelanggan',
                'verbose_name_plural': 'Detail Pemesanan Pelanggan',
            },
        ),
    ]