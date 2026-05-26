[app]
title = Fuel Analysis
package.name = fuelanalysis
package.domain = org.diploma
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.1

requirements = python3,kivy,reportlab
log_level = 2

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
icon.filename = %(source.dir)s/icon.png

# ЖЕСТКО ФИКСИРУЕМ СТАБИЛЬНУЮ ВЕРСИЮ NDK ДЛЯ PANDAS И NUMPY:
android.ndk = 25b

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET
android.api = 33