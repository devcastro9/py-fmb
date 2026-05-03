"""
╔══════════════════════════════════════════════════════════════════╗
║   BUSCADOR DE PROCEDIMIENTOS EN ORACLE FORMS/REPORTS - AIX       ║
║   Ejecutar desde Windows, busca en servidor AIX via SSH          ║
╚══════════════════════════════════════════════════════════════════╝

Requisito: pip install paramiko
"""

import re
import sys
import os
import io
from datetime import datetime

try:
    import paramiko
except ImportError:
    print("❌ Falta la librería 'paramiko'. Instálala con:")
    print("   pip install paramiko")
    sys.exit(1)

# ╔══════════════════════════════════════════════════════════════════╗
# ║                     CONFIGURACIÓN                                ║
# ╚══════════════════════════════════════════════════════════════════╝

SSH_HOST     = "192.168.1.100"          # IP o hostname del servidor AIX
SSH_PORT     = 22                        # Puerto SSH (por defecto 22)
SSH_USER     = "tu_usuario"              # Usuario SSH
SSH_PASSWORD = "tu_password"             # Contraseña SSH

PROCEDURE    = "NOMBRE_PROCEDIMIENTO"    # Procedimiento a buscar (case-insensitive)

# Rutas a escanear en el servidor AIX (puede ser más de una)
REMOTE_PATHS = [
    "/oracle/forms",
    "/oracle/reports",
    # "/app/custom/forms",    # Agrega más rutas si es necesario
]

# Extensiones de archivos Oracle a analizar
EXTENSIONS = (".fmb", ".fmx", ".rdf", ".rep", ".pll", ".plx", ".olb", ".mmb")

# Tamaño máximo de archivo a leer en MB (evita archivos enormes)
MAX_FILE_SIZE_MB = 50

# Archivo de reporte de salida (se genera en la carpeta donde ejecutas el script)
OUTPUT_REPORT = f"reporte_busqueda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# ╔══════════════════════════════════════════════════════════════════╝


# ── Colores para consola Windows ──────────────────────────────────
class C:
    OK      = "\033[92m"   # Verde
    WARN    = "\033[93m"   # Amarillo
    ERR     = "\033[91m"   # Rojo
    BOLD    = "\033[1m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    RESET   = "\033[0m"

def enable_windows_ansi():
    """Habilita colores ANSI en Windows 10+"""
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def log(msg, color="", file=None):
    print(f"{color}{msg}{C.RESET}")
    if file:
        # Escribir al reporte sin códigos de color
        clean = re.sub(r'\033\[[0-9;]*m', '', msg)
        file.write(clean + "\n")

def header(title, file=None):
    line = "═" * 60
    log(f"\n{C.BOLD}{C.BLUE}{line}", file=file)
    log(f"  {title}", file=file)
    log(f"{line}{C.RESET}", file=file)


def conectar_ssh():
    """Establece conexión SSH al servidor AIX."""
    log(f"\n🔌 Conectando a {SSH_HOST}:{SSH_PORT} como '{SSH_USER}'...", C.CYAN)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASSWORD,
            timeout=30,
            look_for_keys=False,
            allow_agent=False
        )
        log(f"✅ Conexión exitosa a {SSH_HOST}", C.OK)
        return client
    except paramiko.AuthenticationException:
        log("❌ Error: Usuario o contraseña incorrectos.", C.ERR)
        sys.exit(1)
    except Exception as e:
        log(f"❌ Error de conexión: {e}", C.ERR)
        sys.exit(1)


def listar_archivos(sftp, remote_path, extensions, max_size_bytes):
    """
    Recorre recursivamente la ruta remota en AIX
    y devuelve lista de (filepath, size) con las extensiones indicadas.
    """
    encontrados = []

    def _walk(path):
        try:
            items = sftp.listdir_attr(path)
        except PermissionError:
            log(f"  ⚠️  Sin permisos en: {path}", C.WARN)
            return
        except Exception as e:
            log(f"  ⚠️  Error accediendo {path}: {e}", C.WARN)
            return

        for item in items:
            full_path = f"{path}/{item.filename}"
            # Es directorio
            if item.st_mode and (item.st_mode & 0o40000):
                _walk(full_path)
            else:
                ext = os.path.splitext(item.filename)[1].lower()
                if ext in extensions:
                    size = item.st_size or 0
                    if size <= max_size_bytes:
                        encontrados.append((full_path, size))
                    else:
                        log(f"  ⏭️  Omitido (>{MAX_FILE_SIZE_MB}MB): {full_path}", C.WARN)

    _walk(remote_path)
    return encontrados


