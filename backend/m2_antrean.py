"""backend/m2_antrean.py - M2: Tumpukan, kasir postfix, antrean naif vs melingkar, undo/redo"""
try:
    from .m1_pesanan import Array, Node
except ImportError:                              
    from m1_pesanan import Array, Node
 
 
class Tumpukan:                                  
    def __init__(self): self.larik = Array()
    def push(self, x): self.larik.tambah_reguler(x)
    def kosong(self): return self.larik.ukuran == 0
    def panjang(self): return self.larik.ukuran
    def kosongkan(self): self.larik = Array()
 
    def peek(self):
        if self.kosong():
            raise IndexError("Tumpukan kosong")
        return self.larik.lihat(self.larik.ukuran - 1)
 
    def pop(self):
        x = self.peek()
        self.larik.hapus(self.larik.ukuran - 1)  # ambil dari ujung, tanpa geser
        return x
 
 
# kasir
def angka(t): return "0" <= t[0] <= "9" or t[0] == "."
def kuat(op): return 2 if op in "*/" else 1 if op in "+-" else 0    # "(" = 0
 
 
def gabung(larik, kosong=""):                    
    s = ""
    for i in range(larik.ukuran):
        s = s + ("" if i == 0 else " ") + str(larik.lihat(i))
    return s if larik.ukuran > 0 else kosong
 
 
def pecah_token(teks):
    """'( 3*12000 )' -> ( 3 * 12000 ) ; angka berdigit banyak = 1 token."""
    hasil, i = Array(), 0
    while i < len(teks):
        c = teks[i]
        if c == " ":
            i += 1
        elif angka(c):
            j = i
            while j < len(teks) and angka(teks[j]):
                j += 1
            hasil.tambah_reguler(teks[i:j])
            i = j
        elif c in "+-*/()":
            hasil.tambah_reguler(c)
            i += 1
        else:
            raise ValueError("Karakter tidak dikenal: " + c)
    return hasil
 
 
def ke_postfix(ekspresi, jejak=None):
    """Return teks postfix. 'jejak' (Array, opsional) diisi tuple (token, tindakan, stack, output)."""
    token, st, keluar = pecah_token(ekspresi), Tumpukan(), Array()
    for k in range(token.ukuran):
        t = token.lihat(k)
        if angka(t):
            keluar.tambah_reguler(t)
            aksi = "operand, langsung ke output"
        elif t == "(":
            st.push(t)
            aksi = "push ( ke stack"
        elif t == ")":
            while not st.kosong() and st.peek() != "(":
                keluar.tambah_reguler(st.pop())
            if st.kosong():
                raise ValueError("Tanda kurung tidak seimbang")
            st.pop()                             
            aksi = "pop sampai (, lalu buang ("
        else:                                    
            aksi = ""
            while not st.kosong() and kuat(st.peek()) >= kuat(t):
                op = st.pop()
                keluar.tambah_reguler(op)
                aksi = aksi + "pop " + op + ", lalu "
            st.push(t)
            aksi = aksi + "push " + t
        if jejak is not None:
            jejak.tambah_reguler((t, aksi, gabung(st.larik, "kosong"), gabung(keluar, "kosong")))
    sisa = ""
    while not st.kosong():                       
        op = st.pop()
        if op == "(":
            raise ValueError("Tanda kurung tidak seimbang")
        keluar.tambah_reguler(op)
        sisa = sisa + op + " "
    if jejak is not None:
        aksi = "pop sisa stack: " + sisa.strip() if sisa != "" else "stack sudah kosong"
        jejak.tambah_reguler(("akhir", aksi, "kosong", gabung(keluar, "kosong")))
    return gabung(keluar)
 
 
