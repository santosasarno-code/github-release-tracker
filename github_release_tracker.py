"""
GitHub Release Tracker (portable)
=================================
A small portable Windows desktop app (Python + tkinter, standard library only)
that tracks the latest release of GitHub projects and tells you when a new one
has been published since you last acknowledged it.

How it works
- Add a project by pasting a GitHub URL or "owner/repo".
- The list shows project name, owner/repo, latest release, publish date, status.
- "Check for updates" reads each project's public release feed
  (github.com/owner/repo/releases.atom): no login or token needed and it does not
  use the GitHub API rate limit. The API is only a fallback.
- A project whose latest release differs from the one you last acknowledged is
  highlighted as "Update available: old -> new".
- "Mark as seen" acknowledges the current release (clears the highlight).
- The app never downloads or installs anything; it opens the release page.
- "Import" / "Export" read and write a .json file (merge or replace on import).
- The moon / sun icon (bottom right) toggles the dark / light theme; the choice is remembered.
- Hover a row and click the pencil (or double-click the name, press F2, or right-click >
  Rename) to give a project your own display name. Reset name brings the GitHub name back.

Portable: no installer, no registry writes. Data lives in projects.json next to
the .exe (or this script). Only if that folder is read-only does the app fall
back to %APPDATA%\\GitHubReleaseTracker.

Build the single-file portable .exe on Windows: double-click build.bat, or run
    pip install pyinstaller
    pyinstaller --onefile --windowed --icon icon.ico --name GitHubReleaseTracker github_release_tracker.py
The exe appears in the dist folder.
"""

import base64
import json
import os
import queue
import re
import struct
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import webbrowser
import zlib
from datetime import datetime

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "GitHub Release Tracker"
# Keep in step with the release tag: tag v1.1.1 <-> APP_VERSION "1.1.1" (build.bat checks the format).
APP_VERSION = "1.5.0"
APP_ID = "santosasarno-code.GitHubReleaseTracker"  # Windows taskbar identity (so the taskbar shows our icon)
REPO_URL = "https://github.com/santosasarno-code/github-release-tracker"
NO_DESCRIPTION = "No description, website, or topics provided."  # same wording GitHub shows for an empty About box
API = "https://api.github.com"
MAX_PROJECTS = 2000
MAX_IMPORT_BYTES = 5 * 1024 * 1024
MAX_CUSTOM_NAME = 80

