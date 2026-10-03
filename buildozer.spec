[app]

title = Edy P2P Chat
package.name = edyp2pchat
package.domain = org.edy

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json

version = 1.0

requirements = python3==3.12.10,hostpython3==3.12.10,kivy==2.3.1

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 35
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.debug_artifact = apk

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
