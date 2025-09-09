# Arabic Morfology

Aplikasi web untuk analisis morfologi bahasa Arab yang dibangun menggunakan React.js untuk frontend dan Flask Python untuk backend.

## 🚀 Teknologi yang Digunakan

- **Frontend**: React.js
- **Backend**: Flask (Python)
- **Package Manager**: npm

## 📋 Prasyarat

Pastikan sistem Anda sudah terinstall:

- **Node.js** (versi terbaru)
- **Python** (versi 3.x)
- **npm** (biasanya sudah termasuk dengan Node.js)

### Download Links:
- Node.js: [https://nodejs.org/en/download/](https://nodejs.org/en/download/)
- Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)

## 🛠️ Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/ridhogithub1/arabic-morfology.git
cd arabic-morfology
```

### 2. Verifikasi Instalasi

Pastikan Node.js dan Python sudah terinstall dengan benar:

```bash
node -v
python --version
```

Jika kedua perintah di atas menampilkan versi, maka Anda siap melanjutkan.

## 🚀 Menjalankan Aplikasi

### Langkah-langkah:

1. **Buka terminal** di direktori proyek

2. **Jalankan backend** (Flask server):
   ```bash
   python app.py
   ```

3. **Jalankan frontend** (React development server):
   ```bash
   npm run dev
   ```

### 📝 Catatan Penting:

- Pastikan kedua server (Flask dan React) berjalan bersamaan
- Backend Flask biasanya berjalan di port 5000
- Frontend React development server biasanya berjalan di port 3000
- Buka browser dan akses aplikasi di alamat yang ditampilkan di terminal (biasanya `http://localhost:3000`)

## 📁 Struktur Proyek

```
arabic-morfology/
├── frontend/          # React.js aplikasi
├── backend/           # Flask API
├── app.py            # Main Flask application
├── package.json      # npm dependencies
└── README.md         # Dokumentasi ini
```

## 🔧 Troubleshooting

### Jika terjadi error:

1. **Node.js tidak ditemukan**: 
   - Download dan install Node.js dari link yang disediakan di atas

2. **Python tidak ditemukan**:
   - Download dan install Python dari link resmi

3. **Port sudah digunakan**:
   - Pastikan tidak ada aplikasi lain yang menggunakan port yang sama
   - Restart terminal dan coba lagi

4. **Dependencies error**:
   - Jalankan `npm install` untuk menginstall dependencies Node.js
   - Untuk Python dependencies, jalankan `pip install -r requirements.txt` (jika ada file requirements.txt)

## 🤝 Kontribusi

Jika Anda ingin berkontribusi pada proyek ini:

1. Fork repository
2. Buat branch fitur baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📞 Kontak

Jika ada pertanyaan atau masalah, silakan buka issue di repository ini atau hubungi maintainer.

## 📄 Lisensi

[Tambahkan informasi lisensi sesuai kebutuhan]

---

**Selamat menggunakan Arabic Morfology! 🎉**