# --- BEGIN GENERATED ICON DATA (tools/make_icons.py) ---
# Toolbar icons: zlib-compressed 8-bit alpha masks, base64. Window icon: 64 px PNG, base64.
ICON_MASKS = {
    "refresh": {
        16: (
            "eNpjYAADRkYGRgY4YGZiYGBhNBSBigF5PLwMDA/CGJkh3MDd7z9um/1/MQMzmNvy///Tp/+BQBbIYWbw+//Uk4194eEZeZJA"
            "Y5kYDvx3AxrEBbWIgefTUyaQBczsrIwIPiML1G6YegaHdCGgdrh5ni//e6Da1wByGMw973cHwn0Aci8PA1QW5h8mZgYkwAhT"
            "CwBdBy28"
        ),
        24: (
            "eNpjYEADTAxYASOGOhYgYGRiyJdDlmNkhsoq/YtkZEE2VC68ujpcnmHt/7UMzAhhiTmf/gPBp21//32RgNnNxKD/8D8U/P7x"
            "P5sBYhATk9iT//+/LUxPn/cNJLWLEaKemWHe/7+3dIEs3osHp2TayjBCTZH5/u+rJgMbC4uAAJLDWRgi//9fyMAK8wUzI0y8"
            "5t//FIijGZH8hCwOFGZhxGIOE0oAwu1lY9A+VyjJCNWBcCeD7s3//ydBvYXkr4VAfz2QZGRiwAyHh/pIliDCbY4Emt2QcJZD"
            "j0dYvDBjj0cckU4EAAARF2gZ"
        ),
    },
    "check": {
        16: (
            "eNpjYGRAAoxAyOkfCwExgbwMjIy8p/7DwRVhRobA/7kGxgYGBobGxsn/kxgY4v+qwnSL/C1gYIj5b8TMxszMxrBossr/PAaG"
            "2P+GQFNYGIr+H1b9nw/iazPwMjJ4/7/HJw2Sj/uvvfwsm+qHL8YM6hD1Ov3/95z/H8TAqAzixwD1T/3/v46Bg0n1fy7IPg0G"
            "hroWkH2SIPuC/yepqIuKqiirKof9T2FgFLyKcO9dcUZGBoH43DwwyE0UBXsQxb8AExtTrQ=="
        ),
        24: (
            "eNp1krFOwzAQhv+znSbQjQmJhVcAFYTEezAgARIsLDDAIzCwsCJlSOdQnAim0qTqwFSpCwsLM2LoBlNVUHo4TdKmEXySB38+"
            "3dl3BkCqAuEfaLroyPWaMzz3WKYHwnrkCh1HkMIh/wyiOMqJo/6Yz6EUvGSwmL2XBJAKTW5DiQwJ2ORz7mMSWaSglVMgLHyE"
            "zJtiIbec+5IX6ZUtXDO/Oq25V2m4wgFP3lfLebBBRu+Mk9EWoAvfpb3vW2DtY8L7sOf+aWnIfFMfMF/BkqV4bJqDNzZ7RSVv"
            "8je+TF9els21Sj5GDbufPFxP3yERFL5Nlo2Gu42alLIm7nKf9Bf71s36dsLjng50+BBqQ6C7I7409YXdqc7luW7qE6wzXwcz"
            "tH/h5AP+c+7TfyJLZP/kF98Lv8Y="
        ),
    },
    "ext": {
        16: (
            "eNpjYAADZhYWFmZmJgbsgJEppX/SwtU7pzMwgvlMjBZf/wPBSQaoDiYG+Us/vv7ZyMAM5TNyHPr//99KKJ+Jge/w/yPX/s9k"
            "YIFyD/4/xC73Zh6YD+Ye5GNgMM0CqYdxmSB2MTLwQLgMYBFGJu5T/w/wMcCdysQ2/TgvA4rLWVG5jFBXIwkgAAAhdSkw"
        ),
        24: (
            "eNql0TEOAUEUBuD/zUyiQSIKewKNS6gUGqVCp1GJYnUaCRGJSusMTqGgoNdLHEHYzK5nsLtmrWQLf/lN3p83eUBWSEqpXhHI"
            "DqFSr7c6PXe8WPXxmSDh7DnMGsoeyG/Y01pf9dJ2M1vccsCseZ5wSOROd9/4KOGkMPF8DjQPEv0KM1Nz5ht3LX/xlSflHQdt"
            "U5nkGVDccCP2mKVE4dCMPGZFZt2SYz7zzQjtvbjF5oGij05tjqIw5EuaIah25GmKnz1VF5LSNxHA79MJiX/zALwVXIU="
        ),
    },
    "trash": {
        16: (
            "eNpjYEAHjIyMLEl5eUksQAZM7MP//x+gsgzrb9++/x8I7t++vR6omGHq9lVrFi1cuGjNqu1TgdJAPUYGpsbGpgZGINUMTMxa"
            "/6FAi5kJJMT7q3dnXNzO3l+8IHmgjg8t+1xc9rV8AGsG4mur9gQF7Vl1DcxlYGbYfXBHVNSOg7uBTCBgYZh783Bc3OGbc4FM"
            "ML/q5cr4+JUvq2D8uP+//wNRHITPyCCXW1hUVJgrx8CI4VkGAJoYSfs="
        ),
        24: (
            "eNpjYIACFjBgIAIwMTOzMHP0L5g/f0E/B5DJzIQs+/E/EHxE8BkZdBwdHB3dn/36+fPXM3dHIEcHKMjAzLDjPxrYARQEooWv"
            "X71///7jJyD4CGS8er0QJM7AwCPIi2wRryAPjCkSHR0ZGRkRASSio0XgPmI0QTbdhJEF5iKJj78PHT21a+fJY4d+f5QAuQYi"
            "zv7wv+Kk2wwM5xep/H/IDhMH0qf+O83+z8P0d63r/1NwYaCrNvyPnvCPm+HHotj/GyCOBFvMMPV/WfN/IbZ/U8r/T2VgQYhX"
            "/p/Y9F+Y/f/kSf8rkcXj/q+p+i/N979nzf84hDgzg8v/Iy3/FYX/Tzvy3wVhPjOD7v9bFd9FWb933fyvixBnYpD4/HXZvvbm"
            "fau/fJZgYEJEAfsHWCh8QHgLBJoXzJk/B4gWNDMQBZhZoABmKQBjiKEO"
        ),
    },
    "gear": {
        16: (
            "eNpdj8sJgEAMRCeuaBFahj14sAjtYM+LrYg1iDVoP4Kfi58x6C2BQB5MkhlAxCErywxOBMDXNVn/ICJDgH8ejzAoRPFIztt5"
            "bjM5xpFL2uPiV9fRJk6XJt5r3683J4W88TuXAigW7r7JK9WxQ5qi04GVZau39+w/68f6tXlg8r4tR3Hh"
        ),
        24: (
            "eNp1UrsKg0AQnDstUmhrEQIhTT4toJWFH5LCT5H0YqH5H0Xk9Ca3JoQU2WHv2JuBfR4QYPAD8+MZi6zt+zaDNV/BhhPbCwMu"
            "Nv4QciddBSTjuo4JUHXJLhiTdmR+vTvv3f2ak11qJPLhyYVigt17HkIWG1X0nnSrC0bxqygEMhHyZfMiCem3JUf0Luk4Cd0U"
            "RSPCdNzJ7Hyq6TaW8ii5Odancwa080iufCAOwCO4HOcWGChJeZOOYnujpOag81ocLa9Wp9aXMgd1bsqc1b2oe1T3/vefvAAF"
            "YP29"
        ),
    },
    "plus": {
        16: (
            "eNpjYAADRkYG3ICJweHMGQcgBQXMDCH//4cAKQiPmY056M+fICDFDFPh+v+/K4ztEBAU0P7/fzuQcgBaxHD1PxxcBdmLykdX"
            "j2kepn2o7sF0LxYA9y8AO7M2PQ=="
        ),
        24: (
            "eNqlkUEKgDAMBFNFSW/+v38Q/JGSfsB7YV09qaQqOPSwTGnTJiJvtES+EqRL45g6hpvXFVjV8XMps+cNsIsPpAlx95GBnE/0"
            "u+8vRlWjDhnIA4PqsdtKssXMcgFKZlgsUXJNuDE9e/+eWt36O5/+5fXhpW+VPvtz+T33Dd1rdsE="
        ),
    },
    "moon": {
        16: (
            "eNpjYGBgYGZAAUwMrK4ejIwwLjND6PU/lkBRGLf4//9OuB5mBuv/v/+aMyL42////SEDV84g+PH//9/KCL4GkPs/mJEFxpf5"
            "CeTvZ2CFKmBkvvL3z5//JQwMLCwgIRaGnP8///3538YHlWdi2fP/9+/f/+9Na3QEmcrIyLf6PxjslWcCORqIPeYeOzbbBcwE"
            "CUC9guQlFkZGFoiLAS5dOMs="
        ),
        24: (
            "eNqFkrFKA0EQhmdm14iCiFdGtBFB0lr5AAm+gLG3t1fwAQQlha02FjbmBbSzMIV1tFKwUvEFEi97N797dxizq5Cfbfab5Z/h"
            "nyWqxMYy/ZWh/8RMc63jbZIQ++v+M56WJHRiSm6AwXpkxjL/gIFexz0MnSPNsMs2wpvIFNqIulq6gFMMl0POZF+QK9xayIVW"
            "hlDkaLIJeQOeO5ySDfnqV/n+Y0Ek8J959RQZzqjGwZyX6lAU9kgmMjW0hYJrjoMybx4XrjAqCor7naSKscpnsY+Rllb4vLs9"
            "mZWfkeo9D51zaQo8brCMZ60dvaPU26EQTy4maXe63U47oSCO3wxMtH3/H4w/TFP0DVsLfUc="
        ),
    },
    "sun": {
        16: (
            "eNpNTzEOgzAMvIRkgbBQlX6ACirRBb4VvsMaJiTGDmVh6gP4CywMCEQdQFVPsnWWzvYdAAdAGFDjOMAdtCXEOXoZKfoGArG0"
            "4nwruEwjyYs5oRUOXQOuAuu0vSAE4JtxMOrgBGY2QrXza/16eNOyrsuk7qa8/M3u8/O+7aJq1zNmub2hzDAan5471qTuGJQL"
            "1Hp/n8zkJ0rJz5bbLDImq01PNPPOPAJlC+cXjyoIcQT/AgrjNeA="
        ),
        24: (
            "eNp9UTGOwkAMHHsTiERQqICGz6RPBa+JRHEVh3gAz0h/VYAEJN5ARQkPQEoEvt0suRyncN6VbI1mvWMP8E+Qud4yflYNbM5A"
            "rnVZhwsmBI+zxhuQO+uDD4afJzBpM1dsmnDvKNsJswIU8ySVvcdUdfdzCclwoGgmu/6zGWMU6hQtFpFO0yHYqjFUHqeiIx0T"
            "fili18mkKMtCMse1bDjdrqsQSWH4hURQFv+4XL6A1b00eHlfgZLTKW7Bkd1un219/CDw3v9rdVKt02gmOxhjOG3mCkc/c/V3"
            "MqNKHlMouV/NReztJW32tpVjr9obq/nG7BlJXq37sO5wY5lmnB+Bfq1NevURVxn88dG6HS+9V9/b4hviZXUK"
        ),
    },
    "import": {
        16: (
            "eNpjYMAKotKZkXiMDI/+swFJBP/8ayQ+IyvL5fdcLExIOs6/gzOZGDyWz3n3c94yTwaQCiZWJuFL/////X9VBMiEmCZ099/f"
            "R6JgaQarHEZmBuPf/60ZmBlzrBgYev+zMrIxpOQxsDGy/u9lYGj6DLeH6XMTA0PLZw4WVhY2NiDB8bmFgaH2/5fvUPDlfy0D"
            "g1RFcwsUNFdIYXgUACRUN3w="
        ),
        24: (
            "eNqNkrFKA0EQhv+dHTBNCgvjM1ikExtt9NA3sJLjJAGLBM5AQF/A3sr6UkkgdRKx9iHESnwKyR75ndN4xotIvmZ3P2aW+ZcF"
            "vnGqgrUR7AwGB/BV73FCXkBX/WEIyV/+iDxf1zvd0GOyrTV11Y5d8rQ6Y/M67d2R973LqybKdE4az1zw0hC31LD1GmbkLLxt"
            "l+XensVj7z2fz/Owb1vRn9SKM4bAdjmooJtFVqS4IW9t8YiyLsRjyr4dneLhCTa9os8pvMcwdIpu5+qbcMWNnTAs/IipxTSs"
            "1qhpytGXb/2O2Vr4PIuTuCSJs/zTj7nCGF4QTR4rTCL88wPESwW7BB+g8XgE"
        ),
    },
    "export": {
        16: (
            "eNpdjjEOglAMhv+W94QzMHkOFkcXvQm7LCxA4sRNTDyEgyYOxncDZ2MYHtEFUx/4wMQvaZumf/8W6CGA8SPAYunSCCN+tPNJ"
            "QRQcRM663xrGaifvTvaa6bu8MsdndzLr0UID12Yog9oFmSZ0YuUtCZf7zNslKbtLN3E9pwlQiyamzVYRaamBwk6fsi2AykZK"
            "q7BPka2AXNqXp5UciLOy8pRZjH8+ijE3KA=="
        ),
        24: (
            "eNptkTFuwkAQRb93Vg4XSJFbpIK0ibkAUqRUjiPTgUTDKbgArVsiLDqDFClSpNTp6dLkCikAWz8DJmB7ebJm7b/r8fMucMLz"
            "cAlzuBwsJlMtbvxIPjsTgtvfPN909KbW27v+ZlHw56b2DTV554bc8sNDxUr8Vx5JfVMxbGfp4pP8WqRZu2nbIZ8cTfGlS8Zy"
            "JY7oA/lS9Rdr6rmxUl1/XxTReb3BMAm0CrR/X3ODIBnCCFYc66Pgbr3u6WAx5goimO0G5evl/lsMdrN9PufItqwisq8tO+K8"
            "zOO6cnzM8ySMwhNRmOSHPKNDBlGt5VuDZXDxpP//TEwDbYI/efZ3zg=="
        ),
    },
    "pencil": {
        16: (
            "eNpjYIABRmYGZMDIwMCExGViEDBnYEbicuz94wJXAeTu/P/nWxAjE4L76/f/fIgOCPfP/2yIehg3h4EFzGVihXJZwfYyMh/9"
            "/xPOZWDk1p3w/xecy8xo89qg7X8mlAu0YMn/b1p2CLeqvp5rw4PkUgVFsCokwIzMAwDpjCz2"
        ),
        24: (
            "eNpjYCAOMOISxirBxMDOwIQpw8wgfKGRgYURQ1j0/P//NUBdmMK//vxvQZUAC//+///H/wwgG0P49//DMkhWMzHwnYYIH+Vj"
            "QBE+ChdmIluY+wgWYUYGwfNYhBkY2ZlX/f+FIczM0NXOsOT/d3TVjFxP/pczzP9/GEWYgYUh4u/X/50M1cKowcLEcOD//9sd"
            "XGhRxcxg+39HGFAULdSZGBwtwNLYYo+ZEasoNrUAaF9jPw=="
        ),
    },
}
APP_ICON_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAJxUlEQVR42u2bf4xcVRXHP+fe++bNzM52d7vSUBsqLViNLQYo"
    "WpMGi0sN0UYiYGsb0fojKjHYooKQaLL2HyMVtBY1aKJSUSlsAiKKvwulggHkh1IR22orWIFtt93tdmd25r17j3/M7ILQ3e52"
    "Z3RaPMnL/PHmze75nu/93nPuO0c4knV3G9Z9QUEUoO3qb3aphgsVv1gCc0DbAUtzmQfpV8Nuwd4vYn4ycO0ntlRvqdD9BWHd"
    "uvDSh+RlP7P8NkvPCg/QevXGSwW5HGWRuAgNHrwHDTSliQFrEWPRNAHhQUW/Pnjtmh+81LcjA9Dd7Vi3Lm1dc+1rJdtyo2Qy"
    "XfgUTcpVhFUEQY4IXHOYoiiiCliJYrAOrVS26PDQZYMbr9454uPLAajdaPv0dedrlLtVnOvU4VIKGATD8WhKAIJkc07TtE+S"
    "0nsHvnLlb18MQhWA5cstPT2+7Yovd2k2fzeqMWmSIuI4EUw1xUUOkbIMF985sOGqLSM+S1Xw1mnbZzaeqlYeRaSdNPGIWE4k"
    "U/W4yKLaL17PHrh+zR66u8XUbqL4TRJl2muRP7GcBxCxpEkqUaZd8ZtQfUEDpn1mw0rJt9yixcNNT3uLIqKoCgqIKAIEFcJE"
    "tFk1lXzBaXFo1aHrr9gsLL/Nts7e+7CJ4zO1UglNuL8DYFAUOByyeLUY8VgCiVrAEJsKeVMhqKDjA+ElkzGhXH588OlZb3Jt"
    "s/eeq9adpZWyQnNS30pgKMSIQlfhryxt/Suvi58nJwkHfAuPl2Zx9+B8nijNomCHcYTx2GC1Ulax7qy22XvPdQEuNi5CK2lT"
    "Rt9KoN/nODO7l/WvvoOuwg6MpKCmuoJFWdnxIJ/3v+SmA4vofn4ZxRCRlXQ8EIK4yAafXuxAFmvw1JKcpnN+wOe4oPAUt7zm"
    "u7TbIodDnqA18RJAQQEngctn/JY35f/BJXs+ygGfJx4LBBXR4AFZbIA5eE+zJTsGpRgyLMg+y49e8z1aTIVDvgVDwEnASsBS"
    "/XQSUKA/aWNRyy42zb65KoxjRVQweA8wxwi0NWtuH9Rw7cw76XBDFEOMEz/2LgdkJGUgncb507bzsc77OeRzOBnDNw0ItDVl"
    "mmtQDoeYt7TsZmnhKYZ8jmgc51+6bFIf85HpD9BmS6Q6jnuCacoc34iSqqOrsANnKniVSYFX1oh5cS8Lsv+iGDIYdJzvN2UN"
    "A0LgtZleYPLaHFTImIS5mf2kajBynAFQpaeSM+kUKm8lZ5KjPt+UAAigatmXFmoF/rH4b9iXtiLoSNp/nDEA5ZHSKccU/0g8"
    "B30LT5ZPJjbJuDVCUwLgVcibMr8afD29STuxSY+W349aqoasLXPf4dPZWT6JnEnGfbZJRVDImpR/VDq5Yf8SYluqFT1HET8E"
    "J4FyiFi/bymWgOpxqAEjkZxmS1y373zu6j+L9miAVC3+CP+y1r5vUPJuiGuefTcPDM2lYMtHLZHd5PZnwYg0mP5hVLQExRJ4"
    "/9Or+YbP8r7pD4JaSiGDR1AVRJRIPC22RCnErH1mFTf0LaHdFvF69Pi6iR+oCEOVhCRJGwpASzYm4ww+KIoQiSfFsPqZD3D3"
    "4Hw+3vk7zszuZZodrp56qqHXF7h34I18dV8XDxVPpd0WJ3Y4Asi0KzfoRCI/nKQsPm0W58yeiaoidWVCtaRLQ2DzI0/x3OAQ"
    "bbmY1IdRJgjQ73PEJmVe3MucTB85qXDAt7CzPIM9lelE4inY8oQiPykGGBGGyxXeteB01p63sKEMWL1oAatuuos//2s/nYUc"
    "iQ8o1eOvDlckqLCjPIPtwzNRFYwoWUnpcEVUZVLOT04Ea0sgDYHhNCUNoe5X4gNnvPoktq5dxTvmz6XvUBFnzCiZvRoUIScJ"
    "7bZEhyvSZoaJJMWrmTDtj3kXMCI4Yxp2Rba69jtbcvz0sku4/G0LOXC4CMJ/iG+gGmmvpiqGUzjJabpt0BohaNWlG5Yv5Wsr"
    "llIsp1S8xzageG3SclhABB8Ca5Ys5I6PXUQ+ijhcruCsOfEBGCmIrDGkIbBs/lzuWbuSeTM6OHC4RFRHEJr+paergbBg5qvG"
    "FMemACCo1pIX8CEQVOsKwkTE8X8GgKpiRLBGRqlrRNA6gtAocXT1cF5E+Mvzfaz/9UPs2X+QeSd3cvXbFzG3s72uWaMRGWXY"
    "miULOe1VHXzw5rsZGC7Tms2MZo7/NQYEVRBhR+9Bur62mZse+CMP7HmWb299lPM33soz/YPV0706MmE8cTyW5TBlAATYuPUR"
    "nusfZEZ7K/lMxIyOaezpPcCN2x5HhLoCcCRxvGfNSi4843QS7yfNNjPl/Rr42/5+XMaReE9QJfEBm3Hs2n+wFjVp2A5RTj0n"
    "FfJ8a9UFTMvGpGFyCfHUlwBwziknkw5XiKzFGkNkDH444c2zZ452LjXk0CQEYmd57J+9dG3cTH+pjDNmUn/NTe3lZVXp15x3"
    "Nr948u/84e97kcihScJb3zCHjy5+I6qKFVPnbhcIGnDGcOefdvHhH/6cwXKFlkw06eXmptZ1UgXgpEKe36x5L9/9/RPseK6P"
    "BbNm8KG3LCCfiajpJPXMN0QEK4brtzzMNXduJXaOQhzhg/73t8EqCNCWjfnU2855+RueOjrvg2KNkIbAJ3t+w433PUZbSw6p"
    "3fuf5AG1owJUFf8i+lkxdXU+DVXK9w4WufT7P+XXT+5meiFfzTqnIqT1a8ISXIMOTEec/+PeXlZ+7y6eer6PztY8iZ/6a33X"
    "3K19Rxa76S25ujjf1NVgNcusZn3Xb3mY93znx5RTTyGOjinlPa4Y0AixO24AaJTY1QWA6prU0av+a14bJnZjA6CEifYJZVy1"
    "zs9Y26h+3oaJ3Vjt9E5hQMR0jNcp5lXJxxk2Pbide3c+04A3Qy/Qf9uufxJU6y52R5ouUQ0DDtiNtR0kYUwmqCqRM+zsPcj2"
    "Z/c39CC0Nc4gYuoudi8bpHDWEMJuB3q/GHu2SkXH66dRhThy5DKu4TuAqtLg/iMVY1Eq9zsDt2uafHIiOUE13eVEMKNpgoHb"
    "zcDTs7apTx+TTFwbPTvhzUsmRn362MDTs7YZelZ4QdZjI2k895oiv1ZsJIKsp2eFt3R3m/IXr9ke/+y+Lsnm59RGZswJ6nwq"
    "2bzT0tC2Q9ddcSWMtMqKINjVmlT6cZFD1Z+Azntc5DSp9At29Uit/oofm6syoKfH093tBjZctUUqpWUgfZLNO5S0NnzIcTs4"
    "qaSSzTuQPqmUlg1suGoL3d2Onh7Pf4zIbN0a6O525S997m+ZhUvuwNj5ks2eJkaEkI6Mzo5wptlHZwNgJBOLZGKjSbJFh4cu"
    "OrThs38Ye3SW/w9P80ocn/835VdnC4YtbSsAAAAASUVORK5CYII="
)
# --- END GENERATED ICON DATA ---


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def data_dir():
    """Prefer the folder next to the exe (portable); fall back if read-only."""
    base = app_dir()
    probe = os.path.join(base, ".write_test_%d" % os.getpid())
    try:
        with open(probe, "w") as f:
            f.write("x")
        os.remove(probe)
        return base
    except OSError:
        root = os.environ.get("APPDATA") or os.path.expanduser("~")
        path = os.path.join(root, "GitHubReleaseTracker")
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except OSError:
            return base


DATA_FILE = os.path.join(data_dir(), "projects.json")


# --------------------------------------------------------------------------
# GitHub API helpers
# --------------------------------------------------------------------------
class GitHubError(Exception):
    pass


class NotFoundError(GitHubError):
    pass


class RateLimitError(GitHubError):
    pass


class NetworkError(GitHubError):
    """The server could not be reached at all (DNS, refused, timeout, certificate)."""


