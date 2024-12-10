from django.shortcuts import render, redirect
# from django.db.models import ExtractHour
from django.contrib import messages  # Import messages
from django.db.models import Count
from django.db.models.functions import ExtractHour
from catering1.models import Pelanggan, DetailPemesanan, DetailPemesananAcara, CateringMenu, CategoriMenu, PemesananPelanggan, PemesananAcara, Acara
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import LoginForm
from django.contrib.auth.hashers import check_password
from decimal import Decimal, InvalidOperation
import logging
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


def home(request):
    return render(request, 'home.html')


def jenislaporan(request):
    # Data yang ingin Anda kirim ke template, misalnya:
    context = {
        # Misalnya, ini adalah judul yang ditampilkan di template
        'judul': 'Laporan Jenis Acara',
        # Bisa juga menambahkan data lainnya yang diperlukan di template
    }

    return render(request, 'jenislaporan.html', context)


def create_pelanggan(request):
    if request.method == 'POST':
        id_pelanggan = request.POST.get('idPelanggan')
        nama = request.POST.get('nama')
        alamat = request.POST.get('alamat')
        pekerjaan = request.POST.get('pekerjaan')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Buat instance pelanggan baru
        pelanggan = Pelanggan(
            idPelanggan=id_pelanggan,
            nama=nama,
            alamat=alamat,
            pekerjaan=pekerjaan,
            username=username,
            password=password  # Anda dapat menambahkan enkripsi password di sini jika diperlukan
        )
        pelanggan = Pelanggan(username=username)
        pelanggan.set_password(password)
        pelanggan.save()

        messages.success(request, "Pelanggan berhasil didaftarkan!")
        # Bisa diarahkan ke halaman lain sesuai keinginan
        return redirect('create_pelanggan')

    return render(request, 'formsPelanggan.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            # Ambil data dari form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                # Cek apakah username ada di database Pelanggan
                pelanggan = Pelanggan.objects.get(username=username)
            except Pelanggan.DoesNotExist:  # pylint: disable=no-member
                pelanggan = None
                print(f"[ERROR] Username {
                      username} tidak ditemukan di database.")

            # Jika pelanggan ditemukan, periksa password yang di-hash
            if pelanggan is not None and check_password(password, pelanggan.password):
                # Login berhasil, simpan sesi pelanggan ke request
                request.session['pelanggan_id'] = pelanggan.idPelanggan
                print(f"[INFO] Login berhasil untuk {username}.")
                return redirect('home')  # Redirect ke halaman utama
            else:
                # Jika password salah atau username tidak valid
                if pelanggan is not None:
                    print(f"[WARNING] Password salah untuk username {
                          username}.")
                else:
                    print(f"[WARNING] Username {username} gagal login.")

                # Tampilkan pesan kesalahan langsung di halaman login
                return render(request, 'login.html', {'form': form, 'error': 'Username atau Password salah.'})
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def laporan_pemesanan_acara(request):
    # Mengambil semua pemesanan acara yang sudah dikonfirmasi dan relasi terkait

    pemesanan_acara = PemesananAcara.objects.prefetch_related(
        # Menambahkan prefetch untuk mengambil idPelanggan dari Acara
        'detailAcara', 'detailAcara__idMenu', 'idAcara__idPelanggan')

    laporan_data = []

    # Menampilkan laporan pemesanan acara dan menghitung ulang total harga
    for pemesanan1 in pemesanan_acara:
        total_harga_baru = 0
        detail_pemesanan = []
        # Debugging: Cek apakah idPelanggan ada dan bisa diakses
        print(f"Acara: {pemesanan1.idAcara.namaAcara}")
        if pemesanan1.idAcara.idPelanggan:
            print(f"Pelanggan: {pemesanan1.idAcara.idPelanggan.nama}")
        else:
            print("Tidak ada pelanggan terkait dengan acara ini")

        # Menampilkan menu yang dipesan dan menghitung total harga
        for detail in pemesanan1.detailAcara.all():
            menu = detail.idMenu
            harga_per_item = menu.harga
            jumlah_item = detail.jumlahItemMenu

            # Menghitung harga untuk item ini
            harga_item = harga_per_item * jumlah_item
            total_harga_baru += harga_item

            detail_pemesanan.append({
                'menu': menu.namaMenu,
                'jumlah': jumlah_item,
                'harga_per_item': harga_per_item,
                'totalharga_item': format_number(harga_item),
            })

        laporan_data.append({
            'id_pemesanan': pemesanan1.idPemesanan,
            'nama_pelanggan': pemesanan1.idAcara.idPelanggan.nama,
            'nama_acara': pemesanan1.idAcara.namaAcara,
            'tanggal_pemesanan': pemesanan1.tanggalPemesanan,
            'status': pemesanan1.status,
            'detail_pemesanan': detail_pemesanan,
            'total_harga': format_number(total_harga_baru),
            # Mengambil nama pelanggan melalui Acara
        })

    # Kirimkan data ke template
    return render(request, 'laporan_pemesanan_acara.html', {'laporan_data': laporan_data})


def pemesanan_list(request):
    pemesanan_pelanggan = PemesananPelanggan.objects.prefetch_related(
        'detailpem', 'detailpem__idMenu')  # Mengambil detail pemesanan dan menu terkait
    pemesanan_data = []

    for pemesanan2 in pemesanan_pelanggan:
        total_harga_baru = Decimal('0.00')
        detail_pemesanan = []  # Untuk menyimpan detail pemesanan

        # Menghitung total harga dan menyiapkan detail pemesanan
        for detail in pemesanan2.detailpem.all():
            menu = detail.idMenu
            harga_per_item = menu.harga
            jumlah_item = detail.jumlahItemMenu
            if harga_per_item is not None and jumlah_item is not None:
                try:
                    harga_item = harga_per_item * Decimal(jumlah_item)
                    total_harga_baru += harga_item

                    # Menambahkan detail menu ke list
                    detail_pemesanan.append({
                        'nama_menu': menu.namaMenu,
                        'jumlah_item': jumlah_item,
                        'harga_per_item': harga_per_item,
                        'sub_total': format_number(harga_item)  # Format angka
                    })
                except InvalidOperation:
                    # Jika terjadi kesalahan perhitungan, set subtotal menjadi 0
                    total_harga_baru += Decimal('0.00')

        pemesanan_data.append({
            'id_pemesanan': pemesanan2.idPemesanan,
            'pelanggan': pemesanan2.idPelanggan.nama,
            'tanggal': pemesanan2.tanggalPemesanan,
            'status': pemesanan2.status,
            'total_harga': format_number(total_harga_baru),  # Format angka
            'detail_pemesanan': detail_pemesanan  # Menambahkan detail pemesanan ke data
        })

    return render(request, 'pemesanan_list.html', {'pemesanan_data': pemesanan_data})

# Fungsi untuk memformat angka dengan tanda titik setiap 3 digit


def format_number(value):
    if isinstance(value, Decimal):
        # Format angka dengan 2 digit desimal dan pemisah ribuan
        return "{:,.2f}".format(value)
    return value


def laporan(request):
    # Menghitung total penjualan untuk setiap menu dari DetailPemesanan
    detail_pemesanan = DetailPemesanan.objects.values(
        'idMenu').annotate(total_terjual=Sum('jumlahItemMenu'))

    # Menghitung total penjualan untuk setiap menu dari DetailPemesananAcara
    detail_acara = DetailPemesananAcara.objects.values(
        'idMenu').annotate(total_terjual=Sum('jumlahItemMenu'))

    # Menggabungkan hasil
    combined_results = {}

    for item in detail_pemesanan:
        menu_id = item['idMenu']
        total = item['total_terjual']
        combined_results[menu_id] = combined_results.get(menu_id, 0) + total

    for item in detail_acara:
        menu_id = item['idMenu']
        total = item['total_terjual']
        combined_results[menu_id] = combined_results.get(menu_id, 0) + total

    # Mengambil nama menu dan total terjual
    menu_terlaris = []
    for menu_id, total in combined_results.items():
        try:
            menu = CateringMenu.objects.get(idMenu=menu_id)
            menu_terlaris.append((menu.namaMenu, format_number(total)))
        except CateringMenu.DoesNotExist:  # pylint: disable=no-member
            continue

    # Mengurutkan berdasarkan jumlah terjual
    menu_terlaris.sort(key=lambda x: x[1], reverse=True)

    # Mengambil 5 menu terlaris
    top_menus = menu_terlaris[:5]

    # Render ke template dengan data menu terlaris
    return render(request, 'laporan.html', {'top_menus': top_menus})


def laporan_pekerjaan(request):
    # Menghitung jumlah pelanggan berdasarkan pekerjaan
    pekerjaan_pelanggan = Pelanggan.objects.values('pekerjaan').annotate(
        count=Count('idPelanggan')).order_by('-count')

    # Menyiapkan data untuk ditampilkan
    pekerjaan_terbanyak = []
    for item in pekerjaan_pelanggan:
        pekerjaan = item['pekerjaan']  # Nama pekerjaan
        # Jumlah pelanggan dengan pekerjaan tersebut
        count = item['count']
        pekerjaan_terbanyak.append((pekerjaan, count))

    # Render ke template dengan data pekerjaan terbanyak
    return render(request, 'laporan_pekerjaan.html', {'pekerjaan_terbanyak': pekerjaan_terbanyak})


def laporan_kategori_acara(request):
    # Menghitung jumlah acara berdasarkan kategori
    kategori_acara = Acara.objects.values('idKategori__namaKategori').annotate(
        count=Count('idKategori')).order_by('-count')

    # Menyiapkan data untuk ditampilkan
    kategori_tersering = []
    for item in kategori_acara:
        kategori = item['idKategori__namaKategori']  # Nama kategori acara
        # Jumlah acara yang dipesan dalam kategori tersebut
        count = item['count']
        kategori_tersering.append((kategori, count))

    # Render ke template dengan data kategori acara tersering
    return render(request, 'laporan_kategori_acara.html', {'kategori_tersering': kategori_tersering})


def laporan_waktu_pesanan(request):
    # Menghitung waktu terbanyak pemesanan untuk setiap PemesananPelanggan
    waktu_terbanyak_pesanan = PemesananPelanggan.objects.annotate(
        hour=ExtractHour('waktuPengantaran')
    ).values('hour').annotate(
        count=Count('idPemesanan')
    ).order_by('-count')

    # Menghitung waktu terbanyak pemesanan untuk setiap PemesananAcara
    waktu_terbanyak_pesanan2 = PemesananAcara.objects.annotate(
        hour=ExtractHour('waktuPengantaran')
    ).values('hour').annotate(
        count=Count('idPemesanan')
    ).order_by('-count')

    # Menggabungkan hasil pemesanan pelanggan dan acara
    combined_results = {}

    # Menggabungkan hasil dari PemesananPelanggan
    for item in waktu_terbanyak_pesanan:
        hour = item['hour']  # Jam pengantaran
        count = item['count']  # Jumlah pemesanan pada jam tersebut
        combined_results[hour] = combined_results.get(hour, 0) + count

    # Menggabungkan hasil dari PemesananAcara
    for item in waktu_terbanyak_pesanan2:
        hour = item['hour']
        count = item['count']
        combined_results[hour] = combined_results.get(hour, 0) + count

    # Menyusun hasil akhir berdasarkan jumlah pesanan
    waktuPesanan = [(hour, count) for hour, count in combined_results.items()]

    # Mengurutkan berdasarkan jumlah pesanan terbanyak
    waktuPesanan.sort(key=lambda x: x[1], reverse=True)

    # Mengambil 5 jam terlaris
    top_times = waktuPesanan[:5]

    # Render ke template dengan data top times
    return render(request, 'laporan_waktu.html', {'top_times': top_times})


def laporan_menu_pemesan_paling_sedikit(request):
    # Menghitung jumlah pemesan untuk setiap menu
    menu_dengan_pemesan = CateringMenu.objects.annotate(
        jumlah_pemesan=Count('detailpemesanan') + Count('detailpemesananacara')
        # Mengambil menu yang memiliki pemesan (lebih dari 0)
    ).filter(jumlah_pemesan__gt=0)

    # Menemukan menu dengan jumlah pemesan paling sedikit
    menu_paling_sedikit_pemesan = menu_dengan_pemesan.order_by(
        'jumlah_pemesan').first()

    # Jika ada menu yang memiliki pemesan, ambil nama dan jumlah pemesan
    if menu_paling_sedikit_pemesan:
        menu_data = {
            'nama_menu': menu_paling_sedikit_pemesan.namaMenu,
            'jumlah_pemesan': menu_paling_sedikit_pemesan.jumlah_pemesan
        }
    else:
        menu_data = None

    # Render ke template dengan data menu
    return render(request, 'laporan_Sedikit_pemesanan.html', {'menu_data': menu_data})


def menu_list(request):
    categories = CategoriMenu.objects.all()

    # Ambil semua menu, jika ada kategori terpilih filter berdasarkan kategori
    category_id = request.GET.get('idKate', None)
    if category_id:
        menus = CateringMenu.objects.filter(idKate=category_id)
    else:
        menus = CateringMenu.objects.all()

    context = {
        'menus': menus,
        'categories': categories,
    }

    return render(request, 'menu_list.html', context)


# Setting up logging
logger = logging.getLogger(__name__)


@csrf_exempt
def pemesanan(request):
    categories = CategoriMenu.objects.all()
    menus = CateringMenu.objects.all()

    if request.method == 'POST':
        try:
            # Ambil data dari request body
            data = json.loads(request.body)

            # Log data untuk debugging
            logger.debug("Data yang diterima: %s", data)

            id_pelanggan = data.get('idPelanggan')
            items = data.get('items')
            total_harga = data.get('totalHarga')
            tanggal_pemesanan = data.get('tanggalPemesanan')
            waktu_pengantaran = data.get('waktuPengantaran')

            # Validasi data yang diterima
            if not id_pelanggan or not items or not total_harga or not tanggal_pemesanan or not waktu_pengantaran:
                logger.error('Data tidak lengkap: %s', data)
                return JsonResponse({'error': 'Data tidak lengkap'}, status=400)

            # Verifikasi apakah pelanggan ada
            try:
                pelanggan1 = Pelanggan.objects.get(idPelanggan=id_pelanggan)
                print(pelanggan1.username)
            except Pelanggan.DoesNotExist:  # pylint: disable=no-member
                logger.error(
                    'Pelanggan dengan ID %s tidak ditemukan', id_pelanggan)
                return JsonResponse({'error': 'Pelanggan tidak ditemukan'}, status=404)

            # Buat pemesanan baru
            pesan = PemesananPelanggan.objects.create(
                idPelanggan=id_pelanggan,
                totalHarga=total_harga,
                tanggalPemesanan=tanggal_pemesanan,
                waktuPengantaran=waktu_pengantaran,
            )
            logger.info('Pemesanan berhasil dibuat: %s', pesan.id)

            # Inisialisasi jumlah total untuk pemesanan
            jumlah_total = 0

            # Simpan item pemesanan dan hitung jumlah total
            for item in items:
                try:
                    menu = CateringMenu.objects.get(idMenu=item['idMenu'])
                except CateringMenu.DoesNotExist:  # pylint: disable=no-member
                    logger.error(
                        'Menu dengan ID %s tidak ditemukan', item['idMenu'])
                    return JsonResponse({'error': f"Menu dengan ID {item['idMenu']} tidak ditemukan"}, status=404)

                total_item = item['jumlahItemMenu'] * menu.harga
                jumlah_total += total_item

                # Simpan detail pemesanan
                DetailPemesanan.objects.create(
                    idPemesanan=pesan,
                    idMenu=item['idMenu'],
                    jumlahItemMenu=item['jumlahItemMenu'],
                )

            # Update jumlahTotal setelah menghitung total item
            pesan.jumlahTotal = jumlah_total
            pesan.save()

            logger.info('Jumlah total pemesanan diperbarui: %s',
                        pesan.jumlahTotal)

            return JsonResponse({'message': 'Pesanan berhasil dibuat!'}, status=200)

        except json.JSONDecodeError as e:
            logger.error('Format JSON tidak valid: %s', str(e))
            return JsonResponse({'error': 'Format JSON tidak valid'}, status=400)
        except IntegrityError as e:
            logger.error('Terjadi kesalahan integritas data: %s', str(e))
            return JsonResponse({'error': 'Terjadi kesalahan dalam menyimpan data'}, status=500)
        except ObjectDoesNotExist as e:
            logger.error('Objek tidak ditemukan: %s', str(e))
            return JsonResponse({'error': 'Data tidak ditemukan'}, status=404)
        except Exception as e:
            logger.error('Terjadi kesalahan tak terduga: %s', str(e))
            return JsonResponse({'error': 'Terjadi kesalahan tak terduga'}, status=500)

    return render(request, 'menu_list.html', {'categories': categories, 'menus': menus})
