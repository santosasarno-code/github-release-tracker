# Changelog

## [1.5.0]
- New **Source** column after Repository: GitHub, GitLab, Codeberg, or the address of your own server. Click the header to sort (GitHub, GitLab, Codeberg, then other servers A-Z; names A-Z inside each group). The search box matches the source too (type `gitlab`).
- The **Repository** column now shows `owner/repo` only; the host moved to Source. It sorts by what it shows. The **Project** column is unchanged.
- **Ctrl+A** in the list selects every listed project (a filter limits it).
- New "Keyboard and mouse" section in the README (English and Bahasa Indonesia).
- Brought in line with the Rust edition 2.3.0 (<https://github.com/santosasarno-code/github-release-tracker-rs>). Your `projects.json` is unchanged; nothing new is saved.

## [1.4.0]
- **Search and filter.** A *Filter* row sits above the list: type to show only projects whose name or repository contains every word you typed (any case), and/or choose *Show:* All projects, Updates available, Errors, Up to date or No releases. Ctrl+F jumps to the box, Esc (or *Clear*) resets it, and it shows "n of m". Only the view changes; nothing is removed or saved differently. Adding a project clears the filter so the new row is visible.
- The project limit is now 2000 (was 500). Before, extra entries in `projects.json` were dropped when the file was read; adding past the limit now says the list is full.
- Brought in line with the Rust edition 2.2.0 (<https://github.com/santosasarno-code/github-release-tracker-rs>).
- Not done yet: user-defined tags, and keeping several entries for the same repository (duplicates are still merged into one).

## [1.3.0]
- Track projects on other hosts: **GitLab** (gitlab.com or your own server, with groups and subgroups), **Codeberg**, **Gitea**, **Forgejo** and self-hosted servers of those. Paste the project URL like a GitHub one; `owner/repo` still means GitHub.
- Public repositories only, no token, and only official releases: a project with just tags (or no release yet) is refused when you add it. The optional GitHub token is sent to `github.com` only.
- Projects from other hosts show the host in the Repository column. Their release links only open on the project's own host. Older versions skip these projects when reading `projects.json` and lose them when saving, so update every copy you share the file with. GitHub-only files are unchanged.
- Security: names such as `..` are no longer accepted in an owner or repository name.
- Brought in line with the Rust edition 2.1.0 (<https://github.com/santosasarno-code/github-release-tracker-rs>).

## [1.2.1]
- Fix: at a high Windows display scale (for example 225%) the list rows were too short for the text, so the text was cut off, and the window and columns opened too small. Row height, column widths, window size and the sort arrow now follow the display scale. At 100% nothing changes.

## [1.2.0]
- Double-click a project **name** to rename it (same as the pencil). Double-clicking any other column still opens the release page.
- "Mark as seen" now has a checkbox icon.
- The dark / light button moved to the bottom right (icon only). The status bar says "Dark mode." or "Light mode." when you switch.
- Resizing the window does less work: the row lines are no longer re-placed when only the width changes, and the separator lines are redrawn once after a burst of resize events. (Not benchmarked on Windows; please report if the list still feels slow.)
- Brought in line with the Rust edition 2.0.0 (<https://github.com/santosasarno-code/github-release-tracker-rs>); both read and write the same `projects.json`.

## [1.1.1]
- Thin separator lines between columns, in the same colour as the row lines.
- Column headers are left-aligned and bold.
- The horizontal scrollbar only appears when the columns do not fit; the vertical one stays visible.
- Fix: making a column narrower no longer leaves an empty strip on the right; the last column takes the freed space.

## [1.1.0]
- Release-tag app icon (window, taskbar and the `.exe` file).
- Version number in the window title, and an About box (Settings > About) with a Copy version button.
- Small icons next to the toolbar buttons; the theme button is now a moon / sun icon with a tooltip.
- Thin separator lines between rows.
- Rename a project: hover a row and click the pencil, press F2, or right-click > Rename. Reset name restores the GitHub name. Custom names are saved and exported.
- Fix: when the window is stretched sideways, all columns now grow in proportion (before, only Status grew). Shrinking works the same way, and a column you drag keeps your width until the window is resized.
- Fix: a project with an empty About box on GitHub no longer shows another project's description; it shows "No description, website, or topics provided."
- Fix: status messages such as "Renamed to ..." or "Marked 1 project(s) as seen." are no longer replaced right away by the project description.
- `build.bat` now checks Python and tkinter, reads the version, adds the icon and writes ready-to-paste release notes with the SHA-256.
- The GitHub Actions workflow (manual run) now also writes the release notes, with the SHA-256 and a link to the public build log. It never touches a Release by itself.

## [1.0.1]
- Right-click menus in text boxes (Cut / Copy / Paste / Select all) and on the status bar (Copy).

## [1.0.0]
- First release: add GitHub projects, check for new releases (feed first, API as fallback), sortable list, import / export, light and dark theme, portable `.exe`.