class NoReleasesError(GitHubError):
    pass


# Remaining API calls reported by the last response (None = unknown).
last_rate_remaining = None


def api_get(path, token=""):
    global last_rate_remaining
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GitHubReleaseTracker",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            remaining = resp.headers.get("X-RateLimit-Remaining")
            if remaining is not None and remaining.isdigit():
                last_rate_remaining = int(remaining)
            return json.load(resp)
    except urllib.error.HTTPError as e:
        remaining = e.headers.get("X-RateLimit-Remaining") if e.headers else None
        if e.code in (403, 429) and remaining == "0":
            reset = e.headers.get("X-RateLimit-Reset", "")
            when = ""
            if reset.isdigit():
                when = " Resets at " + datetime.fromtimestamp(int(reset)).strftime("%H:%M") + "."
            last_rate_remaining = 0
            raise RateLimitError("GitHub API rate limit reached." + when +
                                 " Add a token in Settings for a higher limit.")
        if e.code == 404:
            raise NotFoundError("Not found (wrong name, or a private repository).")
        if e.code == 401:
            raise GitHubError("GitHub rejected the token (401). Check it in Settings.")
        raise GitHubError("GitHub returned HTTP %d." % e.code)
    except urllib.error.URLError as e:
        raise GitHubError("Network error: %s" % e.reason)
    except (TimeoutError, OSError) as e:
        raise GitHubError("Network error: %s" % e)
    except ValueError:
        raise GitHubError("Unexpected response from GitHub.")