def buscar_en_archivo(sftp, filepath):
    """Lee el archivo remoto y busca el procedimiento."""
    try:
        with sftp.open(filepath, "rb") as f:
            content = f.read().decode("latin-1", errors="ignore")
        return bool(re.search(PROCEDURE, content, re.IGNORECASE))
    except Exception as e:
        return None  # None indica error de lectura


def main():
    enable_windows_ansi()

    # Abrir archivo de reporte
    report_file = open(OUTPUT_REPORT, "w", encoding="utf-8")

    header("BUSCADOR DE PROCEDIMIENTOS - ORACLE FORMS/REPORTS en AIX", report_file)
    log(f"  🔍 Procedimiento : {C.BOLD}{PROCEDURE}", file=report_file)
    log(f"  🖥️  Servidor AIX  : {SSH_HOST}", file=report_file)
    log(f"  📂 Rutas         : {', '.join(REMOTE_PATHS)}", file=report_file)
    log(f"  📎 Extensiones   : {', '.join(EXTENSIONS)}", file=report_file)
    log(f"  📅 Fecha         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=report_file)

    # ── Conexión SSH ──────────────────────────────────────────────
    client = conectar_ssh()
    sftp   = client.open_sftp()

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    todos_archivos = []

    # ── Listar archivos en todas las rutas ────────────────────────
    header("FASE 1: Listando archivos remotos...", report_file)
    for rpath in REMOTE_PATHS:
        log(f"\n  📁 Escaneando: {rpath}", C.CYAN)
        archivos = listar_archivos(sftp, rpath, EXTENSIONS, max_bytes)
        log(f"     → {len(archivos)} archivo(s) encontrado(s)", C.OK)
        todos_archivos.extend(archivos)

    total = len(todos_archivos)
    log(f"\n  📊 Total a analizar: {C.BOLD}{total} archivo(s){C.RESET}", file=report_file)

    if total == 0:
        log("\n⚠️  No se encontraron archivos con esas extensiones en las rutas indicadas.", C.WARN, report_file)
        sftp.close()
        client.close()
        report_file.close()
        return

    # ── Buscar procedimiento ──────────────────────────────────────
    header("FASE 2: Buscando procedimiento en archivos...", report_file)

    resultados  = []   # (ext, filepath)
    errores     = []
    procesados  = 0

    for filepath, size in todos_archivos:
        procesados += 1
        ext      = os.path.splitext(filepath)[1].upper()
        filename = filepath.split("/")[-1]
        kb       = size / 1024

        # Barra de progreso simple
        pct = int((procesados / total) * 40)
        bar = f"[{'█'*pct}{'░'*(40-pct)}] {procesados}/{total}"
        print(f"\r  {C.CYAN}{bar}  {filename[:30]:<30}{C.RESET}", end="", flush=True)

        encontrado = buscar_en_archivo(sftp, filepath)

        if encontrado is True:
            resultados.append((ext, filepath, kb))
        elif encontrado is None:
            errores.append(filepath)

    print()  # Salto de línea tras la barra

    # ── Reporte final ─────────────────────────────────────────────
    header("RESULTADOS", report_file)

    if not resultados:
        log(f"\n  ℹ️  El procedimiento '{PROCEDURE}' NO fue encontrado en ningún archivo.", C.WARN, report_file)
    else:
        # Agrupar por extensión
        by_ext = {}
        for ext, path, kb in resultados:
            by_ext.setdefault(ext, []).append((path, kb))

        for ext in sorted(by_ext.keys()):
            paths = by_ext[ext]
            log(f"\n  {C.BOLD}📂 {ext}  ({len(paths)} archivo(s)){C.RESET}", file=report_file)
            for path, kb in paths:
                log(f"     ✅  {path}  [{kb:.1f} KB]", C.OK, report_file)

        log(f"\n  {'─'*55}", file=report_file)
        log(f"  {C.BOLD}✅ Total con '{PROCEDURE}': {len(resultados)} archivo(s){C.RESET}", file=report_file)

    if errores:
        log(f"\n  ⚠️  Archivos con error de lectura ({len(errores)}):", C.WARN, report_file)
        for e in errores:
            log(f"     ⚠️  {e}", C.WARN, report_file)

    log(f"\n  📄 Reporte guardado en: {C.BOLD}{OUTPUT_REPORT}", C.CYAN, report_file)

    # ── Cierre ────────────────────────────────────────────────────
    sftp.close()
    client.close()
    report_file.close()
    log("\n  🔌 Conexión SSH cerrada.\n", C.CYAN)


if __name__ == "__main__":
    main()