"""
Run this script on Windows to build PLCTools.exe:

    pip install pyinstaller
    python build_exe.py

The exe will be placed in dist/PLCTools.exe
"""
import subprocess
import sys

subprocess.run(
    [
        sys.executable, "-m", "PyInstaller",
        "PLCTools.spec",
        "--distpath", "dist",
        "--workpath", "build/work",
        "--noconfirm",
    ],
    check=True,
)
print("\nBuild complete: dist/PLCTools.exe")