def parse_repo(text):
    """Accept https://github.com/owner/repo[/...] or owner/repo."""
    text = (text or "").strip()
    m = re.match(r"^(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", text)
    if not m:
        m = re.match(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$", text)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    if repo.endswith(".git"):
        repo = repo[:-4]
    if not repo:
        return None
    return owner, repo


def fetch_repo_info(owner, repo, token=""):
    d = api_get("/repos/%s/%s" % (owner, repo), token)
    full = d.get("full_name") or "%s/%s" % (owner, repo)
    real_owner, real_repo = full.split("/", 1)
    return {
        "owner": real_owner,
        "repo": real_repo,
        "title": d.get("name") or real_repo,
        "description": d.get("description") or "",
        "html_url": d.get("html_url") or "https://github.com/" + full,
    }


def _release_dict(r):
    return {
        "id": r.get("id"),
        "tag": r.get("tag_name") or "",
        "name": r.get("name") or "",
        "published_at": r.get("published_at") or r.get("created_at") or "",
        "url": r.get("html_url") or "",
        "prerelease": bool(r.get("prerelease")),
        "source": "release",
    }


def _newest_release(owner, repo, token):
    """Newest non-draft release, pre-releases included. None if there are none."""
    try:
        data = api_get("/repos/%s/%s/releases?per_page=10" % (owner, repo), token)
    except NotFoundError:
        return None
    for r in data:
        if not r.get("draft"):
            return _release_dict(r)
    return None


def _newest_tag(owner, repo, token):
    """First tag GitHub returns. Used only when no GitHub Release exists at all.

    Caveat: the tags endpoint does not guarantee newest-first ordering, and
    tags carry no publish date.
    """
    try:
        data = api_get("/repos/%s/%s/tags?per_page=1" % (owner, repo), token)
    except NotFoundError:
        return None
    if not data:
        return None
    t = data[0]
    name = t.get("name") or ""
    sha = (t.get("commit") or {}).get("sha") or name
    return {
        "id": sha,
        "tag": name,
        "name": "",
        "published_at": "",
        "url": "https://github.com/%s/%s/releases/tag/%s" % (owner, repo, urllib.parse.quote(name, safe="")),
        "prerelease": False,
        "source": "tag",
    }


def fetch_latest_release(owner, repo, token="", include_prereleases=False):
    """Return the latest version info dict, or None if the project has nothing.

    Order of preference:
      1. newest stable GitHub Release (or newest incl. pre-releases if enabled)
      2. newest pre-release, when no stable release exists
      3. newest git tag, when no GitHub Release exists at all
    """
    if not include_prereleases:
        try:
            return _release_dict(api_get("/repos/%s/%s/releases/latest" % (owner, repo), token))
        except NotFoundError:
            pass  # no stable release; fall through to pre-releases / tags
    rel = _newest_release(owner, repo, token)
    if rel:
        return rel
    return _newest_tag(owner, repo, token)


FEED_NS = "{http://www.w3.org/2005/Atom}"


def fetch_latest_from_feed(owner, repo):
    """Newest release from the public releases.atom feed (no token, no API quota).

    The feed lists every published release, pre-releases included, newest first.
    It does not say which entries are pre-releases. Returns None if it is empty.
    """
    url = "https://github.com/%s/%s/releases.atom" % (owner, repo)
    req = urllib.request.Request(url, headers={
        "User-Agent": "GitHubReleaseTracker",
        "Accept": "application/atom+xml, application/xml;q=0.9, */*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise NotFoundError("Not found (wrong name, or a private repository).")
        if e.code == 429:
            raise GitHubError("GitHub is rate-limiting the release feed (429). Try again later.")
        raise GitHubError("Release feed returned HTTP %d." % e.code)
    except urllib.error.URLError as e:
        raise GitHubError("Network error: %s" % e.reason)
    except (TimeoutError, OSError) as e:
        raise GitHubError("Network error: %s" % e)
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        raise GitHubError("Release feed was not valid XML.")
    entry = root.find(FEED_NS + "entry")
    if entry is None:
        return None
    entry_id = (entry.findtext(FEED_NS + "id") or "").strip()
    title = (entry.findtext(FEED_NS + "title") or "").strip()
    updated = (entry.findtext(FEED_NS + "updated") or "").strip()
    href = ""
    for link in entry.findall(FEED_NS + "link"):
        if link.get("rel", "alternate") == "alternate":
            href = link.get("href") or ""
            break
    marker = "/releases/tag/"
    if marker in href:
        tag = urllib.parse.unquote(href.split(marker, 1)[1])
    else:
        m = re.search(r"Repository/\d+/(.+)$", entry_id)
        tag = m.group(1) if m else ""
    if not (entry_id or tag):
        return None
    return {
        "id": entry_id or tag,
        "tag": tag,
        "name": title,
        "published_at": updated,
        "url": href or "https://github.com/%s/%s/releases" % (owner, repo),
        "prerelease": False,  # not reported by the feed
        "source": "feed",
    }


def get_latest(owner, repo, token="", include_prereleases=True):
    """Feed first (free, no quota); GitHub API as fallback.

    Stable-only mode needs the API, because the feed does not mark pre-releases.
    """
    if include_prereleases:
        try:
            rel = fetch_latest_from_feed(owner, repo)
            if rel:
                return rel
        except GitHubError:
            pass  # feed unavailable or repo has no releases: try the API
    return fetch_latest_release(owner, repo, token, include_prereleases)


# --------------------------------------------------------------------------
# Other hosts: GitLab, Gitea / Forgejo (Codeberg) and self-hosted servers.
# Public repositories only, no token, official releases only (not bare tags).
# A GitHub project has no "host" / "kind" keys, so GitHub-only files stay as they were.
# --------------------------------------------------------------------------
KNOWN_HOSTS = {   # host -> kind ("gitea" also covers Forgejo, which speaks the same API)
    "gitlab.com": "gitlab",
    "codeberg.org": "gitea",
    "gitea.com": "gitea",
    "code.forgejo.org": "gitea",
}
SEG_RE = re.compile(r"^(?!\.+$)[A-Za-z0-9_.-]{1,100}$")
HOST_RE = re.compile(r"^(?:http://)?[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?(?::\d{1,5})?$")
KINDS = ("gitlab", "gitea")
MAX_BODY = 2 * 1024 * 1024
MAX_PATH_SEGMENTS = 20


def host_base(host):
    """Base URL of a stored host: "codeberg.org" -> https://codeberg.org, "http://x:3000" stays http."""
    return host if host.startswith("http://") else "https://" + host


def host_label(host):
    return host[len("http://"):] if host.startswith("http://") else host


def parse_project_ref(text):
    """Understand a pasted project reference.

    Returns (host, kind, segments) or None.
      - host "" = github.com (segments = [owner, repo]);
      - otherwise host is "example.org" (https) or "http://example.org:3000" (only when typed so);
      - kind is "gitlab" / "gitea" for known hosts, None for unknown servers (found out later).
    """
    text = (text or "").strip()
    gh = parse_repo(text)
    if gh:
        return "", None, [gh[0], gh[1]]
    m = re.match(r"^(https?)://([^/\s?#]+)([^?#\s]*)", text, re.I)
    if m:
        scheme, netloc, path = m.group(1).lower(), m.group(2).lower(), m.group(3)
    else:   # "codeberg.org/owner/repo" without the scheme
        m = re.match(r"^((?:[a-z0-9-]+\.)+[a-z0-9-]+(?::\d{1,5})?)/([^?#\s]*)$", text, re.I)
        if not m:
            return None
        scheme, netloc, path = "https", m.group(1).lower(), "/" + m.group(2)
    if "@" in netloc or netloc in ("github.com", "www.github.com"):
        return None
    host = netloc if scheme == "https" else "http://" + netloc
    if not HOST_RE.match(host):
        return None
    kind = KNOWN_HOSTS.get(netloc)
    path = path.split("/-/")[0]
    if path.endswith("/-"):
        path = path[:-2]
    segs = [x for x in path.split("/") if x]
    if segs and segs[-1].endswith(".git"):
        segs[-1] = segs[-1][:-4]
    if len(segs) < 2 or len(segs) > MAX_PATH_SEGMENTS or not all(SEG_RE.match(x) for x in segs):
        return None
    if kind == "gitea":
        segs = segs[:2]
    return host, kind, segs


def split_path(segs):
    return "/".join(segs[:-1]), segs[-1]


def http_json(url):
    """GET a public JSON document (no credentials are ever sent)."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "GitHubReleaseTracker",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read(MAX_BODY + 1)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise NotFoundError("Not found (wrong name, or a private repository).")
        if e.code in (401, 403):
            raise GitHubError("The server asks for a sign-in (HTTP %d). Only public repositories "
                              "work, and tokens are not supported for this host." % e.code)
        if e.code == 429:
            raise GitHubError("The server is rate-limiting requests (429). Try again later.")
        raise GitHubError("The server returned HTTP %d." % e.code)
    except urllib.error.URLError as e:
        raise NetworkError("Network error: %s" % e.reason)
    except (TimeoutError, OSError) as e:
        raise NetworkError("Network error: %s" % e)
    if len(body) > MAX_BODY:
        raise GitHubError("The server's answer was too large.")
    try:
        return json.loads(body)
    except ValueError:
        raise GitHubError("Unexpected answer (not JSON). This does not look like a GitLab or Gitea/Forgejo server.")


def _api_url(base, kind, path, tail=""):
    if kind == "gitea":
        return "%s/api/v1/repos/%s%s" % (base, "/".join(urllib.parse.quote(x, safe="") for x in path), tail)
    return "%s/api/v4/projects/%s%s" % (base, urllib.parse.quote("/".join(path), safe=""), tail)


def _host_info(base, host, kind, path):
    d = http_json(_api_url(base, kind, path))
    if not isinstance(d, dict):
        raise GitHubError("Unexpected answer from the server.")
    full = d.get("full_name") if kind == "gitea" else d.get("path_with_namespace")
    if not (isinstance(full, str) and full):
        raise NotFoundError("Not found on this server.")
    parts = full.split("/")
    if not (2 <= len(parts) <= MAX_PATH_SEGMENTS and all(SEG_RE.match(x) for x in parts)):
        raise GitHubError("Unexpected project name from the server.")
    owner, repo = split_path(parts)
    page = base + "/" + full
    url = d.get("html_url") if kind == "gitea" else d.get("web_url")
    return {
        "owner": owner,
        "repo": repo,
        "title": _s(d.get("name"), 200) or repo,
        "description": _s(d.get("description"), 500),
        "html_url": safe_url(url, base, page),
        "host": host,
        "kind": kind,
    }


def _host_release(base, kind, owner, repo, r):
    """One release object from the server -> this app's release dict (None if unusable)."""
    if not isinstance(r, dict) or r.get("draft"):
        return None
    tag = _s(r.get("tag_name"), 200)
    if not tag:
        return None
    full = "%s/%s" % (owner, repo)
    if kind == "gitea":
        rid = r.get("id") if isinstance(r.get("id"), int) and not isinstance(r.get("id"), bool) else tag
        when = r.get("published_at") or r.get("created_at") or ""
        url = r.get("html_url")
        fallback = "%s/%s/releases/tag/%s" % (base, full, urllib.parse.quote(tag, safe=""))
        pre = bool(r.get("prerelease"))
    else:
        if r.get("upcoming_release"):   # dated in the future: not released yet
            return None
        rid, pre = tag, False
        when = r.get("released_at") or r.get("created_at") or ""
        links = r.get("_links") if isinstance(r.get("_links"), dict) else {}
        url = links.get("self")
        fallback = "%s/%s/-/releases/%s" % (base, full, urllib.parse.quote(tag, safe=""))
    return {
        "id": rid,
        "tag": tag,
        "name": _s(r.get("name"), 300),
        "published_at": _s(when, 40),
        "url": safe_url(url, base, fallback),
        "prerelease": pre,
        "source": "release",
    }


def fetch_latest_host(host, kind, owner, repo, include_prereleases=True):
    """Newest official release of a project on another host, or None if it has none."""
    base = host_base(host)
    path = (owner + "/" + repo).split("/")
    data = http_json(_api_url(base, kind, path, "/releases?%s=10" % ("limit" if kind == "gitea" else "per_page")))
    if not isinstance(data, list):
        raise GitHubError("Unexpected answer from the server.")
    rels = [x for x in (_host_release(base, kind, owner, repo, r) for r in data) if x]
    if not rels:
        return None
    if not include_prereleases:
        for r in rels:
            if not r["prerelease"]:
                return r
    return rels[0]


def resolve_project(host, kind, segs, include_prereleases=True):
    """Add-time lookup on another host: find out what the server is, check that the project
    exists and has an official release. Returns (info, latest)."""
    base = host_base(host)
    last = None
    for k in ([kind] if kind else ["gitea", "gitlab"]):
        path = segs[:2] if k == "gitea" else segs
        try:
            info = _host_info(base, host, k, path)
            latest = fetch_latest_host(host, k, info["owner"], info["repo"], include_prereleases)
        except NetworkError:
            raise                      # the server is not reachable: trying another kind will not help
        except GitHubError as e:
            last = last or e
            continue
        if not latest:
            raise NoReleasesError("%s has no official releases (only tags, or nothing yet), "
                                  "so it cannot be tracked." % info["title"])
        return info, latest
    if kind or isinstance(last, GitHubError) and not isinstance(last, NotFoundError):
        raise last
    raise NotFoundError("Could not find this project on %s. It must be a public repository on a "
                        "GitLab, Gitea or Forgejo server." % host_label(host))


def fetch_latest_for(p_host, p_kind, owner, repo, token, include_prereleases):
    """Latest release for a GitHub project (host "") or one on another host."""
    if not p_host:
        return get_latest(owner, repo, token, include_prereleases)
    return fetch_latest_host(p_host, p_kind, owner, repo, include_prereleases)


def apply_result(p, latest, err, now):
    """Store one check result on project p, without inventing false updates."""
    p["last_checked"] = now
    if err:
        p["error"] = err
        return
    p["error"] = None
    if latest:
        if p.get("seen_tag") and p["seen_tag"] == latest["tag"]:
            # Same release as the one already seen; only the ID scheme differs
            # (API release ID vs feed entry ID), so carry the acknowledgement over.
            p["seen_id"] = latest["id"]
        elif p.get("fmt") != 2 and p.get("seen_id") is None:
            # Entry saved by an older version that found nothing: treat what
            # exists now as the baseline instead of flagging it.
            p["seen_id"], p["seen_tag"] = latest["id"], latest["tag"]
    p["latest"] = latest
    p["fmt"] = 2


# --------------------------------------------------------------------------
# Storage, import and export (all input is treated as untrusted)
# --------------------------------------------------------------------------
NAME_RE = re.compile(r"^(?!\.+$)[A-Za-z0-9_.-]{1,100}$")   # no "." / ".." (path tricks)


def _s(value, limit=300):
    return value.strip()[:limit] if isinstance(value, str) else ""


def safe_url(url, base, fallback):
    """Only ever open links that live on the project's own host, whatever a JSON file says."""
    if (isinstance(url, str) and url.startswith(base + "/") and len(url) < 500
            and not any(c.isspace() for c in url)):
        return url
    return fallback


def safe_github_url(url, fallback):
    return safe_url(url, "https://github.com", fallback)


def project_base(p):
    return host_base(p["host"]) if p.get("host") else "https://github.com"


def repo_page(p):
    return "%s/%s/%s" % (project_base(p), p["owner"], p["repo"])


def release_page(p):
    """The page listing the project's releases (used when no exact release link is known)."""
    tail = "/-/releases" if p.get("kind") == "gitlab" else "/releases"
    return repo_page(p) + tail


def repo_label(p):
    """The full address (host first for other servers); used by the search box."""
    full = "%s/%s" % (p["owner"], p["repo"])
    return "%s/%s" % (host_label(p["host"]), full) if p.get("host") else full


def repo_path(p):
    """What the Repository column shows: owner/repo (the host is in the Source column)."""
    return "%s/%s" % (p["owner"], p["repo"])


# Known hosts get a friendly name in the Source column; any other server shows its own address.
SOURCE_NAMES = {"github.com": "GitHub", "gitlab.com": "GitLab", "codeberg.org": "Codeberg"}
_SOURCE_ORDER = ("GitHub", "GitLab", "Codeberg")


def source_label(p):
    """Where the project lives: GitHub, GitLab, Codeberg, or the server's address."""
    host = p.get("host")
    if not host:
        return "GitHub"
    shown = host_label(host)
    return SOURCE_NAMES.get(shown.lower(), shown)


def _source_key(p):
    name = source_label(p)
    return (_SOURCE_ORDER.index(name) if name in _SOURCE_ORDER else len(_SOURCE_ORDER), name.casefold())


def _id_value(value):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    return value[:300] if isinstance(value, str) else value


def normalize_release(r, base, fallback):
    if not isinstance(r, dict):
        return None
    tag = _s(r.get("tag"), 200)
    rid = _id_value(r.get("id"))
    if rid is None:
        rid = tag or None
    if rid is None:
        return None
    source = r.get("source")
    return {
        "id": rid,
        "tag": tag,
        "name": _s(r.get("name"), 300),
        "published_at": _s(r.get("published_at"), 40),
        "url": safe_url(r.get("url"), base, fallback),
        "prerelease": bool(r.get("prerelease")),
        "source": source if source in ("release", "tag", "feed") else "release",
    }


def clean_name(value):
    """A user-chosen display name: one line, single spaces, at most MAX_CUSTOM_NAME characters."""
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())[:MAX_CUSTOM_NAME].strip()


def display_name(p):
    """What the Project column shows: the user's own name if set, else the GitHub name."""
    return p.get("custom_name") or p.get("title") or p["repo"]


def normalize_project(raw):
    """Return a clean project dict from untrusted input, or None if unusable."""
    if isinstance(raw, str):
        ref = parse_project_ref(raw)
        if not ref or (ref[0] and not ref[1]):   # an unknown server cannot be identified offline
            return None
        owner, repo = split_path(ref[2])
        raw = {"owner": owner, "repo": repo}
        if ref[0]:
            raw["host"], raw["kind"] = ref[0], ref[1]
    if not isinstance(raw, dict):
        return None
    owner, repo = raw.get("owner"), raw.get("repo")
    host, kind = raw.get("host"), raw.get("kind")
    if host in (None, "", "github.com"):
        host = kind = None
        ok = (isinstance(owner, str) and isinstance(repo, str)
              and NAME_RE.match(owner) and NAME_RE.match(repo))
    else:
        host = host.lower() if isinstance(host, str) else ""
        ok = (HOST_RE.match(host) is not None and kind in KINDS and isinstance(owner, str)
              and isinstance(repo, str) and bool(NAME_RE.match(repo))
              and 1 <= len(owner.split("/")) < MAX_PATH_SEGMENTS
              and all(SEG_RE.match(x) for x in owner.split("/")))
    if not ok:
        return None
    ref = {"owner": owner, "repo": repo, "host": host, "kind": kind}
    base = project_base(ref)
    fmt = raw.get("fmt")
    out = {
        "owner": owner,
        "repo": repo,
    }
    if host:   # only projects on other hosts carry these keys
        out["host"], out["kind"] = host, kind
    out.update({
        "title": _s(raw.get("title"), 200) or repo,
        "description": _s(raw.get("description"), 500),
        "html_url": safe_url(raw.get("html_url"), base, repo_page(ref)),
        "include_prereleases": bool(raw.get("include_prereleases", True)),
        "fmt": fmt if fmt == 2 else None,
        "latest": normalize_release(raw.get("latest"), base, release_page(ref)),
        "seen_id": _id_value(raw.get("seen_id")),
        "seen_tag": _s(raw.get("seen_tag"), 200) or None,
        "last_checked": _s(raw.get("last_checked"), 40),
        "error": _s(raw.get("error"), 300) or None,
    })
    custom = clean_name(raw.get("custom_name"))
    if custom:  # only present when the user renamed the project
        out["custom_name"] = custom
    return out


def parse_import(raw):
    """Return (projects, skipped_count), or (None, 0) if there is no project list.

    Accepts this app's file ({"projects": [...]}), a bare list, and lists of
    plain "owner/repo" strings or GitHub URLs.
    """
    items = raw.get("projects") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return None, 0
    seen, out, skipped = set(), [], max(0, len(items) - MAX_PROJECTS)
    for item in items[:MAX_PROJECTS]:
        p = normalize_project(item)
        if not p or project_key(p) in seen:
            skipped += 1
            continue
        seen.add(project_key(p))
        out.append(p)
    return out, skipped


def merge_projects(existing, incoming):
    """Add incoming projects that are not already listed. Returns how many were added."""
    keys = {project_key(p) for p in existing}
    added = 0
    for p in incoming:
        k = project_key(p)
        if k not in keys:
            existing.append(p)
            keys.add(k)
            added += 1
    return added


def build_export(projects):
    """Export payload. The access token is deliberately never included."""
    return {
        "app": APP_NAME,
        "format": 2,
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "projects": projects,
    }


SORTABLE = ("name", "repo", "source", "published", "status")  # columns whose header can be clicked


def _title_key(p):
    return display_name(p).casefold()


def status_rank(p):
    """Order of the Status column. Same precedence as status_text()."""
    if p.get("error"):
        return 1                      # Error
    if not p.get("latest"):
        return 2                      # No releases published
    return 0 if has_update(p) else 3  # Update available / Up to date


def sort_projects(projects, col, asc):
    """Return projects sorted by column. col "" = default (updates first, then A-Z).

    Projects without a publish date (no release, or a tag) always stay at the
    bottom for "published", whichever direction is chosen.
    Status: ascending = Update available, Error, No releases, Up to date;
    descending = the reverse, so "Up to date" comes first. Projects with the
    same status are always A-Z.
    """
    if col == "status":
        sign = 1 if asc else -1
        return sorted(projects, key=lambda p: (sign * status_rank(p), _title_key(p), project_key(p)))
    if col == "name":
        return sorted(projects, key=lambda p: (_title_key(p), project_key(p)), reverse=not asc)
    if col == "repo":
        # what the column shows (owner/repo); the full key only breaks ties
        return sorted(projects, key=lambda p: (repo_path(p).lower(), project_key(p)), reverse=not asc)
    if col == "source":
        # GitHub, GitLab, Codeberg, then other servers A-Z. Same source: A-Z by name in either
        # direction (the second sort is stable, so the name order is kept).
        by_name = sorted(projects, key=lambda p: (_title_key(p), project_key(p)))
        return sorted(by_name, key=_source_key, reverse=not asc)
    if col == "published":
        dated = [p for p in projects if (p.get("latest") or {}).get("published_at")]
        undated = [p for p in projects if not (p.get("latest") or {}).get("published_at")]
        dated.sort(key=lambda p: (p["latest"]["published_at"], _title_key(p)), reverse=not asc)
        undated.sort(key=_title_key)
        return dated + undated
    return sorted(projects, key=lambda p: (not has_update(p), _title_key(p)))


def default_data():
    return {"settings": {"token": "", "check_on_launch": False, "theme": "",
                         "sort_col": "", "sort_asc": True}, "projects": []}


def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8-sig") as f:
            d = json.load(f)
        if not isinstance(d, dict) or not isinstance(d.get("projects", []), list):
            raise ValueError("bad structure")
    except (OSError, ValueError, RecursionError):
        try:
            os.replace(DATA_FILE, DATA_FILE + ".bak")
        except OSError:
            pass
        return default_data()
    base = default_data()
    s = d.get("settings")
    if isinstance(s, dict):
        base["settings"]["token"] = _s(s.get("token"), 200)
        base["settings"]["check_on_launch"] = bool(s.get("check_on_launch"))
        base["settings"]["theme"] = s.get("theme") if s.get("theme") in ("light", "dark") else ""
        base["settings"]["sort_col"] = s.get("sort_col") if s.get("sort_col") in SORTABLE else ""
        base["settings"]["sort_asc"] = s.get("sort_asc") is not False
    projects, _ = parse_import(d)
    base["projects"] = projects or []
    return base


def write_json_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def save_data(data):
    write_json_atomic(DATA_FILE, data)


def project_key(p):
    if p.get("host"):
        return ("%s/%s/%s" % (host_label(p["host"]), p["owner"], p["repo"])).lower()
    return ("%s/%s" % (p["owner"], p["repo"])).lower()


def has_update(p):
    latest = p.get("latest")
    return bool(latest) and latest.get("id") != p.get("seen_id")


def status_text(p):
    if p.get("error"):
        return "Error: " + p["error"]
    latest = p.get("latest")
    if not latest:
        return "No releases published"
    if has_update(p):
        old = p.get("seen_tag")
        new = latest.get("tag") or latest.get("name") or "new release"
        return "Update available: %s -> %s" % (old, new) if old else "Update available: " + new
    return "Up to date"


def status_kind(p):
    """'error', 'update', 'none' (no releases) or 'ok': the same split that colors the rows."""
    if p.get("error"):
        return "error"
    if has_update(p):
        return "update"
    if not p.get("latest"):
        return "none"
    return "ok"


# Choices of the status filter (value, menu text). "all" shows everything.
STATUS_FILTERS = [("all", "All projects"), ("update", "Updates available"), ("error", "Errors"),
                  ("ok", "Up to date"), ("none", "No releases")]


def filter_projects(projects, query="", kind="all"):
    """The projects that match the search text and the status filter, in the same order.

    Every word of the search text must appear (any case) in the project name or in the
    repository address, so "emu rom" finds "Emu Roms" and "owner/emu-roms". Nothing is
    changed; this only decides what is shown.
    """
    terms = (query or "").casefold().split()
    out = []
    for p in projects:
        if kind != "all" and status_kind(p) != kind:
            continue
        if terms:
            hay = ("%s %s %s" % (display_name(p), repo_label(p), source_label(p))).casefold()
            if not all(t in hay for t in terms):
                continue
        out.append(p)
    return out


# --------------------------------------------------------------------------
# Theme
# --------------------------------------------------------------------------
THEMES = {
    "light": dict(bg="#f3f3f3", fg="#1b1b1b", field="#ffffff", sel_bg="#0078d4", sel_fg="#ffffff",
                  head_bg="#e5e5e5", btn_bg="#e1e1e1", btn_active="#d0d0d0", border="#bdbdbd",
                  update_bg="#fff3cd", update_fg="#1b1b1b", error_fg="#b00020",
                  none_fg="#777777", sub_fg="#666666", line="#d4d4d4", tip_bg="#ffffe1", tip_fg="#1b1b1b"),
    "dark": dict(bg="#202124", fg="#e8eaed", field="#2b2d31", sel_bg="#2f6fbf", sel_fg="#ffffff",
                 head_bg="#33363b", btn_bg="#3a3d42", btn_active="#4a4d52", border="#4a4d52",
                 update_bg="#4d4210", update_fg="#ffe9a6", error_fg="#ff8a80",
                 none_fg="#9aa0a6", sub_fg="#9aa0a6", line="#3d4046", tip_bg="#3a3d42", tip_fg="#e8eaed"),
}


def system_theme():
    """Windows' own app theme (dark/light); light if it cannot be read."""
    try:
        import winreg
        key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            return "light" if winreg.QueryValueEx(k, "AppsUseLightTheme")[0] else "dark"
    except Exception:  # noqa: BLE001 - not Windows / value missing
        return "light"


def set_titlebar_dark(win, dark):
    """Best effort: dark title bar on Windows 10/11. May show after a repaint."""
    try:
        import ctypes
        win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        for attr in (20, 19):  # 20 = current, 19 = older Windows 10 builds
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)) == 0:
                break
    except Exception:  # noqa: BLE001
        pass


