"""frontend/ui.py - jendela Tkinter 2EZ4U Food Delivery (M1 + M2 + M3)"""
import os
import time
import tkinter as tk
from tkinter import ttk
 
from backend.m1_pesanan import Pesanan, Array, LinkList, muat_csv
from backend.m2_antrean import LayananAntrean, isi_antrean, ke_postfix, hitung
from backend.m3_laporan import Pencacah, insertion_sort, merge_sort, linear_search, binary_search, salin, terurut
 
BIRU, ABU, KUNING, AKTIF = "#1f3a5f", "#6b7280", "#fff8dc", "#dbeafe"
FONT, FONT_B = ("Segoe UI", 10), ("Segoe UI", 10, "bold")
CSV_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pesanan.csv")
KUNCI = ("oid", "harga", "selesai")
 
MENU = [
    ("DATA", [("Load", "load")]),
    ("M1 - DATA PESANAN", [
        ("ARRAY - LIHAT PESANAN", "array_lihat"),
        ("ARRAY - TAMBAH PESANAN REGULER", "array_reguler"),
        ("ARRAY - TAMBAH PESANAN PRIORITAS", "array_prioritas"),
        ("ARRAY - TAMBAH PESANAN VIP", "array_vip"),
        ("ARRAY - HAPUS PESANAN", "array_hapus"),
        ("LINKEDLIST - LIHAT PESANAN", "linkedlist_lihat"),
        ("LINKEDLIST - TAMBAH PESANAN REGULER", "linkedlist_reguler"),
        ("LINKEDLIST - TAMBAH PESANAN PRIORITAS", "linkedlist_prioritas"),
        ("LINKEDLIST - TAMBAH PESANAN VIP", "linkedlist_vip"),
        ("LINKEDLIST - HAPUS PESANAN", "linkedlist_hapus")]),
    ("M2 - STACK DAN QUEUE", [
        ("STACK - POSTFIX (MESIN KASIR)", "stack_postfix"),
        ("STACK - UNDO", "stack_undo"),
        ("STACK - REDO", "stack_redo"),
        ("QUEUE - ENQUEUE", "queue_enqueue"),
        ("QUEUE - DEQUEUE NAIF", "queue_dequeue_naive"),
        ("QUEUE - DEQUEUE CIRCULAR", "queue_dequeue_circular")]),
    ("M3 - SORT DAN SEARCH", [
        ("SORT - INSERTION SORT", "sort_insertion"),
        ("SORT - MERGE SORT", "sort_merge"),
        ("SEARCH - LINEAR SEARCH", "search_linear"),
        ("SEARCH - BINARY SEARCH", "search_binary")]),
]
 
 
# ---------------------------------------------------------------- bantu
def ribu(n):                                     # 19852 -> "19.852"
    s, hasil = str(n), ""
    while len(s) > 3:
        hasil = "." + s[-3:] + hasil
        s = s[:-3]
    return s + hasil
 
 
