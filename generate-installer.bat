rmdir dist /s /q
rmdir build /s /q
pyinstaller Launcher.py --icon=resources/image/shishi-odoshi.ico --name Shishi-odoshi --onefile -w --add-data "resources;resources"