# 📚 EduTest SMA — Pre-Post Test Platform

Website pre-post test berbasis Flask untuk siswa SMA dengan UI bergradasi kuning.

## ✨ Fitur

- **Autentikasi**: Login/Register siswa, akun Admin terpisah
- **Alur Belajar**: Pre-Test → Materi → Post-Test
- **Materi**: Video (YouTube), Teks/HTML, Audio (MP3)
- **Admin Dashboard**: Kelola soal, materi, lihat hasil, export CSV
- **UI Modern**: Gradasi kuning emas, responsif

## 📂 Struktur Folder

```
prepost-test/
├── app.py                  ← Aplikasi utama Flask
├── requirements.txt        ← Dependencies Python
├── vercel.json             ← Konfigurasi Vercel
├── api/
│   └── index.py            ← Entry point Vercel
├── templates/
│   ├── base.html           ← Template dasar (navbar, dll)
│   ├── login.html          ← Halaman login
│   ├── register.html       ← Halaman registrasi siswa
│   ├── dashboard.html      ← Dashboard siswa
│   ├── test.html           ← Halaman pre/post test
│   ├── result.html         ← Halaman hasil test
│   ├── materi.html         ← Halaman materi pembelajaran
│   └── admin/
│       ├── base.html       ← Template dasar admin
│       ├── dashboard.html  ← Dashboard admin
│       ├── siswa.html      ← Manajemen siswa
│       ├── hasil.html      ← Analisis hasil test
│       ├── soal.html       ← Manajemen soal
│       └── materi.html     ← Manajemen materi
└── instance/
    └── prepost.db          ← Database SQLite (auto-generated)
```

## 🚀 Menjalankan Secara Lokal

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Jalankan server
python app.py

# 3. Buka browser
# http://localhost:5000
```

## 🔑 Akun Default

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |

Siswa harus registrasi sendiri via `/register`

## ☁️ Deploy ke Vercel (Gratis)

### Metode 1: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login Vercel
vercel login

# Deploy
vercel --prod
```

### Metode 2: GitHub + Vercel Dashboard

1. Push project ke GitHub
2. Buka [vercel.com](https://vercel.com) → Import Project
3. Pilih repository
4. Tambahkan **Environment Variables**:
   - `SECRET_KEY` → string acak panjang
   - `DATABASE_URL` → (opsional, default SQLite)
5. Klik Deploy ✅

### ⚠️ Catatan Database untuk Vercel

Vercel adalah **serverless** — SQLite tidak persisten antar deploy. Untuk production:

**Opsi gratis:**
- [Neon.tech](https://neon.tech) — PostgreSQL gratis
- [PlanetScale](https://planetscale.com) — MySQL gratis
- [Supabase](https://supabase.com) — PostgreSQL + Auth gratis

**Cara pakai Neon (rekomendasi):**
1. Daftar di neon.tech, buat database
2. Copy connection string: `postgresql://user:pass@host/db`
3. Set environment variable `DATABASE_URL` di Vercel
4. Install: `pip install psycopg2-binary` (tambah ke requirements.txt)

## 📊 Alur Penggunaan Siswa

```
Registrasi → Login → Pre-Test (5 soal, 20 menit)
          → Lihat Nilai Pre-Test
          → Materi (Video + Teks + Audio)
          → Post-Test (5 soal, 20 menit)
          → Lihat Nilai Post-Test + Perbandingan
```

## 👨‍💼 Fitur Admin

- 📊 Dashboard statistik (rata-rata nilai, jumlah peserta)
- 👥 Manajemen siswa (reset/hapus data)
- 📈 Analisis hasil pre-post test + filter
- 📝 CRUD soal pre-test & post-test
- 📚 CRUD materi pembelajaran
- 💾 Export hasil ke CSV

## 🎨 UI Design

- Tema: Kuning emas (#FFD700) gradasi ke oranye (#FFA500)
- Background gelap (#1A1200) untuk kontras elegan
- Font: Playfair Display (heading) + DM Sans (body)
- Responsif untuk mobile dan desktop