def hitung(postfix, jejak=None):
    """Evaluasi postfix dengan tumpukan angka. Return total."""
    token, st = pecah_token(postfix), Tumpukan()
    for k in range(token.ukuran):
        t = token.lihat(k)
        if angka(t):
            st.push(float(t) if "." in t else int(t))
            aksi = "operand, push " + t
        else:
            if st.panjang() < 2:
                raise ValueError("Ekspresi tidak valid")
            b = st.pop()                         # operand KANAN keluar lebih dulu
            a = st.pop()
            if t == "+": r = a + b
            elif t == "-": r = a - b
            elif t == "*": r = a * b
            elif t == "/":
                if b == 0:
                    raise ValueError("Pembagian dengan nol")
                r = a / b
            else:
                raise ValueError("Operator tidak dikenal: " + t)
            st.push(r)
            aksi = "pop " + str(b) + " dan " + str(a) + " -> " + str(a) + t + str(b) + " = " + str(r)
        if jejak is not None:
            jejak.tambah_reguler((t, aksi, gabung(st.larik), str(st.peek())))
    if st.panjang() != 1:
        raise ValueError("Ekspresi tidak valid")
    return st.pop()
 
 
# antrean
class AntreanNaif:                               
    def __init__(self):
        self.larik = Array()
        self.total_geser = 0
 
    def enqueue(self, x): self.larik.tambah_reguler(x)
    def masuk_depan(self, x): self.larik.sisip(0, x)        
    def panjang(self): return self.larik.ukuran
    def lihat(self, i): return self.larik.lihat(i)
 
    def dequeue(self):
        if self.larik.ukuran == 0:
            return None
        self.total_geser += self.larik.ukuran - 1
        return self.larik.hapus(0)
 
    def keluar_belakang(self):                               
        if self.larik.ukuran == 0:
            return None
        return self.larik.hapus(self.larik.ukuran - 1)
 
 
class AntreanMelingkar:
    """front/rear berputar dengan modulo, dequeue cukup memajukan front: O(1).
    count membedakan kosong dan penuh (keduanya front == rear). Penuh -> kapasitas tumbuh 2x."""
 
    def __init__(self, K=4):
        self.K, self.data = K, [None] * K
        self.front = self.rear = self.count = 0
        self.total_geser = 0                                 
 
    def panjang(self): return self.count
    def lihat(self, i): return self.data[(self.front + i) % self.K]
 
    def _tumbuh(self):
        baru = [None] * (self.K * 2)
        for i in range(self.count):                          
            baru[i] = self.data[(self.front + i) % self.K]
        self.data, self.front, self.rear, self.K = baru, 0, self.count, self.K * 2
 
    def enqueue(self, x):
        if self.count == self.K:
            self._tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.K
        self.count += 1
 
    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.K
        self.count -= 1
        return x
 
    def masuk_depan(self, x):
        if self.count == self.K:
            self._tumbuh()
        self.front = (self.front - 1) % self.K
        self.data[self.front] = x
        self.count += 1
 
    def keluar_belakang(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1) % self.K
        x, self.data[self.rear] = self.data[self.rear], None
        self.count -= 1
        return x
 
 
# undo / redo
def _sisip_di(struktur, i, pesanan):
    """Sisipkan pesanan di indeks i pada Array maupun LinkList milik M1
    (LinkList M1 tidak punya sisip di indeks bebas, jadi bagian tengah disambung di sini)."""
    if i == 0:
        struktur.tambah_vip(pesanan)
    elif i == struktur.ukuran:
        struktur.tambah_reguler(pesanan)
    elif hasattr(struktur, "sisip"):                         
        struktur.sisip(i, pesanan)
    else:                                                    
        sebelum = struktur.head
        for _ in range(i - 1):
            sebelum = sebelum.next
        n = Node(pesanan)
        n.next = sebelum.next
        sebelum.next = n
        struktur.ukuran += 1
 
 
