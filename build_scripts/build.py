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

def prepare_icons():
    """Prepare icon files for the build"""
    # macOS: Create .icns from .png if needed
    if sys.platform == 'darwin':
        icns_file = Path('icon.icns')
        png_file = Path('icon.png')
        
        if not icns_file.exists() and png_file.exists():
            print("Creating icon.icns from icon.png...")
            try:
                # Create temporary iconset directory
                iconset_dir = Path('icon.iconset')
                iconset_dir.mkdir(exist_ok=True)
                
                # Generate different icon sizes using sips (macOS built-in tool)
                sizes = [16, 32, 64, 128, 256, 512, 1024]
                for size in sizes:
                    subprocess.run([
                        'sips', '-z', str(size), str(size),
                        str(png_file),
                        '--out', str(iconset_dir / f'icon_{size}x{size}.png')
                    ], check=False, capture_output=True)
                    
                    # Also create @2x versions for retina
                    if size <= 512:
                        subprocess.run([
                            'sips', '-z', str(size*2), str(size*2),
                            str(png_file),
                            '--out', str(iconset_dir / f'icon_{size}x{size}@2x.png')
                        ], check=False, capture_output=True)
                
                # Convert iconset to icns
                subprocess.run([
                    'iconutil', '-c', 'icns', str(iconset_dir)
                ], check=False)
                
                # Clean up temporary iconset
                shutil.rmtree(iconset_dir)
                
                if icns_file.exists():
                    print("[OK] Created icon.icns")
                else:
                    print("[WARNING] Could not create icon.icns, will build without icon")
            except Exception as e:
                print(f"[WARNING] Icon creation failed: {e}")
                print("Building without macOS icon...")

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
        sys.executable, '-m', 'PyInstaller',
        'citation_linker.spec',
        '--clean',  # Clean PyInstaller cache
    ], check=True)

    print("\n[OK] Build complete!")
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
    prepare_icons()
    install_dependencies()
    build_executable()

if __name__ == '__main__':
    main()
