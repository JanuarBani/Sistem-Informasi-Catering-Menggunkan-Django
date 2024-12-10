from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.contrib.auth.hashers import make_password, check_password

# Manager untuk model Pelanggan


class PelangganManager(models.Manager):
    def for_job(self, job_title):
        """Mengambil pelanggan berdasarkan pekerjaan (job title)."""
        return self.filter(pekerjaan__icontains=job_title)

    def for_address(self, address):
        """Mengambil pelanggan berdasarkan alamat tertentu."""
        return self.filter(alamat__icontains=address)

    def newest(self, limit=5):
        """Mengambil pelanggan terbaru berdasarkan ID (terbaru yang mendaftar)."""
        return self.order_by('-idPelanggan')[:limit]

    def active(self):
        """Mengambil pelanggan dengan status aktif (asumsi ada status aktif di model)."""
        return self.filter(status='aktif')

# Model Pelanggan


class Pelanggan(models.Model):
    """Model untuk menyimpan informasi pelanggan."""
    idPelanggan = models.AutoField(verbose_name='ID Pelanggan', primary_key=True)
    nama = models.CharField(max_length=35, verbose_name='Nama')
    alamat = models.TextField(verbose_name='Alamat')
    pekerjaan = models.CharField(max_length=100, verbose_name='Pekerjaan')
    status = models.CharField(max_length=20, choices=[
        ('aktif', _('Aktif')),
        ('non-aktif', _('Non-Aktif')),
    ], default='aktif', verbose_name='Status')

    # Menambahkan Username dan Password (Nullable)
    username = models.CharField(max_length=150, unique=True, verbose_name='Username')
    password = models.CharField(max_length=255, verbose_name='Password')

    # Menambahkan Manager Kustom
    objects = PelangganManager()

    class Meta:
        verbose_name_plural = _('Pelanggan')
        verbose_name = _('Pelanggan')

    def __str__(self):
        return f"{self.idPelanggan},{self.nama} - {self.alamat}"

    def set_password(self, raw_password):
        """Menyimpan password dalam bentuk terenkripsi."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Memeriksa apakah password cocok dengan hash yang tersimpan."""
        return check_password(raw_password, self.password)
    
    

class Categori(models.Model):
    """Model untuk menyimpan kategori acara."""
    idKategori = models.AutoField(
        verbose_name='ID Kategori', primary_key=True)
    namaKategori = models.CharField(
        max_length=100, verbose_name='Nama Kategori')

    class Meta:
        verbose_name_plural = _('Kategori Acara')  # Kept as is
        verbose_name = _('Kategori Acara')

    def __str__(self):
        return f"{self.idKategori} - {self.namaKategori}"


class AcaraManager(models.Manager):
    """Custom manager untuk model Acara."""

    def get_by_category(self, kategori):
        """Mengambil acara berdasarkan kategori."""
        return self.filter(idKategori__namaKategori=kategori)

    def get_upcoming_events(self):
        """Mengambil acara yang akan datang (tanggal setelah hari ini)."""
        from django.utils import timezone
        return self.filter(tanggalAcara__gte=timezone.now())

    def get_past_events(self):
        """Mengambil acara yang telah lewat (tanggal sebelum hari ini)."""
        from django.utils import timezone
        return self.filter(tanggalAcara__lt=timezone.now())

    def get_by_capacity(self, min_capacity, max_capacity):
        """Mengambil acara berdasarkan rentang kapasitas."""
        return self.filter(kapasitas__gte=min_capacity, kapasitas__lte=max_capacity)

# Model Acara


