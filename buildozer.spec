[app]
title = Fuel Analysis
package.name = fuelanalysis
package.domain = org.diploma
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.1

# Только стабильные библиотеки, гарантирующие успешную сборку
requirements = python3,kivy,numpy,pandas,openpyxl,reportlab

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
icon.filename = %(source.dir)s/icon.png

# Запрос прав на чтение и запись файлов (для датасетов и отчетов)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET
android.api = 33