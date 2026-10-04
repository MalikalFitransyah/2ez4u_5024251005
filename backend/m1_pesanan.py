"""backend/m1_pesanan.py - M1: Array (tahap 1)"""
import csv


class Pesanan:
    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status):
        self.oid, self.pelanggan, self.resto, self.menu = oid, pelanggan, resto, menu
        self.harga, self.prioritas, self.status = harga, prioritas, status
        self.t_masuk, self.t_selesai = t_masuk, t_selesai

    def __str__(self):
        return self.oid + " | " + self.pelanggan + " | " + self.resto + " | " + \
               self.menu + " | Rp" + str(self.harga) + " | P" + str(self.prioritas) + " | " + self.status


def cek(i, batas):
    if i < 0 or i >= batas:
        raise IndexError("Indeks " + str(i) + " di luar jangkauan")


class Array:
    def __init__(self):
        self.kapasitas = 4
        self.data = [None] * 4
        self.ukuran = 0

    def tambah_reguler(self, v):                 # belakang: O(1) amortized
        if self.ukuran == self.kapasitas:        # penuh -> petak baru 2x, salin isi
            baru = [None] * (self.kapasitas * 2)
            for k in range(self.ukuran):
                baru[k] = self.data[k]
            self.data, self.kapasitas = baru, self.kapasitas * 2
        self.data[self.ukuran] = v
        self.ukuran += 1

    def sisip(self, i, v):                       # O(n): geser ke kanan
        cek(i, self.ukuran + 1)
        self.tambah_reguler(v)                   # pastikan muat
        for k in range(self.ukuran - 1, i, -1):
            self.data[k] = self.data[k - 1]
        self.data[i] = v

    def tambah_prioritas(self, v): self.sisip(self.ukuran // 2, v)
    def tambah_vip(self, v): self.sisip(0, v)

    def lihat(self, i):                          # O(1)
        cek(i, self.ukuran)
        return self.data[i]

    def hapus(self, i):                          # O(n): geser ke kiri
        cek(i, self.ukuran)
        nilai = self.data[i]
        for k in range(i, self.ukuran - 1):
            self.data[k] = self.data[k + 1]
        self.ukuran -= 1
        self.data[self.ukuran] = None
        return nilai


def muat_csv(path, larik):
    """Isi Array dengan data pesanan.csv. Return jumlah baris."""
    jumlah = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        baca = csv.reader(f)
        next(baca)                               # lewati header
        for b in baca:
            selesai = int(b[7]) if b[7] != "" else None
            p = Pesanan(b[0], b[1], b[2], b[3], int(b[4]), int(b[5]), int(b[6]), selesai, b[8])
            larik.tambah_reguler(p)
            jumlah += 1
    return jumlah


if __name__ == "__main__":
    a = Array()
    print("Dimuat:", muat_csv("../data/pesanan.csv", a), "pesanan")
    print(a.lihat(0))