class Acara(models.Model):
    """Model untuk menyimpan informasi acara."""
    idAcara = models.AutoField(verbose_name='ID Acara', primary_key=True)
    idPelanggan = models.ForeignKey('Pelanggan', verbose_name=_(
        "id Pelanggan"), on_delete=models.CASCADE)
    idKategori = models.ForeignKey('Categori', verbose_name=_(
        "idKategori"), on_delete=models.CASCADE, related_name='acara')
    namaAcara = models.CharField(max_length=30, verbose_name='Nama Acara')
    deskripsi = models.TextField(verbose_name='Deskripsi')
    lokasi = models.CharField(max_length=120, verbose_name='Lokasi')
    tanggalAcara = models.DateField(verbose_name='Tanggal Acara')
    kapasitas = models.PositiveIntegerField(verbose_name='Kapasitas')

    # Menambahkan manager custom
    objects = AcaraManager()

    class Meta:
        verbose_name_plural = _('Acara')  # Changed to 'Acara' for consistency
        verbose_name = _('Acara')

    def __str__(self):
        return (f"{self.namaAcara} - {self.deskripsi} - "
                f"{self.lokasi} - {self.tanggalAcara} - {self.kapasitas}")

# Manager Kustom untuk CategoriMenu


class CategoriMenuManager(models.Manager):
    def for_name(self, name):
        """Mengambil kategori berdasarkan nama kategori."""
        return self.filter(namaKategori__icontains=name)

    def with_menus_count(self):
        """Mengambil kategori menu dengan jumlah menu yang terkait."""
        return self.annotate(menu_count=models.Count('menu'))

    def get_top_categories(self, limit=5):
        """Mengambil kategori menu dengan jumlah menu terbanyak."""
        return self.with_menus_count().order_by('-menu_count')[:limit]

# Model CategoriMenu


class CategoriMenu(models.Model):
    """Model untuk menyimpan kategori Menu."""
    idKate = models.AutoField(verbose_name='idKate', primary_key=True)
    namaKategori = models.CharField(
        max_length=100, verbose_name='Nama Kategori')

    # Menambahkan Manager Kustom
    objects = CategoriMenuManager()

    class Meta:
        verbose_name_plural = _('Kategori Menu')
        verbose_name = _('Kategori Menu')

    def __str__(self):
        return f"{self.idKate} - {self.namaKategori}"


# Manager Kustom untuk CateringMenu
class CateringMenuManager(models.Manager):
    def for_category(self, category_id):
        """Mengambil menu berdasarkan kategori (idKategori)."""
        return self.filter(idKate=category_id)

    def in_stock(self):
        """Mengambil menu yang masih memiliki stok lebih dari 0."""
        return self.filter(stok__gt=0)

    def above_price(self, price):
        """Mengambil menu dengan harga di atas nilai tertentu."""
        return self.filter(harga__gt=price)

    def total_value(self):
        """Menghitung total nilai (harga * stok) dari semua menu."""
        return self.aggregate(total_value=Sum(models.F('harga') * models.F('stok')))

# Model CateringMenu dengan Manager Kustom


class CateringMenu(models.Model):
    """Model untuk menyimpan informasi menu catering."""
    idMenu = models.AutoField(verbose_name='ID Menu', primary_key=True)
    idKate = models.ForeignKey(
        CategoriMenu, verbose_name=_("idKate"), on_delete=models.CASCADE, related_name='menu', null=True)
    namaMenu = models.CharField(max_length=35, verbose_name='Nama Menu')
    harga = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Harga')
    deskripsi = models.TextField(verbose_name='Deskripsi')
    img = models.ImageField(upload_to='static/myapp/img/')

    # Menambahkan Manager Kustom
    objects = CateringMenuManager()

    class Meta:
        verbose_name_plural = _('Catering Menu')
        verbose_name = _('Catering Menu')

    def __str__(self):
        return f"{self.namaMenu} - {self.harga}"


class NoTelepon(models.Model):
    """Model untuk menyimpan nomor telepon pelanggan."""
    idNoTelp = models.TextField(verbose_name='ID Telepon', primary_key=True)
    idPelanggan = models.ForeignKey(
        Pelanggan, on_delete=models.CASCADE, related_name='no_telepon')
    noTelp = models.CharField(max_length=35, verbose_name='No Telepon')

    class Meta:
        verbose_name_plural = _('Nomor Telepon')  # Kept as is
        verbose_name = _('Nomor Telepon')

    def __str__(self):
        return f"{self.idNoTelp} - {self.idPelanggan} - {self.noTelp}"


