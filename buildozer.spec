[app]
title = Poultry Shop
package.name = poultryshop
package.domain = org.majid

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xlsx

version = 1.0

requirements = python3,kivy,openpyxl

orientation = portrait
fullscreen = 0

# icon.filename = %(source.dir)s/icon.png   # uncomment and add an icon.png (512x512) if you want a custom icon

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
