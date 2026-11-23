# Releasing a new version

English first, Bahasa Indonesia below.

There are two ways to make the `.exe`. **Way A (GitHub builds it)** is the recommended one: the public build log shows how the file was made. **Way B (`build.bat`)** builds it on your own Windows PC; use it for quick tests or if you prefer. Either way you attach the exe to the Release by hand, and the SHA-256 in the notes must belong to that exact file.

## Checklist

1. **Raise the version number** in `github_release_tracker.py`:

   ```python
   APP_VERSION = "1.1.1"
   ```

   Digits and dots only (`1.2.3`). The release tag is this number with a `v` in front (`v1.1.1`).
   Rule of thumb: `1.1.1` = bug fix, `1.2.0` = new feature, `2.0.0` = big change.
2. **(Optional) Describe the change.** Add a section at the top of `CHANGELOG.md`:

   ```
   ## [1.1.1]
   - Fix: ...
   ```

   The release notes file copies this section for you.
3. **Upload the changed files to GitHub** (*Add file > Upload files*, then *Commit changes*): at least `github_release_tracker.py`, plus `CHANGELOG.md` / README if you changed them. Do this **before** building. Never upload `dist`, `build`, `*.spec` or `projects.json`.
4. **Make the exe.** Pick one:

   **Way A: GitHub builds it (recommended)**
   1. Repository > **Actions** > **Build Windows exe** > **Run workflow** (branch `main`).
   2. Wait for the green check, open the run, and download the artifact **GitHubReleaseTracker-windows** at the bottom.
   3. Extract it. It contains `GitHubReleaseTracker.exe`, `GitHubReleaseTracker.exe.sha256` and `release-notes-v1.1.1.md`.

   **Way B: your own PC**
   1. Double-click `build.bat`. It checks Python and tkinter, reads the version, builds `dist\GitHubReleaseTracker.exe` with the icon, and writes `dist\release-notes-v1.1.1.md`.
   2. It stops with a clear message if something is wrong, for example a version like `1.1` or `v1.1.1`.
   3. If you use way B, the notes say the exe was built on your PC, and the README's "Verify your download" section should say so too.
5. **Test the exe.** Run it: the window title must say `v1.1.1`; adding a project and **Check for updates** must work.
6. **Check the hash.** In PowerShell: `Get-FileHash .\GitHubReleaseTracker.exe -Algorithm SHA256`. It must equal the hash in the `.sha256` file and in the release notes.
7. **Create the release.** *Releases > Draft a new release*:
   - **Choose a tag:** type `v1.1.1` and pick *Create new tag on publish*. It must match `APP_VERSION` exactly.
   - **Title:** `v1.1.1`
   - **Description:** paste the whole content of `release-notes-v1.1.1.md`.
   - **Attach:** drag `GitHubReleaseTracker.exe` into the files box.
   - For a test version use a tag like `v1.2.0-beta` and tick *Set as a pre-release*.
   - Click **Publish release**.
8. **Check it.** Download the exe from the release page and compare its hash with the notes once more. Open the **Actions** tab: nothing should have started by itself.

## Common mistakes

| Mistake | Result |
|---|---|
| Forgot to raise `APP_VERSION` | The exe's title shows the old version. Raise it, rebuild, and replace the file on the release. |
| Tag does not match `APP_VERSION` | Confusing for users. Delete the tag/release and create it again with the right tag. |
| Built before uploading the new source (way A) | The exe is built from the old files on GitHub. Upload first, then run the workflow. |
| Notes and exe come from different builds | The hash will not match. Always take the notes file and the exe from the same run. |
| `dist` or `projects.json` uploaded to GitHub | `projects.json` can contain your token. Both are in `.gitignore`, but the web upload ignores it: do not drag them in. |

---

# Merilis versi baru

Ada dua cara membuat `.exe`. **Cara A (dibuat GitHub)** adalah yang disarankan: log build yang publik memperlihatkan bagaimana file dibuat. **Cara B (`build.bat`)** membuatnya di PC Windows Anda sendiri; pakai untuk uji cepat atau jika Anda lebih suka. Dengan cara apa pun, exe dilampirkan ke Release secara manual, dan SHA-256 di catatan harus milik file yang persis sama.

