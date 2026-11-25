# GitHub Release Tracker

Aplikasi Windows portable berukuran kecil untuk memantau release terbaru dari proyek yang Anda ikuti (GitHub, GitLab, Codeberg, Gitea / Forgejo, dan server self-hosted), dan memberi tahu kalau ada release baru. Tanpa akun, tanpa login, dan tanpa token.

🇬🇧 [Read in English](README.md)

<!-- Tambahkan screenshot Anda sendiri di sini, misalnya simpan sebagai docs/screenshot.png lalu pakai:
![Screenshot](docs/screenshot.png)
-->

## Fitur

- Tambah proyek dengan menempel URL GitHub atau `owner/repo`
- **Host lain, caranya sama.** Tempel URL proyek di **GitLab** (`gitlab.com` atau server sendiri, termasuk grup dan subgrup), **Codeberg**, **Gitea**, **Forgejo**, atau server self-hosted dari semuanya. Hanya repo publik, tanpa token. Hanya **rilis resmi** yang dipantau: proyek yang hanya punya tag (atau belum punya apa-apa) ditolak saat ditambahkan
- Lihat nama proyek, repository, release saat ini, tanggal rilis, dan status sekilas
- **Check for updates** menyegarkan semua proyek; proyek dengan release lebih baru disorot sebagai `Update available: v1.0 -> v1.1`
- **Mark as seen** menghapus sorotan setelah Anda selesai menangani update
- Klik dua kali pada proyek untuk membuka halaman release-nya di browser (klik dua kali pada nama di kolom **Project** akan me-rename)
- **Ganti nama proyek** agar mudah dibaca: arahkan kursor ke baris lalu klik pensil (atau klik dua kali pada nama, tekan **F2**, atau klik kanan > Rename). *Reset name* mengembalikan nama dari GitHub. Nama buatan Anda tersimpan dan ikut di Export
- Klik header **Project**, **Repository**, **Source**, **Published**, atau **Status** untuk mengurutkan (klik lagi untuk membalik; panah menunjukkan arahnya)
- Kolom **Source** menunjukkan asal tiap proyek (GitHub, GitLab, Codeberg, atau alamat server Anda sendiri); klik headernya untuk mengurutkan. Kotak pencarian juga mencocokkannya.
- **Filter** daftar: ketik di kotak pencarian (Ctrl+F untuk pindah ke sana, Esc untuk mengosongkan) agar hanya proyek yang namanya atau repositorinya memuat semua kata yang diketik yang tampil, dan/atau pilih *Show:* All projects / ★ Favorites / Updates available / Errors / Up to date / No releases. Ini hanya mengubah tampilan; tidak ada yang dihapus atau disimpan berbeda. Kotak menampilkan "n of m".
- **Favorit**: klik kanan > *Add to favorites* (bisa untuk beberapa baris terpilih; menjadi *Remove from favorites* jika semua yang dipilih sudah favorit). Favorit diberi ★ sebelum nama; bintang hanya tampilan, jadi ganti nama, pengurutan, dan pencarian memakai nama biasa. Tampilkan hanya favorit lewat *Show:* ★ Favorites.
- **Check selected** (klik kanan): cek ulang hanya proyek yang dipilih. *Check for updates* tetap mengecek semuanya.
- Proyek yang repositorinya **dihapus atau dijadikan private** menampilkan error merah *Not found (deleted or private)*, rilis terakhir tetap tersimpan, dan pulih sendiri jika repositorinya kembali. Server yang sedang down menampilkan *Server down (HTTP 5xx). Try later.*
- Saat **batas API GitHub** tercapai, pengecekan berhenti, tidak ada proyek yang ditandai error, dan bar status menyebut berapa proyek yang belum dicek serta kapan batas direset. Isi token di Settings untuk batas lebih tinggi.
- Jendela **mengingat ukuran, posisi (termasuk monitor) dan status maximize**. Jika monitor itu sudah tidak ada, jendela dibuka di monitor utama. Untuk mereset, tutup aplikasi lalu hapus entri `"window"` di bawah `"settings"` pada `projects.json`.
- **Import / Export** daftar proyek sebagai file `.json` (gabungkan atau ganti saat import)
- Mode **terang / gelap**: klik ikon bulan / matahari di kanan bawah (awalnya mengikuti tema Windows Anda)
- Semua kolom ikut melebar atau menyempit secara proporsional saat jendela diubah ukurannya (seret batas kolom untuk mengubah proporsinya)
- Ikon kecil pada tombol, garis pemisah tipis antar baris dan kolom, dan ikon aplikasi sendiri
- Nomor versi di judul jendela; **Settings > About** juga menampilkannya
- Menu klik kanan di kotak teks (Cut / Copy / Paste / Select all), dan klik kanan pada status bar untuk menyalin pesannya
- Portable: satu file `.exe`, tanpa installer, tanpa entri registry