# Manager Kustom untuk PemesananPelanggan
class PemesananPelangganManager(models.Manager):
    def for_status(self, status):
        """Mengambil pemesanan berdasarkan status."""
        return self.filter(status=status)

    def newest(self, limit=5):
        """Mengambil pemesanan terbaru berdasarkan tanggal pemesanan."""
        return self.order_by('-tanggalPemesanan')[:limit]

    def for_date_range(self, start_date, end_date):
        """Mengambil pemesanan yang terjadi dalam rentang tanggal tertentu."""
        return self.filter(tanggalPemesanan__range=[start_date, end_date])

    def above_price(self, price):
        """Mengambil pemesanan dengan total harga lebih dari nilai tertentu."""
        return self.filter(totalHarga__gt=price)

# Model PemesananPelanggan


class PemesananPelanggan(models.Model):
    """Model untuk menyimpan informasi pemesanan pelanggan."""
    STATUS_CHOICES = [
        ('tertunda', _('Tertunda')),
        ('konfirmasi', _('Dikonfirmasi')),
        ('dibatalkan', _('Dibatalkan')),
        ('dikirim', _('Dikirim')),
        ('diterima', _('Diterima')),
    ]

    idPemesanan = models.AutoField(
        verbose_name='ID Pemesanan', primary_key=True)
    idPelanggan = models.ForeignKey(Pelanggan, verbose_name=_(
        'ID Pelanggan'), on_delete=models.CASCADE)
    totalHarga = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='Total Harga')
    jumlahTotal = models.PositiveIntegerField(verbose_name='Jumlah Total')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='tertunda', verbose_name='Status Pesanan')
    tanggalPemesanan = models.DateField(verbose_name='Tanggal Pemesanan')
    waktuPengantaran = models.DateTimeField(_("Waktu Pengantaran"))

    # Menambahkan Manager Kustom
    objects = PemesananPelangganManager()

    class Meta:
        verbose_name_plural = _('Pemesanan Pelanggan')
        verbose_name = _('Pemesanan Pelanggan')

    def __str__(self):
        return (f"{self.idPemesanan} - {self.idPelanggan} - {self.totalHarga} - "
                f"{self.jumlahTotal} - {self.status} - "
                f"{self.tanggalPemesanan} - {self.waktuPengantaran}")


# Manager Kustom
class DetailPemesananManager(models.Manager):
    def for_pemesanan(self, pemesanan_id):
        """Mengambil detail pemesanan berdasarkan ID pemesanan."""
        return self.filter(idPemesanan=pemesanan_id)

    def total_item_for_menu(self, menu_id):
        """Mengambil jumlah total item berdasarkan ID menu."""
        return self.filter(idMenu=menu_id).aggregate(total=models.Sum('jumlahItemMenu'))

# Model DetailPemesanan dengan Manager Kustom


class DetailPemesanan(models.Model):
    """Model untuk menyimpan informasi detail pemesanan dari pelanggan."""
    id = models.AutoField(_("ID Detail Pemesanan"), primary_key=True)
    idPemesanan = models.ForeignKey(PemesananPelanggan, verbose_name=_(
        "ID Pemesanan"), on_delete=models.CASCADE, related_name='detailpem')
    idMenu = models.ForeignKey(CateringMenu, verbose_name=_(
        "ID Menu"), on_delete=models.CASCADE)
    jumlahItemMenu = models.PositiveIntegerField(_("Jumlah Item Menu"))

    # Menambahkan Manager Kustom
    objects = DetailPemesananManager()

    class Meta:
        verbose_name_plural = _('Detail Pemesanan Pelanggan')  # Kept as is
        verbose_name = _('Detail Pemesanan Pelanggan')

    def __str__(self):
        return f"{self.id} - {self.idPemesanan} - {self.idMenu} - {self.jumlahItemMenu}"