def d2(n): return ("0" + str(n))[-2:]
def jam(detik): return d2(detik // 3600) + ":" + d2(detik % 3600 // 60) + ":" + d2(detik % 60)
def waktu(t): return "%.2f ms" % ((time.perf_counter() - t) * 1000)
 
 
def rupiah(x):
    if isinstance(x, float):
        return ribu(int(x)) if x == int(x) else str(x)
    return ribu(x)
 
 
def bulat(teks, minimal=0):
    try:
        n = int(teks.strip())
    except ValueError:
        raise ValueError("Masukkan angka bulat.")
    if n < minimal:
        raise ValueError("Angka minimal " + str(minimal) + ".")
    return n
 
 
def susun(*item):                                # tuple -> Array
    a = Array()
    for x in item:
        a.tambah_reguler(x)
    return a
 
 
def selesai(p): return "-" if p.t_selesai is None else jam(p.t_selesai)
 
 
def detail(p):
    return susun(("oid", p.oid), ("pelanggan", p.pelanggan), ("resto", p.resto), ("menu", p.menu),
                 ("harga", "Rp " + ribu(p.harga)), ("prioritas", str(p.prioritas)),
                 ("masuk", jam(p.t_masuk)), ("selesai", selesai(p)), ("status", p.status))
 
 
def tabel_pesanan(daftar, dengan_jam):           # baris (#, oid, pelanggan, resto, menu[, masuk])
    baris = Array()
    for i in range(min(daftar.ukuran, 300)):     # tampilkan paling banyak 300 baris
        p = daftar.lihat(i)
        isi = (str(i + 1), p.oid, p.pelanggan, p.resto, p.menu)
        baris.tambah_reguler(isi + (jam(p.t_masuk),) if dengan_jam else isi)
    return baris
 
 
def tabel_sort(A):                               # 30 baris pertama hasil sort, lengkap dengan harga dan waktu selesai
    baris = Array()
    for i in range(min(A.ukuran, 30)):
        p = A.lihat(i)
        baris.tambah_reguler((str(i + 1), p.oid, p.pelanggan, p.resto, p.menu, ribu(p.harga), selesai(p)))
    return baris
 
 
KOLOM_P = ("#", "oid", "pelanggan", "resto", "menu")
KOLOM_PJ = KOLOM_P + ("masuk",)
KOLOM_S = KOLOM_P + ("harga", "selesai")
 
 
def lebar_kolom(kolom):                          # lebar piksel tiap kolom tabel
    n = len(kolom)
    if n == 5 and kolom[0] == "langkah":
        return (70, 70, 330, 170, 260)
    if n == 7:
        return (45, 90, 150, 120, 110, 80, 90)
    if n == 2:
        return (230, 570)
    return (50,) + (150,) * (n - 1)
 
 
def info(key):
    """(judul, deskripsi, field, teks tombol, hint, catatan); field = ((label, awal, pilihan atau None), ...)"""
    arr = key.startswith("array")
    S = "Array" if arr else "Linked list"
    if key == "load":
        return ("Data: muat pesanan.csv", "Membaca seluruh baris ke Array, Linked List, dan kedua antrean M2.",
                (("Lokasi file CSV", CSV_DEFAULT, None),), "LOAD", "Kosongkan untuk memakai data/pesanan.csv.",
                "Data dibaca sekali dan disimpan pada dua struktur sekaligus. Pesanan berstatus ANTRE ikut "
                "dimasukkan ke antrean naif dan circular. Menu lain baru bisa dipakai setelah Load.")
    if key.endswith("_lihat"):
        return (S + ": lihat pesanan ke-i", "Membuka detail satu pesanan berdasarkan nomor urut (indeks).",
                (("Indeks pesanan (mulai dari 0)", "0", None),), "LIHAT", "Coba 0, lalu 100000, untuk membandingkan.",
                "Array menghitung alamat dari indeks sehingga LIHAT selalu satu langkah, O(1)." if arr else
                "Linked list tidak punya alamat yang bisa dihitung: harus melangkah dari head, makin besar "
                "indeks makin lama, O(n). Bandingkan dengan ARRAY - LIHAT PESANAN.")
    if key.endswith("_hapus"):
        return (S + ": hapus pesanan ke-i", "Mencabut pesanan ke-i dari barisan.",
                (("Indeks yang dihapus (mulai dari 0)", "0", None),), "HAPUS", "Indeks 0 adalah kasus terburuk untuk Array.",
                "Setelah dicabut, elemen di kanannya digeser ke kiri: O(n)." if arr else
                "Simpul sebelumnya dicari dulu dari head, lalu cukup melewati simpul target: O(n) telusur.")
    if key.startswith("array_") or key.startswith("linkedlist_"):
        judul = ("pesanan REGULER, masuk paling belakang" if key.endswith("reguler") else
                 "pesanan PRIORITAS, masuk di tengah barisan" if key.endswith("prioritas") else
                 "pesanan VIP, masuk paling depan")
        desk = ("Menambah pesanan biasa (prioritas 3) di ujung belakang barisan." if key.endswith("reguler") else
                "Menambah pesanan prioritas (2) ke tengah barisan, indeks ukuran // 2." if key.endswith("prioritas") else
                "Menambah pesanan VIP (1) di urutan pertama, indeks 0.")
        if key.endswith("reguler"):
            cat = ("Menempel di ujung. Petak baru 2x hanya dibuat saat penuh, jadi amortized O(1)." if arr else
                   "Penunjuk tail disimpan, jadi tidak perlu menelusuri dari head: O(1).")
        elif key.endswith("prioritas"):
            cat = ("Menyisip di tengah memaksa separuh isi array bergeser ke kanan: O(n)." if arr else
                   "Menyambung hanya sekali, tetapi simpul tengah harus dicari dulu dari head: O(n) telusur.")
        else:
            cat = ("Menyisip di depan memaksa SELURUH isi array bergeser satu petak: O(n). Operasi terburuknya." if arr else
                   "Cukup mengubah satu penunjuk head, tanpa menelusuri atau menggeser apa pun: O(1).")
        return (S + ": " + judul, desk, (("Nama pelanggan", "Pelanggan Baru", None),), "TAMBAH",
                "Nama untuk pesanan yang akan dibuat.", cat + " Tiap menu hanya mengubah satu struktur.")
    if key == "stack_postfix":
        return ("Stack: hitung struk lewat postfix",
                "Struk ditulis infix, lalu dihitung dua tahap dengan stack: tahap 1 infix menjadi postfix, tahap 2 postfix dievaluasi.",
                (("Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000", None),), "HITUNG",
                "angka, + - * / dan tanda kurung. 3 x Rp12.000 dan 2 x Rp8.500, potongan Rp5.000.",
                "Baris 1.x adalah tahap konversi, baris 2.x tahap evaluasi. Tahap 1 menahan operator di stack sampai "
                "gilirannya tiba, tanda ( hanya mengatur stack. Tahap 2 mengumpulkan angka, tiap operator mengambil "
                "dua nilai teratas. Operand kanan selalu keluar lebih dulu.")
    if key == "stack_undo":
        return ("Stack: batalkan aksi terakhir",
                "Mengambil catatan teratas tumpukan undo, lalu menjalankan kebalikannya. Aksi terakhirlah yang dibatalkan lebih dulu.",
                (), "UNDO", "",
                "Kebalikan enqueue adalah membuang elemen paling belakang. Kebalikan dequeue mengembalikan SELURUH "
                "pesanan yang keluar ke DEPAN antrean, bukan ke belakang. Tambah dan hapus pesanan di M1 juga bisa dibatalkan.")
    if key == "stack_redo":
        return ("Stack: ulangi aksi yang dibatalkan",
                "Mengambil catatan teratas tumpukan redo lalu mengerjakan ulang aksi aslinya. Aksi baru apa pun mengosongkan tumpukan redo.",
                (), "REDO", "",
                "Redo mengerjakan aksi aslinya, bukan kebalikannya. Setelah undo lalu aksi baru, riwayat bercabang "
                "sehingga redo dikosongkan dan REDO tidak melakukan apa-apa.")
    if key == "queue_enqueue":
        return ("Queue: pesanan baru masuk ke belakang",
                "Menambah pesanan di ujung belakang kedua antrean sekaligus, yang naif maupun yang circular.",
                (("Nama pelanggan", "Pelanggan Baru", None),), "ENQUEUE", "Nama untuk pesanan yang akan dibuat.",
                "Enqueue selalu menempel di belakang, jadi O(1) pada kedua antrean. Perbedaannya baru muncul saat dequeue.")
    if key == "queue_dequeue_naive":
        return ("Queue naif: ambil dari depan dengan menggeser isi",
                "Mengambil indeks 0 lalu menggeser seluruh sisa isi satu petak ke kiri. Biayanya O(n) setiap kali.",
                (("Berapa kali dequeue:", "1", None),), "DEQUEUE", "Isi panjang antrean; coba 1 lalu 100 untuk melihat bedanya.",
                "Mengambil indeks 0 memaksa seluruh sisa isi bergeser satu petak ke kiri, jadi O(n) per dequeue. "
                "Bandingkan waktunya dengan menu DEQUEUE CIRCULAR.")
    if key == "queue_dequeue_circular":
        return ("Queue circular: ambil dari depan dengan memajukan front",
                "Hanya penunjuk front yang maju satu langkah (modulo kapasitas), tanpa menggeser apa pun. O(1).",
                (("Berapa kali dequeue:", "1", None),), "DEQUEUE", "Isi panjang antrean; coba 1 lalu 100 untuk melihat bedanya.",
                "Tidak ada elemen yang digeser: front maju satu langkah dan berputar ke indeks 0 setelah ujung larik "
                "(modulo). O(1) per dequeue, berapa pun panjang antrean.")
    if key == "sort_insertion":
        return ("Sort: insertion sort",
                "Mengambil tiap elemen lalu menggesernya ke kiri sampai menemukan tempatnya. Di tempat, stabil, O(n kuadrat).",
                (("Jumlah pesanan (dari baris pertama)", "2000", None), ("Kunci", "harga", KUNCI)), "URUTKAN",
                "Coba 2000 lalu 4000: perbandingan jadi sekitar 4x. Lebih dari 20.000 baris ditolak.",
                "Stabil karena syarat geser memakai > (bukan >=): dua pesanan berkunci sama tidak saling melewati. "
                "Data besar dan acak membuatnya kuadratik, karena rata-rata separuh bagian kiri digeser untuk tiap elemen.")
    if key == "sort_merge":
        return ("Sort: merge sort",
                "Membelah data sampai satu elemen, lalu menggabungkan dua bagian terurut. Stabil, O(n log n), kuat untuk 200.000 baris.",
                (("Jumlah pesanan (dari baris pertama)", "4000", None), ("Kunci", "oid", KUNCI)), "URUTKAN",
                "Coba 4000 lalu 8000, lalu 200000 (seluruh data).",
                "Stabil karena penggabungan memakai <= (elemen bagian kiri didahulukan). Kedalaman pembelahan log n dan tiap "
                "tingkat O(n), jadi n dua kali lipat hanya membuat perbandingan sekitar dua kali.")
    if key == "search_linear":
        return ("Search: linear search",
                "Menelusuri dari depan satu per satu sampai ketemu. Data boleh acak, O(n).",
                (("OID yang dicari", "O-137442", None),), "CARI", "Coba O-137442, O-199999, lalu oid yang tidak ada (O-999999).",
                "Jumlah perbandingan = indeks + 1, satu untuk tiap baris yang dilewati. Untuk pencarian sekali dua kali, "
                "ini pilihan yang tepat karena tidak perlu mengurutkan dulu.")
    return ("Search: binary search",
            "Pada daftar terurut oid, tiap perbandingan membuang separuh sisa kemungkinan. O(log n).",
            (("OID yang dicari", "O-137442", None),), "CARI", "Bandingkan jumlah perbandingannya dengan LINEAR SEARCH untuk oid yang sama.",
            "Ongkos yang tidak gratis: daftar terurut oid harus dibangun dulu dengan merge sort (tercatat di COMMAND). "
            "Binary search baru untung bila daftarnya dicari berkali-kali.")
 
 
# ---------------------------------------------------------------- jendela
class Aplikasi:
    def __init__(self, root):
        self.root = root
        root.title("2EZ4U Food Delivery")
        root.geometry("1120x760")
        root.minsize(900, 620)
        self.larik = self.rantai = self.layanan = self.indeks_oid = None
        self.oid_berikut = 200001
        self.tombol, self.aktif, self.vars = [], "", Array()
        self._bangun()
        self.pilih("load")
 
    # ----- tata letak
    def _bangun(self):
        r = self.root
        kepala = tk.Frame(r, bg=BIRU)
        kepala.pack(fill="x")
        tk.Label(kepala, text="2EZ4U Food Delivery", bg=BIRU, fg="white",
                 font=("Segoe UI", 13, "bold"), anchor="w", padx=12, pady=8).pack(fill="x")
 
        bawah = tk.Frame(r)
        bawah.pack(side="bottom", fill="x", padx=8, pady=6)
        self.status = tk.Label(bawah, text="siap", bg=BIRU, fg="white", font=("Courier", 10), padx=10, pady=3)
        self.status.pack(side="left")
        tk.Button(bawah, text="Tutup", command=r.destroy, width=8).pack(side="right")
 
        isi = tk.Frame(r)
        isi.pack(fill="both", expand=True)
        self._menu_kiri(isi)
 
        kanan = tk.Frame(isi, padx=14, pady=8)
        kanan.pack(side="left", fill="both", expand=True)
        self.judul = tk.Label(kanan, font=("Segoe UI", 13, "bold"), anchor="w")
        self.judul.pack(fill="x")
        self.desk = tk.Label(kanan, fg=ABU, font=("Segoe UI", 9), anchor="w", justify="left", wraplength=720)
        self.desk.pack(fill="x", pady=(0, 6))
        self.form = tk.Frame(kanan)
        self.form.pack(fill="x")
        self.hint = tk.Label(kanan, fg=ABU, font=("Segoe UI", 8), anchor="w", justify="left", wraplength=720)
        self.hint.pack(fill="x")
        ttk.Separator(kanan).pack(fill="x", pady=6)
        self.hasil = tk.Label(kanan, font=FONT, anchor="w", justify="left", wraplength=720)
        self.hasil.pack(fill="x")
 
        rangka = tk.Frame(kanan)
        rangka.pack(fill="both", expand=True, pady=6)
        self.tree = ttk.Treeview(rangka, show="headings", height=9)
        gulir = ttk.Scrollbar(rangka, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=gulir.set)
        self.tree.pack(side="left", fill="both", expand=True)
        gulir.pack(side="left", fill="y")
 
        tk.Label(kanan, text="COMMAND", fg=ABU, font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x")
        self.log = tk.Text(kanan, height=5, font=("Courier", 9), state="disabled", relief="solid", bd=1)
        self.log.pack(fill="x", pady=(0, 6))
        self.catatan = tk.Label(kanan, bg=KUNING, fg="#444", font=("Segoe UI", 9), anchor="w",
                                justify="left", wraplength=720, padx=8, pady=6)
        self.catatan.pack(fill="x")
 
    def _menu_kiri(self, induk):
        kiri = tk.Frame(induk)
        kiri.pack(side="left", fill="y")
        kanvas = tk.Canvas(kiri, width=320, highlightthickness=0)
        gulir = ttk.Scrollbar(kiri, orient="vertical", command=kanvas.yview)
        dalam = tk.Frame(kanvas)
        dalam.bind("<Configure>", lambda e: kanvas.configure(scrollregion=kanvas.bbox("all")))
        kanvas.create_window((0, 0), window=dalam, anchor="nw")
        kanvas.configure(yscrollcommand=gulir.set)
        kanvas.pack(side="left", fill="y")
        gulir.pack(side="left", fill="y")
        kanvas.bind("<Enter>", lambda e: kanvas.bind_all(
            "<MouseWheel>", lambda ev: kanvas.yview_scroll(int(-ev.delta / 120), "units")))
        kanvas.bind("<Leave>", lambda e: kanvas.unbind_all("<MouseWheel>"))
        for judul, daftar in MENU:
            tk.Label(dalam, text=judul, fg=ABU, font=("Segoe UI", 8, "bold"),
                     anchor="w").pack(fill="x", padx=6, pady=(8, 2))
            for label, key in daftar:
                b = tk.Button(dalam, text=label, anchor="w", relief="groove", bg="white", font=("Segoe UI", 9),
                              command=lambda k=key: self.pilih(k))
                b.pack(fill="x", padx=6, pady=1)
                self.tombol.append((key, b))
 
    # ----- interaksi
    def pilih(self, key):
        self.aktif = key
        for k, b in self.tombol:
            b.configure(bg=AKTIF if k == key else "white")
        judul, desk, field, teks_tombol, hint, cat = info(key)
        self.judul.configure(text=judul)
        self.desk.configure(text=desk)
        self.hint.configure(text=hint)
        self.catatan.configure(text=cat)
        for w in self.form.winfo_children():
            w.destroy()
        self.vars = Array()
        for k in range(len(field)):
            label, awal, pilihan = field[k]
            var = tk.StringVar(value=awal)
            self.vars.tambah_reguler(var)
            kol = tk.Frame(self.form)
            kol.pack(side="left", padx=(0, 18), anchor="n")
            tk.Label(kol, text=label, font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w")
            if pilihan is None:
                lebar = 60 if key == "load" else 44 if len(field) == 1 else 30
                e = tk.Entry(kol, textvariable=var, width=lebar)
                e.bind("<Return>", lambda ev: self.jalankan())
            else:
                e = ttk.Combobox(kol, textvariable=var, values=pilihan, state="readonly", width=12)
            e.pack(anchor="w")
        tk.Button(self.form, text=teks_tombol, bg=BIRU, fg="white", font=FONT_B, width=14, pady=4,
                  command=self.jalankan).pack(side="left", anchor="s")
        self.tampil("", (), Array())
 
    def jalankan(self):
        self.hasil.configure(text="Memproses...")
        self.root.update_idletasks()
        nilai = Array()
        for i in range(self.vars.ukuran):
            nilai.tambah_reguler(self.vars.lihat(i).get())
        try:
            teks, kolom, baris, modul, cmd, ms = self.aksi(self.aktif, nilai)
        except (ValueError, IndexError, OSError) as e:
            self.tampil("Gagal: " + str(e), (), Array())
            return
        self.tampil(teks, kolom, baris)
        self.catat(cmd, modul, ms)
 
    def tampil(self, teks, kolom, baris):
        self.hasil.configure(text=teks)
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = tuple(kolom)
        lebar = lebar_kolom(kolom)
        for k in range(len(kolom)):
            self.tree.heading(kolom[k], text=kolom[k])
            self.tree.column(kolom[k], width=lebar[k], anchor="w")
        for i in range(baris.ukuran):
            self.tree.insert("", "end", values=baris.lihat(i))
 
    def catat(self, cmd, modul, ms):
        wkt = "%.2f ms" % ms
        self.log.configure(state="normal")
        self.log.insert("1.0", cmd.ljust(30) + "-> " + modul.ljust(22) + wkt + "\n")
        self.log.configure(state="disabled")
        self.status.configure(text="[" + modul + "] " + wkt)
 
    # ----- aksi menu
    def aksi(self, key, nilai):
        n0 = nilai.lihat(0) if nilai.ukuran > 0 else ""
        n1 = nilai.lihat(1) if nilai.ukuran > 1 else ""
        if key == "load":
            return self.a_load(n0)
        if key == "stack_postfix":
            return self.a_postfix(n0)
        if self.layanan is None:
            raise ValueError("Data belum dimuat. Klik menu Load dulu.")
        if key == "stack_undo":
            return self.a_undo_redo(True)
        if key == "stack_redo":
            return self.a_undo_redo(False)
        if key == "queue_enqueue":
            return self.a_enqueue(n0)
        if key == "queue_dequeue_naive":
            return self.a_dequeue(n0, True)
        if key == "queue_dequeue_circular":
            return self.a_dequeue(n0, False)
        if key == "sort_insertion":
            return self.a_sort(n0, n1, False)
        if key == "sort_merge":
            return self.a_sort(n0, n1, True)
        if key == "search_linear":
            return self.a_linear(n0)
        if key == "search_binary":
            return self.a_binary(n0)
        return self.a_m1(key, n0)
 
    def a_load(self, nilai):
        path = nilai.strip() or CSV_DEFAULT
        larik, rantai, layanan = Array(), LinkList(), LayananAntrean()
        t = time.perf_counter()
        n = muat_csv(path, larik, rantai)
        ms = (time.perf_counter() - t) * 1000
        t = time.perf_counter()
        antre = isi_antrean(layanan, larik)
        self.catat("isi_antrean", "M2 - queue", (time.perf_counter() - t) * 1000)
        self.larik, self.rantai, self.layanan, self.oid_berikut, self.indeks_oid = larik, rantai, layanan, n + 1, None
        baris = susun(("baris dimuat", ribu(n)),
                      ("array: ukuran / kapasitas", ribu(larik.ukuran) + " / " + ribu(larik.kapasitas)),
                      ("linked list: jumlah simpul", ribu(rantai.ukuran)),
                      ("pesanan ANTRE masuk ke kedua antrean", ribu(antre)),
                      ("antrean circular: kapasitas", ribu(layanan.melingkar.K)))
        return ("Data dimuat dari " + path + ".", ("keterangan", "nilai"), baris, "M1 - Tarik", "load", ms)
 
    def pesanan_baru(self, nama, prioritas):
        oid = "O-" + ("000000" + str(self.oid_berikut))[-6:]
        self.oid_berikut += 1
        lt = time.localtime()
        return Pesanan(oid, nama, "kafe-teknik", "roti-bakar", 12000, prioritas,
                       lt.tm_hour * 3600 + lt.tm_min * 60 + lt.tm_sec, None, "ANTRE")
 
    # ---- M1
    def a_m1(self, key, nilai):
        arr = key.startswith("array")
        s, nama, modul, pre = (self.larik, "Array", "M1 - Array", "array") if arr else \
                              (self.rantai, "Linked list", "M1 - LinkedList", "linkedlist")
        n = s.ukuran
        if key.endswith("_lihat"):
            i = bulat(nilai)
            t = time.perf_counter()
            p = s.lihat(i)
            ms = (time.perf_counter() - t) * 1000
            cara = "langsung ke data[i]" if arr else "melangkah " + ribu(i) + " kali dari head"
            return ("Pesanan ke-" + str(i) + " dari " + nama + " (" + cara + ").",
                    ("kolom", "isi"), detail(p), modul, pre + "_get", ms)
        self.indeks_oid = None                                   # isi berubah -> daftar terurut oid harus dibangun ulang
        if key.endswith("_hapus"):
            i = bulat(nilai)
            t = time.perf_counter()
            p = s.hapus(i)
            ms = (time.perf_counter() - t) * 1000
            self.layanan.catat_hapus(s, i, p, nama)
            cara = ("menggeser " + ribu(n - 1 - i) + " elemen ke kiri") if arr else \
                   ("menelusuri " + ribu(i) + " simpul")
            return (p.oid + " dicabut dari " + nama + " (" + cara + ").\nPanjang " + nama + " sekarang " + ribu(s.ukuran) + ".",
                    ("kolom", "isi"), detail(p), modul, pre + "_delete", ms)
        jenis = key[key.index("_") + 1:]                         # reguler / prioritas / vip
        prio = 3 if jenis == "reguler" else 2 if jenis == "prioritas" else 1
        idx = n if jenis == "reguler" else n // 2 if jenis == "prioritas" else 0
        p = self.pesanan_baru(nilai.strip() or "Pelanggan Baru", prio)
        t = time.perf_counter()
        getattr(s, "tambah_" + jenis)(p)
        ms = (time.perf_counter() - t) * 1000
        self.layanan.catat_order(s, jenis, idx, p, nama)
        if arr:
            cara = "menggeser " + ribu(n - idx) + " elemen ke kanan"
        else:
            cara = ("lewat tail, tanpa menelusuri" if jenis == "reguler" else
                    "menelusuri " + ribu(idx - 1) + " simpul" if jenis == "prioritas" else
                    "hanya mengubah head")
        return (p.oid + " masuk di indeks " + ribu(idx) + " pada " + nama + " (" + cara + ").\nPanjang sekarang: array " +
                ribu(self.larik.ukuran) + ", linked list " + ribu(self.rantai.ukuran) + ".",
                ("kolom", "isi"), detail(p), modul, pre + "_add_" + jenis, ms)
 
    # ---- M2
    def a_postfix(self, nilai):
        teks = nilai.strip()
        if teks == "":
            raise ValueError("Isi struk belanja dulu.")
        j1, j2 = Array(), Array()
        t = time.perf_counter()
        pf = ke_postfix(teks, j1)
        total = hitung(pf, j2)
        ms = (time.perf_counter() - t) * 1000
        baris = Array()
        for k in range(j1.ukuran):
            tok, aksi, st, out = j1.lihat(k)
            baris.tambah_reguler(("1." + ("akhir" if tok == "akhir" else str(k + 1)), tok, aksi, st, out))
        for k in range(j2.ukuran):
            tok, aksi, st, out = j2.lihat(k)
            baris.tambah_reguler(("2." + str(k + 1), tok, aksi, st, out))
        return ("Struk : " + teks + "\nPostfix: " + pf + "\nTOTAL : Rp " + rupiah(total),
                ("langkah", "token", "tindakan", "stack", "output"), baris, "M2 - stack", "stack_postfix", ms)
 
    def _panjang(self):
        L = self.layanan
        return ("Panjang antrean sekarang: naif " + ribu(L.naif.panjang()) + ", circular " + ribu(L.melingkar.panjang()) +
                "; tumpukan undo " + str(L.undo.panjang()) + " catatan, redo " + str(L.redo.panjang()) + ".")
 
    def a_undo_redo(self, undo):
        L = self.layanan
        t = time.perf_counter()
        aksi = L.undo_last() if undo else L.redo_last()
        ms = (time.perf_counter() - t) * 1000
        kata = "undo" if undo else "redo"
        if aksi is None:
            return ("Tumpukan " + kata + " kosong, tidak ada yang " + ("dibatalkan." if undo else "diulang."),
                    (), Array(), "M2 - stack", "stack_" + kata, ms)
        jenis, data, versi = aksi
        awal = "Pembatalan " if undo else "Pengulangan "
        if jenis == "ENQUEUE":
            teks = awal + "enqueue: " + data.oid + (" dikeluarkan lagi dari belakang kedua antrean." if undo
                                                    else " masuk lagi ke belakang kedua antrean.")
            baris = tabel_pesanan(susun(data), False)
        elif jenis == "DEQUEUE":
            k = str(data.ukuran)
            teks = awal + "dequeue x" + k + ": " + k + (" pesanan dikembalikan ke DEPAN antrean " if undo
                                                         else " pesanan keluar lagi dari antrean ") + versi + "."
            baris = tabel_pesanan(data, False)
        else:                                                    # ORDER / HAPUS: data = (struktur, jenis, indeks, pesanan)
            self.indeks_oid = None
            dicabut = (jenis == "ORDER") == undo                 # ORDER di-undo atau HAPUS di-redo -> dicabut
            teks = awal + jenis.lower() + ": " + data[3].oid + (" dicabut dari " if dicabut else " dikembalikan ke ") + \
                   versi + " (indeks " + ribu(data[2]) + ")."
            baris = tabel_pesanan(susun(data[3]), False)
        return (teks + "\n" + self._panjang(), KOLOM_P, baris, "M2 - stack", "stack_" + kata, ms)
 
    def a_enqueue(self, nilai):
        p = self.pesanan_baru(nilai.strip() or "Pelanggan Baru", 3)
        t = time.perf_counter()
        self.layanan.enqueue(p)
        ms = (time.perf_counter() - t) * 1000
        return (p.oid + " masuk ke barisan paling belakang pada KEDUA antrean.\n" + self._panjang(),
                ("kolom", "isi"), detail(p), "M2 - queue", "queue_enqueue", ms)
 
    def a_dequeue(self, nilai, naif):
        n, L = bulat(nilai, 1), self.layanan
        antre = L.naif if naif else L.melingkar
        nama = "naif" if naif else "circular"
        modul, cmd = "M2 - queue " + nama, "queue_dequeue_" + ("naive" if naif else "circular")
        g0 = antre.total_geser
        t = time.perf_counter()
        daftar = (L.dequeue_naif if naif else L.dequeue_melingkar)(n)
        ms = (time.perf_counter() - t) * 1000
        k = daftar.ukuran
        if k == 0:
            return ("Antrean " + nama + " kosong.", (), Array(), modul, cmd, ms)
        if naif:
            geser = antre.total_geser - g0
            rinci = "Total " + ribu(geser) + " elemen digeser, rata-rata " + ribu(geser // k) + " geseran per dequeue."
        else:
            rinci = "Tidak ada elemen yang digeser, hanya front yang maju ke " + ribu(antre.front) + \
                    " (rear " + ribu(antre.rear) + ", kapasitas " + ribu(antre.K) + ")."
        return (str(k) + " pesanan keluar dari depan antrean " + nama + ".\n" + rinci + "\nSisa antrean " + nama +
                " " + ribu(antre.panjang()) + ".", KOLOM_PJ, tabel_pesanan(daftar, True), modul, cmd, ms)
 
    # ---- M3
    def a_sort(self, jumlah, kunci, merge):
        n = bulat(jumlah, 1)
        kunci = kunci or "harga"
        A, c = salin(self.larik, n), Pencacah()
        nama, modul, cmd = ("merge sort", "M3 - merge sort", "merge_sort") if merge else \
                           ("insertion sort", "M3 - insertion sort", "insertion_sort")
        t = time.perf_counter()
        (merge_sort if merge else insertion_sort)(A, kunci, c)
        ms = (time.perf_counter() - t) * 1000
        teks = ribu(A.ukuran) + " pesanan terurut menurut " + kunci + " (" + nama + ")\n" + \
               ribu(c.banding) + " perbandingan | " + ribu(c.pindah) + " pemindahan | " + \
               ("terbukti terurut" if terurut(A, kunci) else "BELUM TERURUT")
        return (teks, KOLOM_S, tabel_sort(A), modul, cmd + " " + str(A.ukuran) + " " + kunci, ms)
 
    def a_linear(self, nilai):
        target = nilai.strip()
        if target == "":
            raise ValueError("Isi oid yang dicari, contoh O-137442.")
        c = Pencacah()
        t = time.perf_counter()
        i = linear_search(self.larik, target, "oid", c)
        ms = (time.perf_counter() - t) * 1000
        modul, cmd = "M3 - linear", "linear_search " + target
        if i < 0:
            return (target + " tidak ditemukan | " + ribu(c.banding) + " perbandingan (seluruh baris dilewati)",
                    (), Array(), modul, cmd, ms)
        return (target + " ditemukan di indeks " + ribu(i) + " | " + ribu(c.banding) + " perbandingan",
                ("kolom", "isi"), detail(self.larik.lihat(i)), modul, cmd, ms)
 
    def a_binary(self, nilai):
        target = nilai.strip()
        if target == "":
            raise ValueError("Isi oid yang dicari, contoh O-137442.")
        awal = "Memakai daftar terurut oid yang sudah dibangun.\n"
        if self.indeks_oid is None:                              # dibangun SEKALI, ongkosnya dicatat terang-terangan
            t = time.perf_counter()
            idx = salin(self.larik)
            merge_sort(idx, "oid")
            ms_b = (time.perf_counter() - t) * 1000
            self.indeks_oid = idx
            awal = "Daftar terurut oid dibangun sekali (merge sort): %.2f ms\n" % ms_b
            self.catat("bangun_indeks_oid", "M3 - merge sort", ms_b)
        c = Pencacah()
        t = time.perf_counter()
        i = binary_search(self.indeks_oid, target, "oid", c)
        ms = (time.perf_counter() - t) * 1000
        modul, cmd = "M3 - binary", "binary_search " + target
        if i < 0:
            return (awal + target + " tidak ditemukan | " + ribu(c.banding) + " perbandingan",
                    (), Array(), modul, cmd, ms)
        return (awal + target + " ditemukan di baris " + ribu(i + 1) + " | " + ribu(c.banding) + " perbandingan",
                ("kolom", "isi"), detail(self.indeks_oid.lihat(i)), modul, cmd, ms)