Aplikasi ini hanya membaca informasi release. Ia tidak pernah mengunduh atau memasang apa pun.

## Keyboard dan mouse

### Menambah dan memfilter
| Aksi | Cara |
|---|---|
| Menambah proyek di kotak atas | **Enter**, atau tombol *Add project* |
| Pindah ke kotak Filter | **Ctrl+F** |
| Mengosongkan filter (teks dan status) | **Esc** di kotak Filter, atau tombol *Clear* |

### Memilih proyek
| Aksi | Cara |
|---|---|
| Pilih satu | Klik baris |
| Tambah atau lepas satu baris dari pilihan | **Ctrl+klik** |
| Pilih satu rentang | **Shift+klik** |
| Menggeser pilihan | **Atas / Bawah** |
| Pilih semua proyek yang tampil | **Ctrl+A** |

*Shift+panah dan Home / End tidak ada di edisi Python (edisi Rust punya).*

Hanya baris yang terlihat yang terpilih, jadi saat filter aktif, *Remove* dan *Mark as seen* hanya berlaku pada baris itu.

### Mengelola proyek
| Aksi | Cara |
|---|---|
| Ganti nama proyek terpilih | **F2**, atau klik dua kali pada nama di kolom **Project**, atau ikon pensil saat kursor di atas baris, atau klik kanan > Rename |
| Simpan / batalkan ganti nama | **Enter** / **Esc** |
| Membuka halaman rilis | Klik dua kali di kolom mana pun kecuali **Project**, atau *Open release page* |
| Menghapus proyek terpilih | **Delete**, atau *Remove* (selalu bertanya dulu) |
| Menu baris | **Klik kanan** baris: Open release page, Open repository, Check selected, Mark as seen, Add to favorites, Rename, Reset name, Include pre-releases, Remove. Klik kanan pada baris yang belum terpilih akan memilihnya dulu |

### Daftar dan jendela
| Aksi | Cara |
|---|---|
| Mengurutkan | Klik header **Project**, **Repository**, **Source**, **Published**, atau **Status**; klik lagi untuk membalik |
| Mengubah lebar kolom | Seret garis pembatas di header |
| Menggulir | Roda mouse; **Shift+roda** menggulir ke samping |
| Menyalin teks status | **Klik kanan** bar status > Copy |
| Kotak teks | Klik kanan untuk Cut / Copy / Paste / Select all |
| Menutup jendela About | **Esc** |
| Beralih gelap / terang | Tombol bulan / matahari di kanan bawah |

## Bahan yang perlu disiapkan

Pilih baris yang sesuai dengan tujuan Anda.

