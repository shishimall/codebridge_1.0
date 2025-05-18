@echo off
cd /d "C:/CODEBRIDGE_1.0"
echo [1/4] PyInstallerでEXE化開始...
pyinstaller --onefile --noconsole --icon="C:/CODEBRIDGE_1.0/codebridge.ico" "codebridge_1.0.py"
echo [2/4] EXEファイルを指定フォルダに移動...
move "dist\codebridge_1.0.exe" "C:/CODEBRIDGE_1.0\codebridge_1.0.exe"
echo [3/4] 一時ファイルを掃除中...
rmdir /s /q build
rmdir /s /q dist
del "codebridge_1.0.spec"
echo [4/4] 完了しました！
pause
