# GitHub Release Tracker

A small, portable Windows app that tracks the latest release of the projects you care about (GitHub, GitLab, Codeberg, Gitea / Forgejo and self-hosted servers) and tells you when a new one appears. No account, no login, and no token needed.

🇮🇩 [Baca dalam Bahasa Indonesia](README.id.md)

<!-- Add a screenshot of your own here, e.g. save it as docs/screenshot.png and use:
![Screenshot](docs/screenshot.png)
-->

## Features

- Add a project by pasting a GitHub URL or `owner/repo`
- **Other hosts, same way.** Paste the URL of a project on **GitLab** (`gitlab.com` or your own server, including groups and subgroups), **Codeberg**, **Gitea**, **Forgejo** or any self-hosted server of those. Public repositories only, no token. Only **official releases** are tracked: a project that has just tags (or nothing yet) is refused when you add it
- See the project name, repository, current release, publish date and status at a glance
- **Check for updates** refreshes every project; a project with a newer release is highlighted as `Update available: v1.0 -> v1.1`
- **Mark as seen** clears the highlight once you have dealt with an update
- Double-click a project to open its release page in your browser (double-clicking the **Project** name renames it instead)
- **Rename a project** to something readable: hover a row and click the pencil (or double-click the name, press **F2**, or right-click > Rename). *Reset name* brings the GitHub name back. Your names are saved and included in Export
- Click the **Project**, **Repository**, **Source**, **Published** or **Status** header to sort (click again to reverse; an arrow shows the direction)
- The **Source** column tells where each project lives (GitHub, GitLab, Codeberg, or your own server's address); click its header to sort by it. The search box matches it too.
- **Filter** the list: type in the search box (Ctrl+F jumps there, Esc clears it) to show only projects whose name or repository contains every word you typed, and/or pick *Show:* All projects / Updates available / Errors / Up to date / No releases. It only changes what is listed; nothing is removed or saved differently. The box shows "n of m".
- **Import / Export** your project list as a `.json` file (merge or replace on import)
- **Light / dark** mode: click the moon / sun icon at the bottom right (starts with your Windows theme)
- Columns resize in proportion when you stretch or shrink the window (drag a column border to change the proportions)
- Small icons on the buttons, thin separator lines between rows and columns, and the app's own icon
- Version number in the window title; **Settings > About** shows it too
- Right-click menu in the text boxes (Cut / Copy / Paste / Select all), and right-click the status bar to copy its message
- Portable: one `.exe`, no installer, no registry entries

The app only reads release information. It never downloads or installs anything.

## Keyboard and mouse

### Adding and filtering
| Action | How |
|---|---|
| Add the project in the top box | **Enter**, or the *Add project* button |
| Jump to the Filter box | **Ctrl+F** |
| Clear the filter (text and status) | **Esc** in the Filter box, or the *Clear* button |

### Selecting projects
| Action | How |
|---|---|
| Select one | Click a row |
| Add or remove one row from the selection | **Ctrl+click** |
| Select a range | **Shift+click** |
| Move the selection | **Up / Down** |
| Select every listed project | **Ctrl+A** |

*Shift+arrows and Home / End are not available in the Python edition (the Rust edition has them).*

Only the rows you can see are selected, so with a filter on, *Remove* and *Mark as seen* act on those rows only.

### Working with projects
| Action | How |
|---|---|
| Rename the selected project | **F2**, or double-click the **Project** name, or the pencil that appears when you hover a row, or right-click > Rename |
| Save / cancel a rename | **Enter** / **Esc** |
| Open the release page | Double-click any column except **Project**, or *Open release page* |
| Remove the selected projects | **Delete**, or *Remove* (always asks first) |
| Row menu | **Right-click** a row: Open release page, Open repository, Mark as seen, Rename, Reset name, Include pre-releases, Remove. Right-clicking a row that is not selected selects it first |

### The list and window
| Action | How |
|---|---|
| Sort | Click the **Project**, **Repository**, **Source**, **Published** or **Status** header; click again to reverse |
| Resize a column | Drag the border in the header |
| Scroll | Mouse wheel; **Shift+wheel** scrolls sideways |
| Copy the status text | **Right-click** the status bar > Copy |
| Text boxes | Right-click for Cut / Copy / Paste / Select all |
| Close the About window | **Esc** |
| Switch dark / light | The moon / sun button at the bottom right |

## What you need

Pick the row that matches what you want to do.

| I want to... | You need |
|---|---|
| **Just use the app** (`.exe` from [Releases](https://github.com/santosasarno-code/github-release-tracker/releases)) | Windows 10 or 11, an internet connection. **Nothing else**: Python is *not* required. |
| **Run from source** (`github_release_tracker.py`) | Windows 10/11, **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/windows/). No extra packages. |
| **Build the `.exe` yourself** (`build.bat`) | The same Python, with **"Add python.exe to PATH"** ticked in the installer, and an internet connection (the script downloads PyInstaller). |

### Python details (only for running from source or building)

- **Version:** the source is written for standard Python and its syntax works from Python 3.6, but only recent versions are recommended. Tested versions: **3.10 and 3.12** (automated GUI tests on Linux) and **3.8** (logic tests only; its GUI could not be tested). Use 3.10 or newer.
- **tkinter must be included.** The python.org installer includes it by default (the "tcl/tk and IDLE" option). Check with:
  ```
  python -c "import tkinter; print('tkinter OK')"
  ```
  If that fails with `No module named tkinter`, re-run the Python installer, choose *Modify*, and tick **tcl/tk and IDLE**.
- **No `pip install` is needed** to run from source: the app uses only Python's standard library. PyInstaller is needed only for building, and `build.bat` installs it for you.
- Python from other sources (for example the Microsoft Store) has not been tested; the python.org installer is the recommended one.

## Quick start

### Use the `.exe`

1. Download `GitHubReleaseTracker.exe` from the [Releases page](https://github.com/santosasarno-code/github-release-tracker/releases).
2. Put it in any folder you like (it can live on a USB stick) and run it.
3. Paste a GitHub URL such as `https://github.com/owner/repo` and click **Add project**.
4. Later, click **Check for updates**.

> **Windows may warn you** ("Windows protected your PC") or antivirus may flag the file. This happens often with single-file executables made by PyInstaller and the app is not code-signed. If you do not want to trust a downloaded `.exe`, read the source (it is one Python file) and build it yourself with the steps below.

#### Verify your download

From v1.1.0 on, the `.exe` on the Releases page is built by the **GitHub Actions workflow** "Build Windows exe" on a GitHub-hosted Windows machine, from the source in this repository. The release notes link to the public build log of that exact run, so you can see how the file was made. (v1.0.0 and v1.0.1 were built by the author on their own PC with `build.bat`.) The author still downloads the result and attaches it to the Release by hand.

The SHA-256 hash of each release's `.exe` is listed in that release's notes. To check that your download is intact, open PowerShell in the folder with the file and run:

```
Get-FileHash .\GitHubReleaseTracker.exe -Algorithm SHA256
```

The hash must match the one in the release notes. This proves the file is the one that was published, not that it is safe; the source code is what you can actually inspect. If you build the `.exe` yourself the hash will differ: builds on different machines are not identical byte for byte.

### Run from source

```
python github_release_tracker.py
```
(or `py github_release_tracker.py`)

### Build the `.exe` yourself

1. Install Python (see above) and download this repository.
2. Double-click `build.bat`.
3. Your portable app appears at `dist\GitHubReleaseTracker.exe`.

Manual alternative:
```
pip install pyinstaller
pyinstaller --onefile --windowed --icon icon.ico --name GitHubReleaseTracker github_release_tracker.py
```

`build.bat` also checks Python and tkinter, adds the icon, and writes a ready-to-paste release notes file with the SHA-256 (`dist\release-notes-vX.Y.Z.md`). Maintainers: see [RELEASING.md](RELEASING.md) for the full release checklist and [CHANGELOG.md](CHANGELOG.md) for what changed in each version.

## How it works

- It reads each project's public release feed, `https://github.com/<owner>/<repo>/releases.atom`. This needs no login and does not use the GitHub API's request limit.
- If the feed fails or a project has no releases, it falls back to GitHub's API (which allows about 60 requests per hour without a token). If the project has no GitHub Releases at all, it shows the newest git tag instead.
- When you add a project, its current release counts as already seen. Only releases published afterwards are flagged as updates.
- Update detection compares the release identity (and tag), not version numbers, so unusual tags like `nightly` or `build-123` work. Side effect: a deleted and re-created release can show up as an update.
- Projects on other hosts are read through that host's public API (GitLab: `/api/v4/projects/<path>/releases`, Gitea / Forgejo / Codeberg: `/api/v1/repos/<owner>/<repo>/releases`). Draft releases and GitLab "upcoming" releases are ignored. For a server it does not know, the app tries the Gitea / Forgejo API first and then GitLab's, once, when you add the project. No token is ever sent to these hosts (the optional GitHub token is used for `github.com` only).
- Links stored in your data are only opened if they point to the project's own host.
- The app contacts only `github.com` and `api.github.com`, plus the hosts of projects you add yourself.

## Your data

- Your list is saved in `projects.json` **next to the `.exe`**. If that folder is read-only (for example `Program Files`), it uses `%APPDATA%\GitHubReleaseTracker` instead.
- **Export** writes a separate `.json` file for backup or moving to another PC. **Import** reads it back (and also reads the `projects.json` of older builds).
- **Custom names travel with the file.** If you rename a project and share your Export, the other person's **Import** shows your names for projects they do not have yet. For a project they already have, **Merge** keeps their entry and name unchanged (your name is not applied); **Replace** swaps their whole list for the file, names included. Files exported by v1.1.0 still import in older versions, but the custom names are dropped.
- Settings has an optional GitHub token. It is **not needed** for normal use. If you add one, it is stored **in plain text** in `projects.json`, so do not share or upload that file. Exported files never contain the token.

## Known limitations

- Windows only (developed for Windows 10/11).
- The release feed does not say which releases are pre-releases, so the `(pre-release)` label is not shown for feed results. "Stable only" mode (right-click a project, untick *Include pre-releases*) uses the API and its rate limit.
- The feed is a public GitHub page, not an official API; GitHub could change or throttle it.
- Private repositories are not supported without a token (GitHub only).
- Other hosts: public repositories only (no token), official releases only (not bare tags), and there is no pre-release marker on GitLab. A self-hosted server with a certificate Windows does not trust is refused (the app never turns certificate checks off). A `http://` address is used only if you type it that way.
- Older versions (before this one) do not understand projects from other hosts: they skip them when reading `projects.json` and drop them when saving. Use the new version everywhere you share the file.
- The "Published" date comes from the feed's updated time, so editing a release on GitHub can change it.
- A project's description (shown in the status bar when you select it) is read once, when the project is added, and is not refreshed later. If the GitHub API was unavailable at that moment, the project shows "No description, website, or topics provided." even if the repository has one.
- The row and column lines and the rename pencil are small widgets drawn over the list. A click exactly on a 1-pixel line is passed on to the row, but a *double*-click exactly on that line may not open the release page.
- Icons are 16 px (24 px on screens scaled to 150% or more). Not every Windows display setup has been tested.

## Files in this repository

| File | What it is |
|---|---|
| `github_release_tracker.py` | The whole app (one Python file, standard library only). |
| `build.bat` | Builds `dist\GitHubReleaseTracker.exe`. |
| `icon.ico` | The app icon used by the build. |
| `tools/` | Maintainer helpers: `release_info.py` (used by `build.bat`) and `make_icons.py` (regenerates the icons; needs Pillow, not needed to use or build the app). |
| `CHANGELOG.md`, `RELEASING.md` | What changed, and how to publish a release. |

## Troubleshooting

| Problem | What to do |
|---|---|
| `No module named tkinter` | Reinstall Python from python.org with **tcl/tk and IDLE** ticked. |
| `python` is not recognized | Reinstall Python and tick **Add python.exe to PATH**, or use `py` instead of `python`. |
| "GitHub API rate limit reached" | You hit the 60-per-hour limit of the API fallback. Wait until the time shown, or add a token in **Settings**. |
| "Not found" when adding a project | Check the spelling. Private repositories are not supported without a token. |
| Windows SmartScreen / antivirus warning | See the note under *Use the `.exe`*. |
| A project shows "No releases published" | The repository has no GitHub Releases and no tags yet. |

## License

[MIT](LICENSE). This project is not affiliated with or endorsed by GitHub.