class LayananAntrean:
    """Catatan undo = tuple (jenis, data, versi):
       ("ENQUEUE", pesanan, None)          undo: keluarkan dari BELAKANG kedua antrean
       ("DEQUEUE", Array pesanan, versi)   undo: kembalikan semuanya ke DEPAN antrean itu
       ("ORDER", (struktur, jenis, i, pesanan), nama)   M1 menambah pesanan
                                           undo: hapus(i) dari struktur, redo: sisipkan lagi di i
       ("HAPUS", (struktur, None, i, pesanan), nama)    M1 menghapus pesanan
                                           undo: sisipkan lagi di i, redo: hapus(i)
       Semua perubahan M1 dicatat, jadi undo selalu berurutan (LIFO) dan indeksnya tidak meleset."""
 
    def __init__(self):
        self.naif, self.melingkar = AntreanNaif(), AntreanMelingkar()
        self.undo, self.redo = Tumpukan(), Tumpukan()
 
    def _catat(self, aksi):                      
        self.undo.push(aksi)
        self.redo.kosongkan()
 
    def catat_order(self, struktur, jenis, indeks, pesanan, nama):
        """Dipanggil setelah M1 menambah pesanan. jenis: reguler / prioritas / vip."""
        self._catat(("ORDER", (struktur, jenis, indeks, pesanan), nama))
 
    def catat_hapus(self, struktur, indeks, pesanan, nama):
        """Dipanggil setelah M1 menghapus pesanan dari indeks tersebut."""
        self._catat(("HAPUS", (struktur, None, indeks, pesanan), nama))
 
    def enqueue(self, pesanan):                  
        self.naif.enqueue(pesanan)
        self.melingkar.enqueue(pesanan)
        self._catat(("ENQUEUE", pesanan, None))
 
    def _dequeue(self, antrean, versi, n):
        daftar = Array()
        for _ in range(n):
            x = antrean.dequeue()
            if x is None:
                break
            daftar.tambah_reguler(x)
        if daftar.ukuran > 0:
            self._catat(("DEQUEUE", daftar, versi))
        return daftar
 
    def dequeue_naif(self, n=1): return self._dequeue(self.naif, "naif", n)
    def dequeue_melingkar(self, n=1): return self._dequeue(self.melingkar, "melingkar", n)
 
    def undo_last(self):
        if self.undo.kosong():
            return None
        aksi = self.undo.pop()
        jenis, data, versi = aksi
        if jenis == "ENQUEUE":
            self.naif.keluar_belakang()
            self.melingkar.keluar_belakang()
        elif jenis == "ORDER":
            data[0].hapus(data[2])
        elif jenis == "HAPUS":
            _sisip_di(data[0], data[2], data[3])
        else:
            antrean = self.naif if versi == "naif" else self.melingkar
            for i in range(data.ukuran - 1, -1, -1):         
                antrean.masuk_depan(data.lihat(i))
        self.redo.push(aksi)
        return aksi
 
    def redo_last(self):
        if self.redo.kosong():
            return None
        aksi = self.redo.pop()
        jenis, data, versi = aksi
        if jenis == "ENQUEUE":                   
            self.naif.enqueue(data)
            self.melingkar.enqueue(data)
        elif jenis == "ORDER":                   
            _sisip_di(data[0], data[2], data[3])
        elif jenis == "HAPUS":
            data[0].hapus(data[2])
        else:
            antrean = self.naif if versi == "naif" else self.melingkar
            for _ in range(data.ukuran):
                antrean.dequeue()
        self.undo.push(aksi)                     
        return aksi
 
    def history(self):
        """Array teks aksi, dari terlama ke terbaru (= isi tumpukan undo)."""
        hasil = Array()
        for i in range(self.undo.panjang()):
            jenis, data, versi = self.undo.larik.lihat(i)
            if jenis == "ENQUEUE":
                hasil.tambah_reguler("ENQUEUE " + data.oid)
            elif jenis == "DEQUEUE":
                hasil.tambah_reguler("DEQUEUE x" + str(data.ukuran) + " (" + versi + ")")
            else:
                hasil.tambah_reguler(jenis + " " + data[3].oid + " (" + versi + ")")
        return hasil
 
    def stats(self):
        """(len naif, len melingkar, kapasitas naif, kapasitas melingkar,
            total geser naif, total geser melingkar, undo depth, redo depth)"""
        return (self.naif.panjang(), self.melingkar.panjang(),
                self.naif.larik.kapasitas, self.melingkar.K,
                self.naif.total_geser, self.melingkar.total_geser,
                self.undo.panjang(), self.redo.panjang())
 
 
def isi_antrean(layanan, semua):
    """Masukkan pesanan berstatus ANTRE dari Array 'semua' ke KEDUA antrean
    (tanpa dicatat undo). Return jumlahnya."""
    jumlah = 0
    for i in range(semua.ukuran):
        p = semua.lihat(i)
        if p.status == "ANTRE":
            layanan.naif.enqueue(p)
            layanan.melingkar.enqueue(p)
            jumlah += 1
    return jumlah