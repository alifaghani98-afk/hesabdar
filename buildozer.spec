[app]

# ── Identity ──────────────────────────────────────────────────────────────────
title           = حسابدار
package.name    = hesabdar
package.domain  = org.hesabdar
version         = 1.0.0

# ── Source ────────────────────────────────────────────────────────────────────
source.dir      = .
source.include_exts = py,kv,ttf,db,json,txt
source.exclude_dirs = tests, .git, __pycache__, .buildozer

# ── Python requirements ───────────────────────────────────────────────────────
# jdatetime: Persian calendar
# pandas + openpyxl: Excel export
requirements = python3,kivy==2.2.1,jdatetime,openpyxl
# ── Assets ────────────────────────────────────────────────────────────────────
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename      = %(source.dir)s/assets/icon.png

# ── Android ───────────────────────────────────────────────────────────────────
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api         = 33
android.minapi      = 24
android.ndk         = 25c
android.build_tools_version = 34.0.0
android.accept_sdk_license = True
android.archs       = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Orientation
orientation = portrait

# ── Build ─────────────────────────────────────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1
