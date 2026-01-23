#!/usr/bin/env python3
"""
Build script for Citation Linker app
Builds executable for current platform
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def clean_build():
    """Remove old build artifacts"""
    dirs_to_clean = ['build', 'dist']
    for d in dirs_to_clean:
        if Path(d).exists():
            print(f"Cleaning {d}/...")
            shutil.rmtree(d)

def install_dependencies():
    """Ensure all dependencies are installed"""
    print("Installing dependencies...")
    subprocess.run([
        sys.executable, '-m', 'pip', 'install',
        '-e', '../citationLinker',
        '-e', '../QtApp',
        'pyinstaller',
    ], check=True)

def build_executable():
    """Build the executable using PyInstaller"""
    print(f"Building for {sys.platform}...")
    subprocess.run([
        'pyinstaller',
        'citation_linker.spec',
        '--clean',  # Clean PyInstaller cache
    ], check=True)

    print("\n✓ Build complete!")
    print(f"Executable location: dist/")

    if sys.platform == 'darwin':
        print("Output: dist/Citation Linker.app")
    elif sys.platform == 'win32':
        print("Output: dist/Citation Linker.exe")
    else:
        print("Output: dist/Citation Linker")

def main():
    # Change to build_scripts directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    clean_build()
    install_dependencies()
    build_executable()

if __name__ == '__main__':
    main()
