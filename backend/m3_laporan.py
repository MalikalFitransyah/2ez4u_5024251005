"""backend/m3_laporan.py - M3: insertion sort, merge sort, linear search, binary search"""
import time
 
try:
    from .m1_pesanan import Array
except ImportError:                              # dijalankan dari folder backend
    from m1_pesanan import Array
 
BATAS_INSERTION = 20000                          # insertion sort menolak data lebih besar dari ini
 
 
class Pencacah:
    """Dititipkan ke tiap algoritma. banding = jumlah perbandingan kunci,
    pindah = jumlah elemen yang ditulis/dipindahkan. Sama di komputer mana pun."""
 
    def __init__(self):
        self.banding = 0
        self.pindah = 0
 
 
def nilai(p, kunci):
    """Ambil kunci dari satu pesanan. Pesanan yang belum selesai ditaruh paling akhir."""
    if kunci == "oid":
        return p.oid                             # "O-000011": nol di depan membuat urutan teks = urutan angka
    if kunci == "harga":
        return p.harga
    if kunci == "selesai":
        return p.t_selesai if p.t_selesai is not None else 10 ** 9
    raise ValueError("Kunci tidak dikenal: " + kunci + " (pilih oid, harga, atau selesai)")
 
 
def cek_kunci(kunci):
    if kunci != "oid" and kunci != "harga" and kunci != "selesai":
        raise ValueError("Kunci tidak dikenal: " + kunci + " (pilih oid, harga, atau selesai)")
 
 
def salin(A, jumlah=None):
    """Salinan Array (opsional hanya 'jumlah' elemen pertama), supaya data asli tidak berubah."""
    n = A.ukuran if jumlah is None or jumlah > A.ukuran else jumlah
    hasil = Array()
    for i in range(n):
        hasil.tambah_reguler(A.lihat(i))
    return hasil
 
 
def terurut(A, kunci):
    for i in range(1, A.ukuran):
        if nilai(A.data[i - 1], kunci) > nilai(A.data[i], kunci):
            return False
    return True
 
 
# ------------------------------------------------------------ insertion sort
def insertion_sort(A, kunci, cnt=None, batas=BATAS_INSERTION):
    """Di tempat, stabil, O(n^2). Menolak data lebih besar dari 'batas' agar program tidak membeku."""
    cnt = cnt or Pencacah()
    cek_kunci(kunci)
    if A.ukuran > batas:
        raise ValueError("Insertion sort ditolak: batasnya " + str(batas) + " baris, pakai merge sort untuk data besar.")
    d = A.data
    for i in range(1, A.ukuran):
        x = d[i]
        kx = nilai(x, kunci)
        j = i - 1
        while j >= 0:
            cnt.banding += 1
            if nilai(d[j], kunci) > kx:          # ">" bukan ">=": elemen sama kunci tidak saling melewati -> stabil
                d[j + 1] = d[j]
                cnt.pindah += 1
                j -= 1
            else:
                break
        d[j + 1] = x
        cnt.pindah += 1
 
 
# ---------------------------------------------------------------- merge sort
def _gabung(d, tmp, lo, mid, hi, kunci, cnt):
    i, j, k = lo, mid, lo
    while i < mid and j < hi:
        cnt.banding += 1
        if nilai(d[i], kunci) <= nilai(d[j], kunci):   # "<=": bagian kiri didahulukan -> stabil
            tmp[k] = d[i]
            i += 1
        else:
            tmp[k] = d[j]
            j += 1
        k += 1
        cnt.pindah += 1
    while i < mid:                                     # sisa bagian kiri
        tmp[k] = d[i]
        i += 1
        k += 1
        cnt.pindah += 1
    while j < hi:                                      # sisa bagian kanan
        tmp[k] = d[j]
        j += 1
        k += 1
        cnt.pindah += 1
    for k in range(lo, hi):                            # salin balik hasil gabungan
        d[k] = tmp[k]
 
 
def _belah(d, tmp, lo, hi, kunci, cnt):
    if hi - lo < 2:
        return
    mid = (lo + hi) // 2
    _belah(d, tmp, lo, mid, kunci, cnt)
    _belah(d, tmp, mid, hi, kunci, cnt)
    _gabung(d, tmp, lo, mid, hi, kunci, cnt)
 
 
def merge_sort(A, kunci, cnt=None):
    """Stabil, O(n log n), kuat untuk seluruh 200.000 baris. Mengurutkan A di tempat."""
    cnt = cnt or Pencacah()
    cek_kunci(kunci)
    _belah(A.data, [None] * A.ukuran, 0, A.ukuran, kunci, cnt)
 
 
# -------------------------------------------------------------------- search
def linear_search(A, target, kunci="oid", cnt=None):
    """Telusuri dari depan. Return indeks, atau -1 bila tidak ada. O(n), data boleh acak."""
    cnt = cnt or Pencacah()
    cek_kunci(kunci)
    for i in range(A.ukuran):
        cnt.banding += 1
        if nilai(A.data[i], kunci) == target:
            return i
    return -1
 
 
def binary_search(A, target, kunci="oid", cnt=None):
    """A HARUS sudah terurut menurut 'kunci'. Return indeks, atau -1. O(log n)."""
    cnt = cnt or Pencacah()
    cek_kunci(kunci)
    lo, hi = 0, A.ukuran - 1
    while lo <= hi:                                    # "<=" , bukan "<"
        mid = (lo + hi) // 2
        cnt.banding += 1
        k = nilai(A.data[mid], kunci)
        if k == target:
            return mid
        if k < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
 
 
# ------------------------------------------- python m3_laporan.py (dari folder backend)
if __name__ == "__main__":
    try:
        from .m1_pesanan import LinkList, muat_csv
    except ImportError:
        from m1_pesanan import LinkList, muat_csv
    semua = Array()
    muat_csv("../data/pesanan.csv", semua, LinkList())
    print("Tabel n vs perbandingan (kunci harga) - salin ke README")
    print("n".rjust(8) + "insertion".rjust(14) + "merge".rjust(12) + "insertion ms".rjust(15) + "merge ms".rjust(12))
    for n in (500, 1000, 2000, 4000, 8000):
        A, ci, t = salin(semua, n), Pencacah(), time.perf_counter()
        insertion_sort(A, "harga", ci)
        ms_i = (time.perf_counter() - t) * 1000
        A, cm, t = salin(semua, n), Pencacah(), time.perf_counter()
        merge_sort(A, "harga", cm)
        ms_m = (time.perf_counter() - t) * 1000
        print(str(n).rjust(8) + str(ci.banding).rjust(14) + str(cm.banding).rjust(12) +
              ("%.1f" % ms_i).rjust(15) + ("%.1f" % ms_m).rjust(12))
    A, c, t = salin(semua), Pencacah(), time.perf_counter()
    merge_sort(A, "harga", c)
    print("merge sort 200000 baris: %d perbandingan, %.0f ms" % (c.banding, (time.perf_counter() - t) * 1000))