## Daftar langkah

1. **Naikkan nomor versi** di `github_release_tracker.py`:

   ```python
   APP_VERSION = "1.1.1"
   ```

   Hanya angka dan titik (`1.2.3`). Tag release adalah nomor ini dengan awalan `v` (`v1.1.1`).
   Patokan: `1.1.1` = perbaikan bug, `1.2.0` = fitur baru, `2.0.0` = perubahan besar.
2. **(Opsional) Tulis perubahannya.** Tambahkan bagian di paling atas `CHANGELOG.md`:

   ```
   ## [1.1.1]
   - Fix: ...
   ```

   File catatan release menyalin bagian ini untuk Anda.
3. **Upload file yang berubah ke GitHub** (*Add file > Upload files*, lalu *Commit changes*): minimal `github_release_tracker.py`, ditambah `CHANGELOG.md` / README jika diubah. Lakukan ini **sebelum** build. Jangan pernah meng-upload `dist`, `build`, `*.spec`, atau `projects.json`.
4. **Buat exe.** Pilih satu:

   **Cara A: dibuat GitHub (disarankan)**
   1. Repository > **Actions** > **Build Windows exe** > **Run workflow** (branch `main`).
   2. Tunggu ceklis hijau, buka run-nya, lalu unduh artifact **GitHubReleaseTracker-windows** di bagian bawah.
   3. Extract. Isinya `GitHubReleaseTracker.exe`, `GitHubReleaseTracker.exe.sha256`, dan `release-notes-v1.1.1.md`.

   **Cara B: PC Anda sendiri**
   1. Klik dua kali `build.bat`. Skrip memeriksa Python dan tkinter, membaca versi, membuat `dist\GitHubReleaseTracker.exe` lengkap dengan ikon, dan menulis `dist\release-notes-v1.1.1.md`.
   2. Skrip berhenti dengan pesan jelas jika ada masalah, misalnya versi `1.1` atau `v1.1.1`.
   3. Kalau memakai cara B, catatan menyebut exe dibuat di PC Anda, dan bagian "Memeriksa file unduhan Anda" di README juga harus disesuaikan.
5. **Uji exe-nya.** Jalankan: judul jendela harus berisi `v1.1.1`; menambah proyek dan **Check for updates** harus berfungsi.
6. **Periksa hash.** Di PowerShell: `Get-FileHash .\GitHubReleaseTracker.exe -Algorithm SHA256`. Harus sama dengan isi file `.sha256` dan hash di catatan release.
7. **Buat release.** *Releases > Draft a new release*:
   - **Choose a tag:** ketik `v1.1.1` lalu pilih *Create new tag on publish*. Harus sama persis dengan `APP_VERSION`.
   - **Title:** `v1.1.1`
   - **Description:** tempel seluruh isi `release-notes-v1.1.1.md`.
   - **Lampiran:** seret `GitHubReleaseTracker.exe` ke kotak file.
   - Untuk versi uji pakai tag seperti `v1.2.0-beta` dan centang *Set as a pre-release*.
   - Klik **Publish release**.
8. **Periksa.** Unduh exe dari halaman release dan cocokkan lagi hash-nya dengan catatan. Buka tab **Actions**: tidak boleh ada yang berjalan sendiri.

## Kesalahan yang sering terjadi

| Kesalahan | Akibat |
|---|---|
| Lupa menaikkan `APP_VERSION` | Judul exe menampilkan versi lama. Naikkan, build ulang, lalu ganti file di release. |
| Tag tidak sama dengan `APP_VERSION` | Membingungkan pengguna. Hapus tag/release lalu buat ulang dengan tag yang benar. |
| Build sebelum source baru di-upload (cara A) | Exe dibuat dari file lama di GitHub. Upload dulu, baru jalankan workflow. |
| Catatan dan exe berasal dari build berbeda | Hash tidak cocok. Selalu ambil file catatan dan exe dari run yang sama. |
| `dist` atau `projects.json` ikut ter-upload | `projects.json` bisa memuat token Anda. Keduanya ada di `.gitignore`, tetapi upload lewat web tidak memakainya: jangan diseret masuk. |
