[app]
title = Fuel Analysis
package.name = fuelanalysis
package.domain = org.diploma
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# Только критически важные зависимости
requirements = python3,kivy

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
icon.filename = %(source.dir)s/icon.png

# Настройки Android
android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b

[buildozer]
# log_level = 2 даст нам подробный вывод для отладки
log_level = 2
warn_on_root = 1