# Manager Kustom untuk PemesananAcara
class PemesananAcaraManager(models.Manager):
    def for_status(self, status):
        """Mengambil pemesanan berdasarkan status acara."""
        return self.filter(status=status)

    def newest(self, limit=5):
        """Mengambil pemesanan acara terbaru berdasarkan tanggal pemesanan."""
        return self.order_by('-tanggalPemesanan')[:limit]

    def for_date_range(self, start_date, end_date):
        """Mengambil pemesanan acara yang terjadi dalam rentang tanggal tertentu."""
        return self.filter(tanggalPemesanan__range=[start_date, end_date])

    def above_price(self, price):
        """Mengambil pemesanan acara dengan total harga lebih dari nilai tertentu."""
        return self.filter(totalHarga__gt=price)

# Model PemesananAcara


class PemesananAcara(models.Model):
    """Model untuk menyimpan informasi pemesanan acara."""
    STATUS_CHOICES = [
        ('tertunda', _('Tertunda')),
        ('konfirmasi', _('Dikonfirmasi')),
        ('dibatalkan', _('Dibatalkan')),
        ('dikirim', _('Dikirim')),
        ('diterima', _('Diterima')),
    ]

    idPemesanan = models.AutoField(
        verbose_name='ID Pemesanan', primary_key=True)
    idAcara = models.ForeignKey(Acara, verbose_name=_(
        'ID Acara'), on_delete=models.CASCADE, default=1)
    totalHarga = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Total Harga')
    jumlahTotal = models.PositiveIntegerField(verbose_name='Jumlah Total')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name='Status Pesanan')
    tanggalPemesanan = models.DateField(verbose_name='Tanggal Pemesanan')
    waktuPengantaran = models.DateTimeField(_("Waktu Pengantaran"))

    # Menambahkan Manager Kustom
    objects = PemesananAcaraManager()

    class Meta:
        verbose_name_plural = _('Pemesanan Acara')
        verbose_name = _('Pemesanan Acara')

    def __str__(self):
        return (f"{self.idPemesanan} - {self.idAcara} - {self.totalHarga} - "
                f"{self.jumlahTotal} - {self.status} - "
                f"{self.tanggalPemesanan} - {self.waktuPengantaran}")

# Manager Kustom untuk DetailPemesananAcara


class DetailPemesananAcaraManager(models.Manager):
    def for_pemesanan(self, pemesanan_id):
        """Mengambil detail pemesanan acara berdasarkan ID pemesanan acara."""
        return self.filter(idPemesanan=pemesanan_id)

    def total_item_for_menu(self, menu_id):
        """Mengambil jumlah total item menu berdasarkan ID menu untuk acara."""
        return self.filter(idMenu=menu_id).aggregate(total=models.Sum('jumlahItemMenu'))

# Model DetailPemesananAcara dengan Manager Kustom


class DetailPemesananAcara(models.Model):
    """Model untuk menyimpan informasi detail pemesanan dari pelanggan acara."""
    id = models.AutoField(_("ID Detail Pemesanan"), primary_key=True)
    idPemesanan = models.ForeignKey(PemesananAcara, verbose_name=_(
        "ID Pemesanan"), on_delete=models.CASCADE, related_name='detailAcara')
    idMenu = models.ForeignKey(CateringMenu, verbose_name=_(
        "ID Menu"), on_delete=models.CASCADE)
    jumlahItemMenu = models.PositiveIntegerField(
        _("Jumlah Item Menu"), default=0)

    # Menambahkan Manager Kustom
    objects = DetailPemesananAcaraManager()

    class Meta:
        verbose_name_plural = _('Detail Pemesanan Acara')
        verbose_name = _('Detail Pemesanan Acara')

    def __str__(self):
        return f"{self.id} - {self.idPemesanan} - {self.idMenu} - {self.jumlahItemMenu}"
