# 🚌 TransJogja Navigator

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/Algorithm-Dijkstra-10b981.svg" alt="Dijkstra">
</div>

<br>

**TransJogja Navigator** adalah sebuah aplikasi web interaktif berbasis algoritma *Dijkstra* yang dirancang untuk mencari rute bus terpendek di Yogyakarta. Sistem ini dibangun dengan antarmuka yang modern, responsif, serta dilengkapi dengan sistem Multi-Role (*Role-Based Access Control*) untuk membedakan fungsi administratif dan pencarian rute publik.

---

## ✨ Fitur Utama

### 👤 Akses Pengguna (Publik)
Fokus pada navigasi, pencarian arah, dan panduan perjalanan.
- **🗺️ Cari Rute Terpendek**: Menemukan jalur bus paling efisien dari titik awal ke tujuan menggunakan teori graf terbobot (Dijkstra) dan formula jarak *Haversine*.
- **📍 Peta Fasilitas Halte**: Eksplorasi interaktif seluruh titik tunggu TransJogja (dilengkapi integrasi GPS untuk melacak lokasi pengguna dengan `streamlit-geolocation`).
- **🚌 Informasi Bus & Koridor**: Katalog visual operasional koridor, jam kerja, dan rentang interval kedatangan bus di Yogyakarta.

### 🛡️ Akses Administrator (Control Panel)
Fokus pada pengelolaan dan pemantauan sistem manajemen data bus.
- **Dashboard Statistik**: Memperlihatkan secara *real-time* jumlah halte aktif, koridor beroperasi, serta struktur node KML (titik lintang & bujur).
- **CRUD (Create, Read, Update, Delete)**: Modul untuk menambah, mengubah, menonaktifkan, atau menghapus data rute bus dan halte melalui panel kontrol khusus.

---

## 🛠️ Teknologi & *Library* yang Digunakan

| Komponen | Teknologi Utama |
| --- | --- |
| **Frontend UI / Backend** | [Streamlit](https://streamlit.io/) (Framework Web Python) |
| **Algoritma Graf** | `networkx` (Pemrosesan Dijkstra) |
| **Formula Spasial** | `haversine` (Perhitungan jarak koordinat bumi melengkung) |
| **Visualisasi Peta Interaktif** | `folium` & `streamlit-folium` |
| **Parser Geografis** | `beautifulsoup4` (BSS4 kml parser) |
| **Penyimpanan Data** | JSON (*Lightweight Document Store*) |

---

## 🚀 Panduan Instalasi (Untuk Development Lokal)

Ikuti langkah-langkah di bawah ini untuk menjalankan aplikasi di mesin lokal Anda:

1. **Clone repositori ini:**
   ```bash
   git clone https://github.com/SonnyRilman/transroute.git
   cd transroute
   ```

2. **Buat Virtual Environment (opsional namun disarankan):**
   ```bash
   python -m venv venv
   # Jika menggunakan Windows:
   venv\Scripts\activate
   # Jika menggunakan MacOS/Linux:
   source venv/bin/activate
   ```

3. **Install *dependencies* yang dibutuhkan:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Aplikasi:**
   ```bash
   streamlit run app.py
   ```
   *Dashboard akan terbuka secara otomatis di browser pada `http://localhost:8501`*

---

## 🔐 Kredensial Login

Saat Anda pertama kali masuk, Anda akan diminta melewati gerbang autentikasi web:

**Sebagai Administrator:**
- **Username:** `admin`
- **Password:** `admin123`

**Sebagai Pengguna Umum (Warga/Pengunjung):**
- **Nama:** *(Isi dengan bebas, contoh: Sonny)*
- **Password (PIN):** `user123`

---

## 📂 Struktur Direktori

```text
transroute/
├── app.py                     # Entry point (Main Application & Login Gate)
├── data/                      # Folder penyimpan basis data lokal
│   ├── halte_info.json        # Struktur simpanan data Halte
│   ├── koridor.json           # Struktur simpanan rute Koridor
│   └── sample_route.kml       # Format XML Geografis Node Graf Bus
├── pages/                     # Sistem Multi-Page Navigation Streamlit
│   ├── Admin.py               # Panel CRUD Administrator
│   ├── Bus_Koridor.py         # Tabulasi info operasional bus
│   ├── Cari_Rute.py           # Core Engine: Pencarian rute dengan Dijkstra
│   └── Peta_Halte.py          # Visualisasi titik GPS Folium
├── utils/                     # Kode-kode pembantu (Utilities)
│   ├── auth.py                # Konfigurasi keamanan dan kustom side-nav
│   ├── graph_logic.py         # Otak algoritma NetworkX & Dijkstra
│   ├── kml_parser.py          # Parser KML (garis lintang/bujur) via BS4
│   └── styles.py              # Injeksi CSS / Dark Mode Premium
├── requirements.txt           # Library dependensi Python
└── README.md                  # Dokumentasi proyek (file ini)
```

---

*Dikembangkan untuk eksperimen studi rute TransJogja berbasis algoritma Dijkstra dan integrasi UI asinkron.*
