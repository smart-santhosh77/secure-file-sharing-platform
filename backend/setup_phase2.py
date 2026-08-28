import subprocess
import sys

def install_dependencies():
    """Install additional dependencies for Phase 2"""
    packages = [
        'cryptography>=40.0.1',
        'pycryptodome>=3.17.0',
    ]
    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

if __name__ == '__main__':
    install_dependencies()
    print("Phase 2 dependencies installed successfully!")