# --------------------------------------------------------------------------
# Icons (drawn from embedded alpha masks; no image files, no extra packages)
# --------------------------------------------------------------------------
def make_png(w, h, rgba):
    """Encode raw RGBA bytes as a PNG (standard library only)."""
    raw = b"".join(b"\x00" + rgba[y * w * 4:(y + 1) * w * 4] for y in range(h))

    def chunk(kind, body):
        crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def icon_image(master, name, size, color):
    """A PhotoImage of a toolbar icon in the given color, or None if anything goes wrong
    (the buttons then simply show their text without an icon)."""
    try:
        mask = zlib.decompress(base64.b64decode(ICON_MASKS[name][size]))
        r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
        rgba = b"".join(bytes((r, g, b, a)) for a in mask)
        return tk.PhotoImage(master=master, data=base64.b64encode(make_png(size, size, rgba)))
    except Exception:  # noqa: BLE001
        return None


class Tooltip:
    """A small hover label for a widget (used on the icon-only theme button)."""

    def __init__(self, widget, text_fn, colors_fn):
        self.widget, self.text_fn, self.colors_fn = widget, text_fn, colors_fn
        self.tip, self.job = None, None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _e=None):
        self._hide()
        self.job = self.widget.after(500, self._show)

    def _show(self):
        self.job = None
        bg, fg = self.colors_fn()
        tip = self.tip = tk.Toplevel(self.widget)
        tip.wm_overrideredirect(True)
        tk.Label(tip, text=self.text_fn(), bg=bg, fg=fg, bd=1, relief="solid", padx=6, pady=2).pack()
        tip.update_idletasks()
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        x = max(0, min(x, self.widget.winfo_screenwidth() - tip.winfo_reqwidth() - 4))
        tip.wm_geometry("+%d+%d" % (x, y))

    def _hide(self, _e=None):
        if self.job:
            self.widget.after_cancel(self.job)
            self.job = None
        if self.tip:
            self.tip.destroy()
            self.tip = None


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("%s v%s" % (APP_NAME, APP_VERSION))
        self.geometry("1260x560")  # replaced below by a screen-aware size
        self.app_icon = None
        try:  # window / taskbar icon (the .exe's own icon comes from build.bat --icon)
            self.app_icon = tk.PhotoImage(master=self, data=APP_ICON_PNG)
            self.iconphoto(True, self.app_icon)
        except Exception:  # noqa: BLE001 - cosmetic only
            self.app_icon = None
        # Windows display scale (1.0 = 100%, 2.25 = 225%). Tk scales fonts by itself, but every
        # pixel size written in this file (row height, column widths, window size) must follow it.
        try:
            self.ui_scale = max(1.0, min(4.0, self.winfo_fpixels("1i") / 96.0))
        except tk.TclError:
            self.ui_scale = 1.0
        # Toolbar icons: 16 px normally, 24 px on high-DPI screens (150% and up).
        self.icon_px = 24 if self.ui_scale >= 1.4 else 16
        self._btn_icons = []      # (button, icon name) pairs, recolored when the theme changes
        self._icon_refs = []      # PhotoImages must stay referenced or Tk blanks them
        self._pencil_imgs = {}
        self._editor = None       # inline rename box: (entry, row id, project)
        self._suppress_select = False  # True while render() restores the selection (see _on_select)
        self._col_base, self._col_min = {}, {}   # preferred / minimum column widths (see _layout_columns)
        self._tree_w, self._col_drag = 0, False
        self._lines, self._lines_job, self._lines_state = [], None, None
        self._vlines, self._head_h = [], None   # column lines; measured height of the header row
        self._hsb_shown = False
        self._xorg = 2
        self.data = load_data()
        self.theme_name = self.data["settings"].get("theme") or system_theme()
        self.sort_col = self.data["settings"].get("sort_col") or ""
        self.sort_asc = self.data["settings"].get("sort_asc") is not False
        self.busy = False
        self.q = queue.Queue()
        self._build_ui()
        self.apply_theme()
        self.render()
        # Never let the window get narrower than the toolbar needs (buttons overlapped).
        self.update_idletasks()
        min_w, min_h = max(self.px(700), self.toolbar.winfo_reqwidth() + self.px(20)), self.px(340)
        self.minsize(min_w, min_h)
        # Normal start size: wide enough that every column fits (no horizontal scrollbar),
        # but never bigger than the screen, never below the minimum; opens centered.
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w = max(min(self.px(1260), sw - 40), min_w)
        h = max(min(self.px(560), sh - self.px(120)), min_h)
        self.geometry("%dx%d+%d+%d" % (w, h, max(0, (sw - w) // 2), max(0, (sh - h) // 3)))
        self.after(100, self._poll)
        if self.data["settings"].get("check_on_launch") and self.data["projects"]:
            self.after(400, self.check_updates)

    # ---- layout ----------------------------------------------------------
    def px(self, n):
        """A design size in pixels at 100% scaling, converted to this display's scale."""
        return int(round(n * self.ui_scale))

    def _build_ui(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")  # the only built-in theme that is fully recolorable
        except tk.TclError:
            pass

        top = ttk.Frame(self, padding=(10, 10, 10, 4))
        top.pack(fill="x")
        ttk.Label(top, text="Project (repo URL or owner/repo):").pack(side="left")
        self.entry = ttk.Entry(top)
        self.entry.pack(side="left", fill="x", expand=True, padx=8)
        self.entry.bind("<Return>", lambda e: self.add_project())
        self.btn_add = self._button(top, "Add project", "plus", self.add_project)
        self.btn_add.pack(side="left")

        bar = ttk.Frame(self, padding=(10, 4, 10, 6))
        bar.pack(fill="x")
        self.toolbar = bar
        self.btn_check = self._button(bar, "Check for updates", "refresh", self.check_updates)
        self.btn_check.pack(side="left")
        self._button(bar, "Mark as seen", "check", self.mark_seen).pack(side="left", padx=(8, 0))
        self._button(bar, "Open release page", "ext", self.open_release).pack(side="left", padx=(8, 0))
        self._button(bar, "Remove", "trash", self.remove_selected).pack(side="left", padx=(8, 0))
        self._button(bar, "Settings", "gear", self.open_settings).pack(side="right")
        self._button(bar, "Export", "export", self.export_json).pack(side="right", padx=(0, 8))
        self._button(bar, "Import", "import", self.import_json).pack(side="right", padx=(0, 8))

        # Search + status filter: only changes what is listed, never the saved data.
        flt = ttk.Frame(self, padding=(10, 0, 10, 6))
        flt.pack(fill="x")
        ttk.Label(flt, text="Filter:").pack(side="left")
        self.filter_text = tk.StringVar()
        self.filter_kind = tk.StringVar(value="all")
        self.filter_entry = ttk.Entry(flt, textvariable=self.filter_text)
        self.filter_entry.pack(side="left", fill="x", expand=True, padx=8)
        self.filter_entry.bind("<Escape>", lambda e: self.clear_filter())
        self.filter_text.trace_add("write", lambda *a: self._schedule_filter())
        self.kind_label = tk.StringVar(value="Show: All projects")
        self.kind_button = ttk.Menubutton(flt, textvariable=self.kind_label, width=24)
        self.kind_menu = tk.Menu(self.kind_button, tearoff=0)
        for value, text in STATUS_FILTERS:
            self.kind_menu.add_radiobutton(label=text, value=value, variable=self.filter_kind,
                                           command=self._kind_changed)
        self.kind_button["menu"] = self.kind_menu
        self.kind_button.pack(side="left")
        self.btn_clear = ttk.Button(flt, text="Clear", command=self.clear_filter)
        self.btn_clear.pack(side="left", padx=(8, 0))
        self.count_var = tk.StringVar()
        ttk.Label(flt, textvariable=self.count_var, style="Sub.TLabel", width=14, anchor="e").pack(side="left", padx=(8, 0))
        self.bind("<Control-f>", lambda e: self._focus_filter())
        self.bind("<Control-F>", lambda e: self._focus_filter())

        frame = ttk.Frame(self, padding=(10, 0, 10, 0))
        frame.pack(fill="both", expand=True)
        cols = ("name", "repo", "source", "release", "published", "status", "checked")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="extended")
        heads = [
            ("name", "Project", 230, 120),
            ("repo", "Repository", 250, 120),
            ("source", "Source", 125, 95),         # wide enough for the sort arrow
            ("release", "Current release", 150, 90),
            ("published", "Published", 125, 115),  # wide enough for the sort arrow
            ("status", "Status", 260, 120),
            ("checked", "Last checked", 140, 110),
        ]
        self.head_text = {cid: text for cid, text, _w, _mw in heads}
        for cid, text, w, mw in heads:
            if cid in SORTABLE:  # Current release / Last checked: not clickable
                self.tree.heading(cid, text=text, anchor="w", command=lambda c=cid: self.sort_by(c))
            else:
                self.tree.heading(cid, text=text, anchor="w")
            # No Tk "stretch": _layout_columns() resizes every column in proportion to the window.
            w, mw = self.px(w), self.px(mw)
            self.tree.column(cid, width=w, minwidth=mw, stretch=False)
            self._col_base[cid], self._col_min[cid] = w, mw
        self.update_headings()
        # Grid (not pack) so the scrollbars always keep their own space: with pack the
        # list took the full width of its columns and pushed the scrollbar out of view.
        self.vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self._on_yscroll, xscrollcommand=self._on_xscroll)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.hsb.grid_remove()   # shown only when the columns do not fit (see _on_xscroll)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Button-3>", self._popup)
        self.tree.bind("<Delete>", lambda e: self.remove_selected())
        self.tree.bind("<F2>", lambda e: self.rename_selected())
        self.tree.bind("<Control-a>", lambda e: self._select_all_rows())
        self.tree.bind("<Control-A>", lambda e: self._select_all_rows())
        self.tree.bind("<Button-1>", self._on_tree_click, add="+")
        self.tree.bind("<Configure>", lambda e: self._schedule_lines(delay=40), add="+")
        self.tree.bind("<Configure>", self._layout_columns, add="+")
        self.tree.bind("<ButtonPress-1>", self._col_press, add="+")
        self.tree.bind("<ButtonRelease-1>", self._col_release, add="+")
        self.tree.bind("<B1-Motion>", lambda e: self._schedule_lines() if self._col_drag else None, add="+")
        self.tree.bind("<Motion>", self._on_motion, add="+")
        self.tree.bind("<Leave>", self._on_leave, add="+")
        self.tree.bind("<MouseWheel>", lambda e: self._hide_pencil(), add="+")
        # Hover pencil (rename). A Label placed over the list: Treeview cannot hold widgets in cells.
        self.pencil = tk.Label(self.tree, bd=0, highlightthickness=0, cursor="hand2")
        self.pencil.bind("<Button-1>", lambda e: self.begin_rename(self._pencil_row))
        self.pencil.bind("<MouseWheel>", self._forward_wheel)
        self.pencil.bind("<Leave>", self._on_leave)
        self._pencil_row = None

        self.menu = tk.Menu(self, tearoff=0)
        self.pre_var = tk.BooleanVar(value=False)
        self.menu.add_command(label="Open release page", command=self.open_release)
        self.menu.add_command(label="Open repository", command=self.open_repo)
        self.menu.add_command(label="Mark as seen", command=self.mark_seen)
        self.menu.add_separator()
        self.menu.add_command(label="Rename...", accelerator="F2", command=self.rename_selected)
        self.menu.add_command(label="Reset name", command=self.reset_name)
        self.menu.add_checkbutton(label="Include pre-releases", variable=self.pre_var,
                                  command=self.toggle_prerelease)
        self.menu.add_separator()
        self.menu.add_command(label="Remove", command=self.remove_selected)

        self.status = tk.StringVar(value="Add a project to get started.")
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(fill="x")
        # Icon-only, bottom right: shows the mode you will switch TO (moon = go dark, sun = go light).
        self.btn_theme = self._button(self.status_bar, "", "moon", self.toggle_theme, style="Icon.TButton")
        self.btn_theme.pack(side="right", padx=(0, 10), pady=2)
        Tooltip(self.btn_theme,
                lambda: "Switch to light mode" if self.theme_name == "dark" else "Switch to dark mode",
                lambda: (THEMES[self.theme_name]["tip_bg"], THEMES[self.theme_name]["tip_fg"]))
        self.status_label = ttk.Label(self.status_bar, textvariable=self.status, anchor="w", padding=(10, 6))
        self.status_label.pack(side="left", fill="x", expand=True)
        self._build_text_menus()

    # ---- theme -----------------------------------------------------------
    def apply_theme(self):
        c = THEMES[self.theme_name]
        s = self.style
        self.configure(bg=c["bg"])
        s.configure(".", background=c["bg"], foreground=c["fg"], fieldbackground=c["field"],
                    bordercolor=c["border"], lightcolor=c["bg"], darkcolor=c["bg"],
                    troughcolor=c["bg"], insertcolor=c["fg"])
        s.configure("TFrame", background=c["bg"])
        s.configure("TLabel", background=c["bg"], foreground=c["fg"])
        s.configure("Sub.TLabel", background=c["bg"], foreground=c["sub_fg"])
        s.configure("TButton", background=c["btn_bg"], foreground=c["fg"], bordercolor=c["border"],
                    lightcolor=c["btn_bg"], darkcolor=c["btn_bg"], focuscolor=c["btn_bg"],
                    padding=(10, 4))
        s.configure("Icon.TButton", background=c["bg"], bordercolor=c["bg"], lightcolor=c["bg"],
                    darkcolor=c["bg"], focuscolor=c["bg"], relief="flat", padding=(6, 4))
        s.map("Icon.TButton", background=[("pressed", c["btn_active"]), ("active", c["btn_active"])],
              bordercolor=[("pressed", c["btn_active"]), ("active", c["btn_active"])],
              lightcolor=[("pressed", c["btn_active"]), ("active", c["btn_active"])],
              darkcolor=[("pressed", c["btn_active"]), ("active", c["btn_active"])])
        s.map("TButton",
              background=[("disabled", c["bg"]), ("pressed", c["btn_active"]), ("active", c["btn_active"])],
              foreground=[("disabled", c["sub_fg"])])
        s.configure("TEntry", fieldbackground=c["field"], foreground=c["fg"], insertcolor=c["fg"],
                    bordercolor=c["border"], lightcolor=c["field"], darkcolor=c["field"])
        s.configure("TMenubutton", background=c["btn_bg"], foreground=c["fg"], bordercolor=c["border"],
                    lightcolor=c["btn_bg"], darkcolor=c["btn_bg"], arrowcolor=c["fg"], padding=(8, 4))
        s.map("TMenubutton", background=[("active", c["btn_active"])])
        s.configure("TCheckbutton", background=c["bg"], foreground=c["fg"])
        s.map("TCheckbutton", background=[("active", c["bg"])])
        s.configure("Treeview", background=c["field"], fieldbackground=c["field"], foreground=c["fg"],
                    bordercolor=c["border"], lightcolor=c["field"], darkcolor=c["field"], rowheight=self.px(26))
        s.map("Treeview", background=[("selected", c["sel_bg"])], foreground=[("selected", c["sel_fg"])])
        s.configure("Treeview.Heading", background=c["head_bg"], foreground=c["fg"], relief="flat",
                    bordercolor=c["border"], lightcolor=c["head_bg"], darkcolor=c["head_bg"],
                    padding=(3, 4), font=self._head_font())
        s.map("Treeview.Heading", background=[("active", c["btn_active"])])
        for name in ("TScrollbar", "Vertical.TScrollbar"):
            s.configure(name, background=c["btn_bg"], troughcolor=c["bg"], arrowcolor=c["fg"],
                        bordercolor=c["bg"], lightcolor=c["btn_bg"], darkcolor=c["btn_bg"])
            s.map(name, background=[("active", c["btn_active"])])
        self.tree.tag_configure("update", background=c["update_bg"], foreground=c["update_fg"])
        self.tree.tag_configure("error", foreground=c["error_fg"])
        self.tree.tag_configure("none", foreground=c["none_fg"])
        for mnu in (self.menu, self.edit_menu, self.status_menu, self.kind_menu):
            mnu.configure(bg=c["field"], fg=c["fg"], activebackground=c["sel_bg"],
                          activeforeground=c["sel_fg"], disabledforeground=c["none_fg"], bd=0)
        self.refresh_icons()
        self.arrow_up = self._triangle(True, c["fg"])      # sort arrows follow the theme color
        self.arrow_down = self._triangle(False, c["fg"])
        self.update_headings()
        self._pencil_imgs = {}
        self._hide_pencil()
        self._head_h = None   # re-measure the header row (its height can depend on the theme)
        self._schedule_lines()
        set_titlebar_dark(self, self.theme_name == "dark")

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.data["settings"]["theme"] = self.theme_name
        self.persist()
        self.apply_theme()
        self.set_status("%s mode." % self.theme_name.capitalize())

    # ---- toolbar icons ---------------------------------------------------
    def _button(self, parent, text, icon, command, style=None):
        btn = ttk.Button(parent, text=text, command=command, **({"style": style} if style else {}))
        self._btn_icons.append((btn, icon))
        return btn

    def refresh_icons(self):
        """(Re)draw every button icon in the theme's colors, with a greyed copy for disabled."""
        c = THEMES[self.theme_name]
        self._icon_refs = []
        for btn, name in self._btn_icons:
            if btn is getattr(self, "btn_theme", None):
                name = "sun" if self.theme_name == "dark" else "moon"
            normal = icon_image(self, name, self.icon_px, c["fg"])
            grey = icon_image(self, name, self.icon_px, c["sub_fg"])
            if normal is None or grey is None:
                continue
            self._icon_refs += [normal, grey]
            icon_only = not str(btn.cget("text"))
            btn.configure(image=(normal, "disabled", grey), compound="image" if icon_only else "left")

    # ---- column widths ---------------------------------------------------
    def _head_font(self):
        """The list's normal font, in bold, for the column headers."""
        if getattr(self, "_head_font_obj", None) is None:
            import tkinter.font as tkfont
            f = tkfont.nametofont("TkDefaultFont", root=self).copy()
            f.configure(weight="bold")
            self._head_font_obj = f
        return self._head_font_obj

    def _layout_columns(self, _event=None):
        """Size the columns to the window, in proportion to their preferred widths.

        Wider than the preferred total: every column grows by the same ratio. Narrower: each
        column shrinks from its preferred width toward its minimum, all at the same rate, so
        the columns hit their minimums together and no single column gets squeezed first.
        Runs only when the list's width changes, so a column the user dragged keeps its width
        until the window is resized.
        """
        width = self.tree.winfo_width()
        if width <= 1 or width == self._tree_w:
            return
        self._tree_w = width
        avail = width - 4  # the list draws a 2 px border on each side
        ids = list(self._col_base)
        pref = [self._col_base[c] for c in ids]
        low = [self._col_min[c] for c in ids]
        total_pref, total_low = sum(pref), sum(low)
        if avail >= total_pref:
            target = [p * avail / float(total_pref) for p in pref]
        else:
            t = max(0.0, (avail - total_low) / float(total_pref - total_low))
            target = [lo + (p - lo) * t for p, lo in zip(pref, low)]
        sizes = [max(lo, int(x)) for x, lo in zip(target, low)]
        if avail >= total_low:                     # hand the rounding remainder to Status
            sizes[ids.index("status")] += max(0, avail - sum(sizes))
        for cid, w in zip(ids, sizes):
            self.tree.column(cid, width=w)
        self._schedule_lines()

    def _col_press(self, event):
        self._col_drag = self.tree.identify_region(event.x, event.y) == "separator"

    def _col_release(self, _event):
        if self._col_drag:  # the user resized a column: that is the new preferred layout
            self._col_drag = False
            ids = list(self._col_base)
            slack = self.tree.winfo_width() - 4 - sum(int(self.tree.column(c, "width")) for c in ids)
            if slack > 0:       # a column was made narrower: the last column takes the freed space, no empty strip
                last = ids[-1]
                self.tree.column(last, width=int(self.tree.column(last, "width")) + slack)
            self._col_base = {c: int(self.tree.column(c, "width")) for c in self._col_base}
            self._schedule_lines()

    # ---- row and column separators (thin lines) ---------------------------
    def _on_xscroll(self, first, last):
        self.hsb.set(first, last)
        needed = (float(last) - float(first)) < 0.998     # less than ~2 px hidden does not count
        if needed != self._hsb_shown:
            self._hsb_shown = needed
            if needed:
                self.hsb.grid()
            else:
                self.hsb.grid_remove()
        self._schedule_lines()

    def _on_yscroll(self, first, last):
        self.vsb.set(first, last)
        self._schedule_lines()
        self._hide_pencil()

    def _schedule_lines(self, _e=None, delay=None):
        """Redraw the separator lines once things settle. While the window is dragged the
        events arrive in a burst; `delay` merges them into one redraw (much less work)."""
        if self._lines_job is None:
            self._lines_job = (self.after(delay, self._redraw_lines) if delay
                               else self.after_idle(self._redraw_lines))

    def _redraw_lines(self):
        self._lines_job = None
        tree = self.tree
        ys = []
        for iid in tree.get_children():
            box = tree.bbox(iid)
            if box:
                ys.append(box[1] + box[3] - 1)
        while len(self._lines) < len(ys):
            f = tk.Frame(tree, height=1, bd=0, highlightthickness=0)
            # A click that lands exactly on the 1 px line is passed on to the list.
            f.bind("<Button-1>", lambda e: self._forward(e, "<Button-1>"))
            f.bind("<ButtonRelease-1>", lambda e: self._forward(e, "<ButtonRelease-1>"))
            f.bind("<Button-3>", lambda e: self._forward(e, "<Button-3>"))
            f.bind("<MouseWheel>", self._forward_wheel)
            self._lines.append(f)
        color = THEMES[self.theme_name]["line"]
        # Row lines span the full width on their own (relwidth), so when only the width changed
        # (window resize) they need no update at all.
        if (ys, color) != self._lines_state:
            self._lines_state = (ys, color)
            for i, f in enumerate(self._lines):
                if i < len(ys):
                    f.configure(bg=color)
                    f.place(x=0, y=ys[i], relwidth=1, height=1)
                    f.lift()
                else:
                    f.place_forget()
        self._redraw_vlines()

    def _header_height(self):
        """Pixel height of the header row (measured once; the column lines start below it)."""
        if self._head_h is None:
            tree = self.tree
            x, y = max(3, tree.winfo_width() // 2), 3
            while y < 80 and tree.identify_region(x, y) in ("heading", "separator"):
                y += 1
            self._head_h = y if 3 < y < 80 else None
        return self._head_h

    def _redraw_vlines(self):
        tree = self.tree
        hh = self._header_height()
        cols = list(tree["columns"])
        widths = [int(tree.column(c, "width")) for c in cols]
        off = int(round(tree.xview()[0] * sum(widths)))      # how far the list is scrolled sideways
        # where the first column really starts inside the widget (border width differs per theme/OS)
        for iid in tree.get_children():
            b = tree.bbox(iid, cols[0])
            if b:
                self._xorg = b[0] + off
                break
        edges, cum = [], 0
        for w in widths[:-1]:
            cum += w
            edges.append(cum - 1 - off + self._xorg)
        while len(self._vlines) < len(edges):
            f = tk.Frame(tree, width=1, bd=0, highlightthickness=0)
            f.bind("<Button-1>", lambda e: self._forward(e, "<Button-1>", True))
            f.bind("<ButtonRelease-1>", lambda e: self._forward(e, "<ButtonRelease-1>", True))
            f.bind("<Button-3>", lambda e: self._forward(e, "<Button-3>", True))
            f.bind("<MouseWheel>", self._forward_wheel)
            self._vlines.append(f)
        color = THEMES[self.theme_name]["line"]
        visible_w = tree.winfo_width() - 2
        for f, x in zip(self._vlines, edges):
            if hh and 0 <= x < visible_w:
                f.configure(bg=color)
                f.place(x=x, y=hh, width=1, relheight=1.0, height=-hh)
                f.lift()
            else:
                f.place_forget()

    def _forward(self, event, sequence, vertical=False):
        """Pass a click that landed on a 1 px line on to the list underneath."""
        w = event.widget
        x, y = (w.winfo_x() - 1, event.y + w.winfo_y()) if vertical else (event.x, w.winfo_y() - 1)
        try:
            self.tree.event_generate(sequence, x=x, y=y, rootx=event.x_root, rooty=event.y_root)
        except tk.TclError:
            pass

    def _forward_wheel(self, event):
        self.tree.yview_scroll(-1 if event.delta > 0 else 1, "units")

    # ---- rename (pencil on hover, F2, right-click) ------------------------
    def _row_bg(self, iid):
        c = THEMES[self.theme_name]
        if iid in self.tree.selection():
            return c["sel_bg"], c["sel_fg"]
        if "update" in self.tree.item(iid, "tags"):
            return c["update_bg"], c["update_fg"]
        return c["field"], c["fg"]

    def _on_motion(self, event):
        if self._editor:
            return
        iid = self.tree.identify_row(event.y)
        if not iid or self.tree.identify_region(event.x, event.y) != "cell":
            self._hide_pencil()
            return
        box = self.tree.bbox(iid, "name")
        if not box:
            self._hide_pencil()
            return
        x, y, w, h = box
        bg, fg = self._row_bg(iid)
        px = self.icon_px
        img = self._pencil_imgs.get(fg)
        if img is None:
            img = self._pencil_imgs[fg] = icon_image(self, "pencil", px, fg)
        if img is None:
            return
        self.pencil.configure(image=img, bg=bg)
        self.pencil.place(x=x + w - px - 8, y=y + (h - px) // 2)
        self.pencil.lift()
        self._pencil_row = iid

    def _on_tree_click(self, _event):
        if self._editor:  # a click elsewhere in the list saves the name being typed
            self.after_idle(lambda: self._finish_rename(True))

    def _on_leave(self, _event=None):
        # Moving from the list onto the pencil itself must not hide it.
        under = self.winfo_containing(*self.winfo_pointerxy())
        if under is not self.pencil:
            self._hide_pencil()

    def _hide_pencil(self):
        self.pencil.place_forget()
        self._pencil_row = None

    def rename_selected(self):
        sel = self.selected_projects()
        if len(sel) != 1:
            self.set_status("Select one project to rename.")
            return
        self.begin_rename(project_key(sel[0]))

    def begin_rename(self, iid):
        if not iid or self._editor or not self.tree.exists(iid):
            return
        self._close_editor(True)
        self.tree.see(iid)
        self.update_idletasks()
        box = self.tree.bbox(iid, "name")
        p = next((q for q in self.data["projects"] if project_key(q) == iid), None)
        if not box or not p:
            return
        self._hide_pencil()
        x, y, w, h = box
        ent = ttk.Entry(self.tree)
        ent.insert(0, display_name(p))
        ent.place(x=x, y=y, width=w, height=h)
        ent.focus_force()
        ent.select_range(0, "end")
        ent.icursor("end")
        self.attach_edit_menu(ent)
        self._editor = (ent, iid, p)
        ent.bind("<Return>", lambda e: self._finish_rename(True))
        ent.bind("<Escape>", lambda e: self._finish_rename(False))
        # No save-on-focus-loss: opening the box's right-click menu (Paste) takes focus away
        # and must not close it. Clicking elsewhere in the list saves it instead (_on_tree_click).

    def _finish_rename(self, commit):
        if not self._editor:
            return
        changed = self._close_editor(commit)
        self.render()
        if changed:
            self.set_status(changed)

    def _close_editor(self, commit):
        """Close the rename box; returns a status message if a name changed, else ''."""
        if not self._editor:
            return ""
        ent, _iid, p = self._editor
        self._editor = None
        text = clean_name(ent.get())
        ent.destroy()
        if not commit:
            return ""
        original = p.get("title") or p["repo"]
        before = display_name(p)
        if text and text != original:
            p["custom_name"] = text
        else:
            p.pop("custom_name", None)  # blank or the GitHub name itself = back to the original
        if display_name(p) == before:
            return ""
        self.persist()
        return "Renamed to %s." % display_name(p) if p.get("custom_name") else "Name reset to %s." % display_name(p)

    def reset_name(self):
        sel = [p for p in self.selected_projects() if p.get("custom_name")]
        if not sel:
            self.set_status("Nothing to reset: the selection has no custom name.")
            return
        for p in sel:
            p.pop("custom_name", None)
        self.persist()
        self.render()
        self.set_status("Reset %d name(s) to the GitHub name." % len(sel))

    # ---- About -----------------------------------------------------------
    def show_about(self, parent=None):
        c = THEMES[self.theme_name]
        parent = parent or self
        win = tk.Toplevel(self)
        win.title("About " + APP_NAME)
        win.configure(bg=c["bg"])
        win.transient(parent)

        def close():
            win.destroy()
            if parent is not self and parent.winfo_exists():
                parent.grab_set()  # back to the Settings window, which is modal
        win.resizable(False, False)
        if self.app_icon is not None:
            try:
                win.iconphoto(False, self.app_icon)
            except tk.TclError:
                pass
        body = ttk.Frame(win, padding=18)
        body.pack(fill="both", expand=True)
        if self.app_icon is not None:
            tk.Label(body, image=self.app_icon, bg=c["bg"], bd=0).grid(row=0, column=0, rowspan=4, sticky="n", padx=(0, 16))
        ttk.Label(body, text=APP_NAME, font=("Segoe UI", 14, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(body, text="Version %s" % APP_VERSION).grid(row=1, column=1, sticky="w")
        ttk.Label(body, style="Sub.TLabel", wraplength=340, justify="left",
                  text="Tracks the latest release of the GitHub projects you follow. "
                       "No account, login or token needed. MIT License.").grid(row=2, column=1, sticky="w", pady=(6, 6))
        link = tk.Label(body, text=REPO_URL, fg="#4da3ff" if self.theme_name == "dark" else "#0b57d0",
                        bg=c["bg"], cursor="hand2", bd=0)
        link.grid(row=3, column=1, sticky="w")
        link.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))
        btns = ttk.Frame(body)
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(16, 0))

        def copy_version():
            self.clipboard_clear()
            self.clipboard_append("%s v%s" % (APP_NAME, APP_VERSION))
            self.set_status("Copied: %s v%s" % (APP_NAME, APP_VERSION))

        ttk.Button(btns, text="Close", command=close).pack(side="right")
        ttk.Button(btns, text="Copy version", command=copy_version).pack(side="right", padx=(0, 8))
        set_titlebar_dark(win, self.theme_name == "dark")
        win.grab_set()
        win.bind("<Escape>", lambda e: close())
        win.protocol("WM_DELETE_WINDOW", close)

    # ---- helpers ---------------------------------------------------------
    # ---- right-click menus for text (Cut / Copy / Paste / Select all) -------
    def _build_text_menus(self):
        em = self.edit_menu = tk.Menu(self, tearoff=0)
        em.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self._edit("<<Cut>>"))
        em.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self._edit("<<Copy>>"))
        em.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self._edit("<<Paste>>"))
        em.add_separator()
        em.add_command(label="Select all", accelerator="Ctrl+A", command=lambda: self._select_all(self._edit_target))
        self._edit_target = None
        self.status_menu = tk.Menu(self, tearoff=0)
        self.status_menu.add_command(label="Copy", command=self.copy_status)
        self.attach_edit_menu(self.entry)
        self.attach_edit_menu(self.filter_entry)
        self.status_label.bind("<Button-3>", self._show_status_menu)

    def attach_edit_menu(self, entry, masked=False):
        """Right-click menu + Ctrl+A for a text box. masked=True (token box): no Cut/Copy."""
        entry.bind("<Button-3>", lambda e, m=masked: self._show_edit_menu(e, m))
        entry.bind("<Control-a>", lambda e: self._select_all(e.widget))
        entry.bind("<Control-A>", lambda e: self._select_all(e.widget))

    @staticmethod
    def _select_all(w):
        if w is not None:
            w.selection_range(0, "end")
            w.icursor("end")
        return "break"  # stop Tk's own Ctrl+A (jump to line start on some platforms)

    def _edit(self, virtual_event):
        w = self._edit_target
        if w is not None:
            w.focus_set()
            w.event_generate(virtual_event)  # use the text box's own, native Cut/Copy/Paste

    def _show_edit_menu(self, event, masked=False):
        w = event.widget
        state = str(w.cget("state"))
        if state == "disabled":
            return
        w.focus_set()
        try:
            has_clip = bool(self.clipboard_get())
        except tk.TclError:  # clipboard empty or holds something that is not text
            has_clip = False
        has_sel = bool(w.selection_present())
        editable = state == "normal"
        em = self.edit_menu
        em.entryconfigure("Cut", state="normal" if (has_sel and editable and not masked) else "disabled")
        em.entryconfigure("Copy", state="normal" if (has_sel and not masked) else "disabled")
        em.entryconfigure("Paste", state="normal" if (has_clip and editable) else "disabled")
        em.entryconfigure("Select all", state="normal" if w.get() else "disabled")
        self._edit_target = w
        try:
            em.tk_popup(event.x_root, event.y_root)
        finally:
            em.grab_release()

    def _show_status_menu(self, event):
        self.status_menu.entryconfigure("Copy", state="normal" if self.status.get() else "disabled")
        try:
            self.status_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.status_menu.grab_release()

    def copy_status(self):
        self.clipboard_clear()
        self.clipboard_append(self.status.get())

    def token(self):
        return (self.data["settings"].get("token") or "").strip()

    def set_status(self, text):
        self.status.set(text)

    def set_busy(self, busy, text=None):
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.btn_add.configure(state=state)
        self.btn_check.configure(state=state)
        if text:
            self.set_status(text)

    def run_async(self, fn, done):
        def target():
            try:
                self.q.put((done, fn(), None))
            except Exception as e:  # noqa: BLE001 - surfaced to the UI
                self.q.put((done, None, e))
        threading.Thread(target=target, daemon=True).start()

    def _poll(self):
        while True:
            try:
                done, res, exc = self.q.get_nowait()
            except queue.Empty:
                break
            try:
                done(res, exc)
            except Exception as e:  # noqa: BLE001
                self.set_busy(False, "Internal error: %s" % e)
        self.after(100, self._poll)

    def selected_projects(self):
        keys = set(self.tree.selection())
        return [p for p in self.data["projects"] if project_key(p) in keys]

    def persist(self):
        try:
            save_data(self.data)
        except OSError as e:
            messagebox.showerror(APP_NAME, "Could not save projects.json:\n%s" % e)

    # ---- sorting ---------------------------------------------------------
    def _triangle(self, up, color):
        """A small drawn arrow (no font needed, so it looks the same everywhere)."""
        img = tk.PhotoImage(master=self, width=11, height=6)
        for r in range(6):
            half = r if up else 5 - r
            img.put(color, to=(5 - half, r, 5 + half + 1, r + 1))
        k = int(round(self.ui_scale))
        return img.zoom(k) if k > 1 else img   # keep the arrow the same visual size on high-DPI

    def update_headings(self):
        """Show an up/down arrow on the header of the column that is sorted."""
        for cid, text in self.head_text.items():
            img = ""
            if cid == self.sort_col and getattr(self, "arrow_up", None) is not None:
                img = self.arrow_up if self.sort_asc else self.arrow_down
            self.tree.heading(cid, text=text, image=img)

    def sort_by(self, col):
        if col == self.sort_col:
            self.sort_asc = not self.sort_asc          # same column again: flip direction
        else:
            self.sort_col = col
            # A-Z first for names; newest first for dates (like Explorer's "Date modified")
            self.sort_asc = (col != "published")
        self.data["settings"]["sort_col"] = self.sort_col
        self.data["settings"]["sort_asc"] = self.sort_asc
        self.persist()
        self.update_headings()
        self.render()

    # ---- search / filter ---------------------------------------------------
    def _schedule_filter(self):
        """Re-list shortly after the last keystroke (400+ rows are rebuilt each time)."""
        if getattr(self, "_filter_job", None):
            self.after_cancel(self._filter_job)
        self._filter_job = self.after(150, self._apply_filter)

    def _apply_filter(self):
        self._filter_job = None
        self.render()

    def _kind_changed(self):
        text = dict(STATUS_FILTERS)[self.filter_kind.get()]
        self.kind_label.set("Show: " + text)
        self.render()

    def clear_filter(self):
        self.filter_text.set("")
        self.filter_kind.set("all")
        self.kind_label.set("Show: " + dict(STATUS_FILTERS)["all"])
        if getattr(self, "_filter_job", None):
            self.after_cancel(self._filter_job)
            self._filter_job = None
        self.render()

    def _focus_filter(self):
        self.filter_entry.focus_set()
        self.filter_entry.selection_range(0, "end")
        return "break"

    def _select_all_rows(self):
        """Ctrl+A in the list: select every project that is listed (a filter limits it)."""
        self.tree.selection_set(self.tree.get_children())
        return "break"

    def filter_active(self):
        return bool(self.filter_text.get().strip()) or self.filter_kind.get() != "all"

    # ---- rendering -------------------------------------------------------
    def render(self):
        self._close_editor(True)  # rows are rebuilt below: save a name being typed first
        self._hide_pencil()
        # Re-selecting the rows below fires <<TreeviewSelect>> a moment later, which would replace
        # a status message such as "Renamed to ..." with the project description. Ignore those
        # events until the event queue is empty (idle callbacks run after pending events).
        self._suppress_select = True
        self.after_idle(self._allow_select)
        selected = set(self.tree.selection())
        self.tree.delete(*self.tree.get_children())
        total = len(self.data["projects"])
        projects = sort_projects(filter_projects(self.data["projects"], self.filter_text.get(),
                                                 self.filter_kind.get()), self.sort_col, self.sort_asc)
        self.count_var.set("%d of %d" % (len(projects), total) if len(projects) != total
                           else "%d project%s" % (total, "" if total == 1 else "s"))
        for p in projects:
            latest = p.get("latest") or {}
            release = latest.get("tag") or latest.get("name") or ""
            if latest.get("source") == "tag":
                release += " (tag)"
            elif latest.get("prerelease"):
                release += " (pre-release)"
            tag = status_kind(p)
            tag = "" if tag == "ok" else tag
            checked = (p.get("last_checked") or "")[:16].replace("T", " ")
            self.tree.insert("", "end", iid=project_key(p), tags=(tag,) if tag else (), values=(
                display_name(p),
                repo_path(p),
                source_label(p),
                release or "-",
                (latest.get("published_at") or "")[:10] or "-",
                status_text(p),
                checked or "never",
            ))
        keep = [k for k in selected if self.tree.exists(k)]
        if keep:
            self.tree.selection_set(keep)
        self._schedule_lines()

    def _on_double_click(self, event):
        """Double-click a project name to rename it; any other cell opens the release page.

        A fast second click on a column header (or on its resize edge, or on
        empty space) must not open anything.
        """
        if self.tree.identify_region(event.x, event.y) == "cell" and self.tree.identify_row(event.y):
            if self.tree.identify_column(event.x) == "#1":   # the Project column: rename, like the pencil
                self.begin_rename(self.tree.identify_row(event.y))
            else:
                self.open_release()

    def _allow_select(self):
        self._suppress_select = False

    def _on_select(self, _event=None):
        if self._suppress_select:
            return
        sel = self.selected_projects()
        if len(sel) == 1:
            p = sel[0]
            if p.get("error"):
                self.set_status(p["error"])
            else:
                # Always replace the status text: skipping this when the About box is
                # empty left the previous project's description on screen.
                self.set_status(p.get("description") or NO_DESCRIPTION)

    def _popup(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            if row not in self.tree.selection():
                self.tree.selection_set(row)
            sel = self.selected_projects()
            if sel:
                self.pre_var.set(bool(sel[0].get("include_prereleases")))
            self.menu.entryconfigure("Rename...", state="normal" if len(sel) == 1 else "disabled")
            self.menu.entryconfigure("Reset name", state="normal" if any(p.get("custom_name") for p in sel) else "disabled")
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    # ---- actions ---------------------------------------------------------
    def add_project(self):
        if self.busy:
            return
        ref = parse_project_ref(self.entry.get())
        if not ref:
            messagebox.showerror(APP_NAME, "Enter a project URL such as\nhttps://github.com/owner/repo,\n"
                                 "https://codeberg.org/owner/repo or https://gitlab.com/group/project\n"
                                 "(any GitLab, Gitea or Forgejo server works), or just owner/repo for GitHub.")
            return
        host, kind, segs = ref
        owner, repo = split_path(segs)
        shown = "%s/%s/%s" % (host_label(host), owner, repo) if host else "%s/%s" % (owner, repo)
        if any(project_key(p) == shown.lower() for p in self.data["projects"]):
            messagebox.showinfo(APP_NAME, "%s is already in the list." % shown)
            return
        if len(self.data["projects"]) >= MAX_PROJECTS:
            messagebox.showinfo(APP_NAME, "The list is full (%d projects)." % MAX_PROJECTS)
            return
        token = self.token()
        self.set_busy(True, "Adding %s ..." % shown)

        def work():
            if host:   # another host: public repositories only, official releases only
                return resolve_project(host, kind, segs, True)
            latest = get_latest(owner, repo, token, True)
            try:
                info = fetch_repo_info(owner, repo, token)
            except NotFoundError:
                raise
            except GitHubError:
                # API unavailable (e.g. rate-limited): the release feed is enough.
                info = {"owner": owner, "repo": repo, "title": repo, "description": "",
                        "html_url": "https://github.com/%s/%s" % (owner, repo)}
            return info, latest

        self.run_async(work, self._added)

    def _added(self, result, exc):
        self.set_busy(False)
        if exc:
            self.set_status("Could not add project.")
            messagebox.showerror(APP_NAME, str(exc))
            return
        info, latest = result
        p = dict(info)
        if any(project_key(x) == project_key(p) for x in self.data["projects"]):
            self.set_status("Already in the list.")
            return
        p.update({
            "include_prereleases": True,  # "whatever is newest", as on the Releases page
            "fmt": 2,
            "latest": latest,
            # Baseline: the release that exists now counts as already seen.
            "seen_id": latest["id"] if latest else None,
            "seen_tag": latest["tag"] if latest else None,
            "last_checked": datetime.now().isoformat(timespec="seconds"),
            "error": None,
        })
        self.data["projects"].append(p)
        self.persist()
        self.entry.delete(0, "end")
        if self.filter_active():   # a filtered-out new project would look like it was not added
            self.clear_filter()
        else:
            self.render()
        if latest:
            self.set_status("Added %s - current release %s." % (p["title"], latest["tag"] or latest["name"]))
        else:
            self.set_status("Added %s - it has no published releases yet." % p["title"])

    def check_updates(self):
        if self.busy:
            return
        if not self.data["projects"]:
            self.set_status("Nothing to check - add a project first.")
            return
        token = self.token()
        snapshot = [(p.get("host") or "", p.get("kind"), p["owner"], p["repo"], bool(p.get("include_prereleases")),
                     project_key(p)) for p in self.data["projects"]]
        self.set_busy(True, "Checking %d project(s) ..." % len(snapshot))

        def work():
            out = []
            for host, kind, owner, repo, inc, key in snapshot:
                try:
                    out.append((key, fetch_latest_for(host, kind, owner, repo, token, inc), None))
                except RateLimitError as e:
                    out.append((key, None, str(e)))
                    break  # no point continuing
                except GitHubError as e:
                    out.append((key, None, str(e)))
            return out

        self.run_async(work, self._checked)

    def _checked(self, result, exc):
        self.set_busy(False)
        if exc:
            self.set_status("Check failed: %s" % exc)
            return
        now = datetime.now().isoformat(timespec="seconds")
        by_key = {project_key(p): p for p in self.data["projects"]}
        errors = 0
        for key, latest, err in result:
            p = by_key.get(key)
            if not p:
                continue
            apply_result(p, latest, err, now)
            if err:
                errors += 1
        self.persist()
        self.render()
        updates = sum(1 for p in self.data["projects"] if has_update(p))
        msg = "Checked %d project(s): %d update(s) available" % (len(result), updates)
        if errors:
            msg += ", %d error(s)" % errors
        if last_rate_remaining is not None:
            msg += ". API calls left this hour: %d" % last_rate_remaining
        self.set_status(msg + ".")

    def mark_seen(self):
        sel = self.selected_projects()
        if not sel:
            self.set_status("Select one or more projects first.")
            return
        n = 0
        for p in sel:
            latest = p.get("latest")
            if latest and has_update(p):
                p["seen_id"] = latest["id"]
                p["seen_tag"] = latest["tag"]
                n += 1
        self.persist()
        self.render()
        self.set_status("Marked %d project(s) as seen." % n if n else "No updates to mark in the selection.")

    def open_release(self):
        sel = self.selected_projects()
        if not sel:
            self.set_status("Select a project first.")
            return
        p = sel[0]
        webbrowser.open(safe_url((p.get("latest") or {}).get("url"), project_base(p), release_page(p)))

    def open_repo(self):
        sel = self.selected_projects()
        if sel:
            p = sel[0]
            webbrowser.open(safe_url(p.get("html_url"), project_base(p), repo_page(p)))

    def toggle_prerelease(self):
        sel = self.selected_projects()
        for p in sel:
            p["include_prereleases"] = self.pre_var.get()
        self.persist()
        if self.pre_var.get():
            self.set_status("Pre-releases included (uses the free release feed). Click \"Check for updates\" to apply.")
        else:
            self.set_status("Stable-only mode uses the GitHub API, which is rate-limited without a token. "
                            "Click \"Check for updates\" to apply.")

    def remove_selected(self):
        sel = self.selected_projects()
        if not sel:
            self.set_status("Select a project first.")
            return
        names = ", ".join(display_name(p) for p in sel[:3]) + ("..." if len(sel) > 3 else "")
        if not messagebox.askyesno(APP_NAME, "Remove %d project(s)?\n%s" % (len(sel), names)):
            return
        drop = {project_key(p) for p in sel}
        self.data["projects"] = [p for p in self.data["projects"] if project_key(p) not in drop]
        self.persist()
        self.render()
        self.set_status("Removed %d project(s)." % len(sel))

    # ---- import / export -------------------------------------------------
    def import_json(self):
        path = filedialog.askopenfilename(
            title="Import projects (.json)",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            if os.path.getsize(path) > MAX_IMPORT_BYTES:
                raise ValueError("The file is larger than 5 MB.")
            with open(path, "r", encoding="utf-8-sig") as f:
                raw = json.load(f)
        except (OSError, ValueError, RecursionError) as e:
            messagebox.showerror(APP_NAME, "Could not read that file as JSON:\n%s" % e)
            return
        projects, skipped = parse_import(raw)
        if projects is None:
            messagebox.showerror(APP_NAME, "This file has no project list.")
            return
        if not projects:
            messagebox.showerror(APP_NAME, "No valid projects found in this file.")
            return
        note = " (%d entries skipped as invalid or duplicate)" % skipped if skipped else ""
        choice = messagebox.askyesnocancel(
            APP_NAME,
            "Found %d project(s)%s.\n\n"
            "Yes = Merge: keep your current list and add the new ones\n"
            "No = Replace: discard your current list and use this file\n"
            "Cancel = do nothing" % (len(projects), note))
        if choice is None:
            return
        if choice:
            added = merge_projects(self.data["projects"], projects)
            msg = "Imported: %d new project(s) added, %d already in the list." % (added, len(projects) - added)
        else:
            self.data["projects"] = projects
            msg = "Imported: list replaced with %d project(s)." % len(projects)
        self.persist()
        self.render()
        self.set_status(msg + " Click \"Check for updates\" to refresh them.")

    def export_json(self):
        if not self.data["projects"]:
            messagebox.showinfo(APP_NAME, "There are no projects to export yet.")
            return
        path = filedialog.asksaveasfilename(
            title="Export projects (.json)",
            defaultextension=".json",
            initialfile="github_release_tracker_%s.json" % datetime.now().strftime("%Y-%m-%d"),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            write_json_atomic(path, build_export(self.data["projects"]))
        except OSError as e:
            messagebox.showerror(APP_NAME, "Could not write the file:\n%s" % e)
            return
        self.set_status("Exported %d project(s) to %s (token not included)." % (len(self.data["projects"]), path))

    # ---- settings --------------------------------------------------------
    def open_settings(self):
        c = THEMES[self.theme_name]
        win = tk.Toplevel(self)
        win.title("Settings")
        win.configure(bg=c["bg"])
        win.transient(self)
        win.resizable(False, False)
        body = ttk.Frame(win, padding=14)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="GitHub personal access token (optional, used for github.com only)").grid(row=0, column=0, sticky="w")
        tok = tk.StringVar(value=self.data["settings"].get("token", ""))
        ent = ttk.Entry(body, textvariable=tok, show="*", width=52)
        ent.grid(row=1, column=0, sticky="we", pady=(2, 2))
        self.attach_edit_menu(ent, masked=True)  # hidden token: Paste yes, Cut/Copy no
        ttk.Label(body, style="Sub.TLabel", wraplength=420, justify="left",
                  text="Not needed for normal use: releases are read from GitHub's public feed. "
                       "A token only helps if the feed is blocked or for stable-only mode. "
                       "It is stored in plain text in projects.json and is never written to "
                       "exported files.").grid(row=2, column=0, sticky="w", pady=(0, 10))
        launch = tk.BooleanVar(value=bool(self.data["settings"].get("check_on_launch")))
        ttk.Checkbutton(body, text="Check for updates when the app starts", variable=launch).grid(
            row=3, column=0, sticky="w")

        def save():
            self.data["settings"]["token"] = tok.get().strip()
            self.data["settings"]["check_on_launch"] = launch.get()
            self.persist()
            win.destroy()
            self.set_status("Settings saved.")

        btns = ttk.Frame(body)
        btns.grid(row=4, column=0, sticky="we", pady=(12, 0))
        ttk.Button(btns, text="About", command=lambda: self.show_about(win)).pack(side="left")
        ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right")
        ttk.Button(btns, text="Save", command=save).pack(side="right", padx=(0, 8))
        set_titlebar_dark(win, self.theme_name == "dark")
        win.grab_set()
        ent.focus_set()


def main():
    try:  # crisp text on high-DPI Windows displays
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:  # noqa: BLE001 - not Windows / not available
        pass
    try:  # own taskbar identity, so Windows shows this app's icon instead of Python's
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:  # noqa: BLE001
        pass
    App().mainloop()


if __name__ == "__main__":
    main()
