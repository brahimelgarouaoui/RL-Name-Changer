#!/usr/bin/env python3
"""
Mitmproxy Certificate Setup Script for Windows
Alternative Python-based setup script
"""

import os
import sys
import subprocess
import tempfile
import urllib.request
import ssl
from pathlib import Path


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Re-run the script with administrator privileges."""
    try:
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    except Exception as e:
        print(f"Failed to run as administrator: {e}")
        return False
    return True


def check_python():
    """Check if Python is properly installed."""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print("ERROR: Python 3.7 or higher is required")
            return False
        print(f"[INFO] Python {version.major}.{version.minor}.{version.micro} found")
        return True
    except Exception as e:
        print(f"ERROR: Python check failed: {e}")
        return False


def install_mitmproxy():
    """Install mitmproxy if not already installed."""
    try:
        import mitmproxy
        print("[INFO] mitmproxy is already installed")
        return True
    except ImportError:
        print("[INFO] mitmproxy not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mitmproxy"])
            print("[INFO] mitmproxy installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install mitmproxy: {e}")
            return False


def generate_certificates():
    """Generate mitmproxy certificates."""
    print("[INFO] Generating mitmproxy certificates...")
    
    # Get mitmproxy config directory
    config_dir = Path.home() / ".mitmproxy"
    config_dir.mkdir(exist_ok=True)
    
    cert_file = config_dir / "mitmproxy-ca-cert.pem"
    
    if cert_file.exists():
        print(f"[INFO] Certificate already exists at: {cert_file}")
        return cert_file
    
    try:
        # Import after installation
        from mitmproxy.certs import CertStore
        
        # Generate certificates
        store = CertStore.from_store(str(config_dir), "mitmproxy", 2048)
        
        if cert_file.exists():
            print(f"[INFO] Certificate generated at: {cert_file}")
            return cert_file
        else:
            print("ERROR: Certificate generation failed")
            return None
            
    except Exception as e:
        print(f"ERROR: Failed to generate certificates: {e}")
        return None


def install_certificate(cert_file):
    """Install certificate to Windows certificate store."""
    print("[INFO] Installing certificate to Windows certificate store...")
    
    # Convert PEM to CRT for Windows
    crt_file = cert_file.with_suffix('.crt')
    try:
        with open(cert_file, 'rb') as src, open(crt_file, 'wb') as dst:
            dst.write(src.read())
        print(f"[INFO] Certificate converted to: {crt_file}")
    except Exception as e:
        print(f"ERROR: Failed to convert certificate: {e}")
        return False
    
    # Install using certutil
    try:
        subprocess.check_call([
            "certutil", "-addstore", "-f", "ROOT", str(crt_file)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[INFO] Certificate installed to ROOT store")
        return True
    except subprocess.CalledProcessError:
        # Try user store if system store fails
        try:
            subprocess.check_call([
                "certutil", "-addstore", "-user", "-f", "ROOT", str(crt_file)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[INFO] Certificate installed to user ROOT store")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install certificate: {e}")
            return False


def verify_installation():
    """Verify certificate installation."""
    print("[INFO] Verifying certificate installation...")
    
    try:
        # Check if certificate is in ROOT store
        result = subprocess.run([
            "certutil", "-store", "ROOT"
        ], capture_output=True, text=True)
        
        if "mitmproxy" in result.stdout.lower():
            print("[SUCCESS] Certificate verified in ROOT store")
            return True
        
        # Check user store
        result = subprocess.run([
            "certutil", "-store", "-user", "ROOT"
        ], capture_output=True, text=True)
        
        if "mitmproxy" in result.stdout.lower():
            print("[SUCCESS] Certificate verified in user ROOT store")
            return True
        
        print("[WARNING] Certificate verification failed, but installation may have succeeded")
        return False
        
    except Exception as e:
        print(f"[WARNING] Certificate verification failed: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("Mitmproxy Certificate Setup for Windows")
    print("=" * 60)
    print()
    
    # Check if running as administrator
    if not is_admin():
        print("ERROR: This script must be run as Administrator!")
        print("Attempting to restart with administrator privileges...")
        if run_as_admin():
            return 0
        else:
            print("Failed to obtain administrator privileges.")
            print("Please right-click this script and select 'Run as administrator'")
            input("Press Enter to exit...")
            return 1
    
    print("[INFO] Administrator privileges confirmed")
    print()
    
    # Check Python installation
    if not check_python():
        input("Press Enter to exit...")
        return 1
    
    # Install mitmproxy
    if not install_mitmproxy():
        input("Press Enter to exit...")
        return 1
    
    # Generate certificates
    cert_file = generate_certificates()
    if not cert_file:
        input("Press Enter to exit...")
        return 1
    
    # Install certificate
    if not install_certificate(cert_file):
        input("Press Enter to exit...")
        return 1
    
    # Verify installation
    verify_installation()
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("The mitmproxy certificate has been installed.")
    print(f"Certificate location: {cert_file.with_suffix('.crt')}")
    print()
    print("You can now use the RL Name Changer application.")
    print()
    print("NOTE: If you encounter any SSL/TLS issues:")
    print("1. Restart your browser/applications")
    print("2. Check Windows certificate store (certmgr.msc)")
    print("3. Re-run this script if needed")
    print()
    
    input("Press Enter to exit...")
    return 0


if __name__ == "__main__":
    sys.exit(main())