| Saya ingin... | Yang dibutuhkan |
|---|---|
| **Langsung memakai aplikasi** (`.exe` dari [Releases](https://github.com/santosasarno-code/github-release-tracker/releases)) | Windows 10 atau 11 dan koneksi internet. **Tidak perlu yang lain**: Python *tidak* diperlukan. |
| **Menjalankan dari source** (`github_release_tracker.py`) | Windows 10/11 dan **Python 3.10 atau lebih baru** dari [python.org](https://www.python.org/downloads/windows/). Tidak perlu paket tambahan. |
| **Membuat `.exe` sendiri** (`build.bat`) | Python yang sama, dengan opsi **"Add python.exe to PATH"** dicentang saat instalasi, dan koneksi internet (skrip mengunduh PyInstaller). |

### Detail Python (hanya untuk menjalankan dari source atau membuat exe)

- **Versi:** kodenya memakai Python standar dan sintaksnya jalan mulai Python 3.6, tetapi yang disarankan hanya versi baru. Versi yang sudah diuji: **3.10 dan 3.12** (tes GUI otomatis di Linux) dan **3.8** (hanya tes logika, GUI-nya tidak bisa diuji). Gunakan 3.10 atau lebih baru.
- **tkinter harus ikut terpasang.** Installer dari python.org menyertakannya secara bawaan (opsi "tcl/tk and IDLE"). Cek dengan:
  ```
  python -c "import tkinter; print('tkinter OK')"
  ```
  Kalau muncul `No module named tkinter`, jalankan lagi installer Python, pilih *Modify*, lalu centang **tcl/tk and IDLE**.
- **Tidak perlu `pip install`** untuk menjalankan dari source: aplikasi hanya memakai library standar Python. PyInstaller hanya dibutuhkan untuk membuat exe, dan `build.bat` memasangnya otomatis.
- Python dari sumber lain (misalnya Microsoft Store) belum diuji; installer python.org adalah yang disarankan.

## Cara cepat memulai

### Memakai `.exe`

1. Unduh `GitHubReleaseTracker.exe` dari [halaman Releases](https://github.com/santosasarno-code/github-release-tracker/releases).
2. Taruh di folder mana saja (boleh di flashdisk) lalu jalankan.
3. Tempel URL GitHub seperti `https://github.com/owner/repo` lalu klik **Add project**.
4. Nanti, klik **Check for updates**.

> **Windows mungkin memberi peringatan** ("Windows protected your PC") atau antivirus menandai file ini. Ini sering terjadi pada file tunggal buatan PyInstaller, dan aplikasi ini tidak ditandatangani digital. Kalau Anda tidak mau memercayai `.exe` unduhan, baca source-nya (hanya satu file Python) dan buat sendiri dengan langkah di bawah.

#### Memeriksa file unduhan Anda

Mulai v1.1.0, `.exe` di halaman Releases dibuat oleh **workflow GitHub Actions** "Build Windows exe" di mesin Windows milik GitHub, dari source di repository ini. Catatan release memuat tautan ke log build publik dari run yang sama, jadi Anda bisa melihat bagaimana file itu dibuat. (v1.0.0 dan v1.0.1 dibuat oleh pembuatnya di PC pribadinya dengan `build.bat`.) Pembuatnya tetap mengunduh hasilnya lalu melampirkannya ke Release secara manual.

Hash SHA-256 dari `.exe` tiap release dicantumkan di catatan release tersebut. Untuk memastikan unduhan Anda utuh, buka PowerShell di folder file tersebut lalu jalankan:

```
Get-FileHash .\GitHubReleaseTracker.exe -Algorithm SHA256
```

Hash-nya harus sama dengan yang tertulis di catatan release. Ini membuktikan file Anda sama dengan yang dipublikasikan, bukan bahwa file itu aman; yang benar-benar bisa Anda periksa adalah source code-nya. Kalau Anda membuat `.exe` sendiri, hash-nya akan berbeda: build di mesin yang berbeda tidak identik byte demi byte.

### Menjalankan dari source

```
python github_release_tracker.py
```
(atau `py github_release_tracker.py`)

### Membuat `.exe` sendiri

1. Pasang Python (lihat di atas) dan unduh repository ini.
2. Klik dua kali `build.bat`.
3. Aplikasi portable Anda muncul di `dist\GitHubReleaseTracker.exe`.

Cara manual:
```
pip install pyinstaller
pyinstaller --onefile --windowed --icon icon.ico --name GitHubReleaseTracker github_release_tracker.py
```

`build.bat` juga memeriksa Python dan tkinter, memasang ikon, dan menulis file catatan release siap tempel berisi SHA-256 (`dist\release-notes-vX.Y.Z.md`). Untuk pemelihara: lihat [RELEASING.md](RELEASING.md) untuk daftar langkah merilis dan [CHANGELOG.md](CHANGELOG.md) untuk perubahan tiap versi.

## Cara kerjanya

- Aplikasi membaca feed release publik tiap proyek, `https://github.com/<owner>/<repo>/releases.atom`. Ini tidak perlu login dan tidak memakai batas permintaan API GitHub.
- Kalau feed gagal atau proyek tidak punya release, aplikasi beralih ke API GitHub (yang membolehkan sekitar 60 permintaan per jam tanpa token). Kalau proyek sama sekali tidak punya GitHub Release, yang ditampilkan adalah git tag terbaru.
- Saat Anda menambah proyek, release yang ada saat itu dianggap sudah dilihat. Hanya release yang terbit sesudahnya yang ditandai sebagai update.
- Deteksi update membandingkan identitas release (dan tag), bukan nomor versi, jadi tag tidak biasa seperti `nightly` atau `build-123` tetap bisa. Efek sampingnya: release yang dihapus lalu dibuat ulang bisa muncul sebagai update.
- Proyek di host lain dibaca lewat API publik host itu (GitLab: `/api/v4/projects/<path>/releases`, Gitea / Forgejo / Codeberg: `/api/v1/repos/<owner>/<repo>/releases`). Rilis draf dan rilis "upcoming" GitLab diabaikan. Untuk server yang tidak dikenal, aplikasi mencoba API Gitea / Forgejo dulu lalu GitLab, satu kali, saat proyek ditambahkan. Token tidak pernah dikirim ke host ini (token GitHub opsional hanya dipakai untuk `github.com`).
- Tautan yang tersimpan di data Anda hanya dibuka jika mengarah ke host proyek itu sendiri.
- Aplikasi hanya menghubungi `github.com` dan `api.github.com`, ditambah host proyek yang Anda tambahkan sendiri.

## Data Anda

- Daftar Anda disimpan di `projects.json` **di sebelah file `.exe`**. Kalau folder itu hanya-baca (misalnya `Program Files`), aplikasi memakai `%APPDATA%\GitHubReleaseTracker`.
- **Export** menulis file `.json` terpisah untuk cadangan atau pindah ke PC lain. **Import** membacanya kembali (dan juga bisa membaca `projects.json` dari build lama).
- **Nama kustom ikut terbawa di file.** Kalau Anda mengganti nama proyek lalu membagikan hasil Export, **Import** di PC orang lain menampilkan nama Anda untuk proyek yang belum mereka punya. Untuk proyek yang sudah mereka punya, **Merge** membiarkan entri dan nama mereka apa adanya (nama Anda tidak diterapkan); **Replace** mengganti seluruh daftar mereka dengan isi file, termasuk namanya. File hasil Export v1.1.0 tetap bisa di-import di versi lama, tetapi nama kustomnya dibuang.
- Di Settings ada kolom token GitHub (opsional). Token **tidak diperlukan** untuk pemakaian normal. Kalau Anda mengisinya, token disimpan **sebagai teks biasa** di `projects.json`, jadi jangan bagikan atau unggah file itu. File hasil Export tidak pernah berisi token.

## Keterbatasan

- Hanya Windows (dibuat untuk Windows 10/11).
- Feed tidak memberi tahu release mana yang pre-release, jadi label `(pre-release)` tidak tampil untuk hasil dari feed. Mode "stable only" (klik kanan proyek, hapus centang *Include pre-releases*) memakai API dan batas permintaannya.
- Feed adalah halaman publik GitHub, bukan API resmi; GitHub bisa mengubah atau membatasinya.
- Repository privat tidak didukung tanpa token.
- Host lain: hanya repo publik (tanpa token), hanya rilis resmi (bukan tag saja), dan GitLab tidak punya penanda pre-release. Server self-hosted dengan sertifikat yang tidak dipercaya Windows ditolak (aplikasi tidak pernah mematikan pemeriksaan sertifikat). Alamat `http://` hanya dipakai kalau Anda mengetiknya.
- Versi lama (sebelum ini) tidak memahami proyek dari host lain: proyek itu dilewati saat membaca `projects.json` dan hilang saat menyimpan. Pakai versi baru di semua tempat yang berbagi file itu.
- Tanggal "Published" berasal dari waktu update di feed, jadi mengedit release di GitHub bisa mengubahnya.
- Deskripsi proyek (tampil di status bar saat dipilih) dibaca sekali ketika proyek ditambahkan dan tidak diperbarui lagi. Kalau API GitHub sedang tidak tersedia saat itu, proyek menampilkan "No description, website, or topics provided." walaupun repository-nya sebenarnya punya deskripsi.
- Garis antar baris dan kolom serta pensil rename adalah widget kecil yang digambar di atas daftar. Klik tepat pada garis setebal 1 piksel diteruskan ke barisnya, tetapi *klik dua kali* tepat di garis itu bisa gagal membuka halaman release.
- Ikon berukuran 16 px (24 px pada layar dengan skala 150% atau lebih). Tidak semua pengaturan layar Windows sudah diuji.

## File di repository ini

| File | Isinya |
|---|---|
| `github_release_tracker.py` | Seluruh aplikasi (satu file Python, hanya library standar). |
| `build.bat` | Membuat `dist\GitHubReleaseTracker.exe`. |
| `icon.ico` | Ikon aplikasi yang dipakai saat build. |
| `tools/` | Alat pemelihara: `release_info.py` (dipakai `build.bat`) dan `make_icons.py` (membuat ulang ikon; butuh Pillow, tidak diperlukan untuk memakai atau membuat aplikasi). |
| `CHANGELOG.md`, `RELEASING.md` | Daftar perubahan, dan cara menerbitkan release. |

## Pemecahan masalah

| Masalah | Yang dilakukan |
|---|---|
| `No module named tkinter` | Pasang ulang Python dari python.org dengan **tcl/tk and IDLE** dicentang. |
| `python` tidak dikenali | Pasang ulang Python dan centang **Add python.exe to PATH**, atau pakai `py` sebagai pengganti `python`. |
| "GitHub API rate limit reached" | Batas 60 per jam pada API cadangan tercapai. Tunggu sampai jam yang tertera, atau isi token di **Settings**. |
| "Not found" saat menambah proyek | Periksa ejaannya. Repository privat tidak didukung tanpa token. |
| Peringatan Windows SmartScreen / antivirus | Lihat catatan di bagian *Memakai `.exe`*. |
| Proyek menampilkan "No releases published" | Repository belum punya GitHub Release maupun tag. |

## Lisensi

[MIT](LICENSE). Proyek ini tidak berafiliasi dengan atau didukung oleh GitHub.
