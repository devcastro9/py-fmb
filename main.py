import os
import re

PROCEDURE = "carga_prr0402g"   # Procedimiento a buscar
PATH      = r"C:\ruta\a\tus\archivos" # Carpeta raíz
EXTENSIONS = (".fmb", ".rdf", ".pll")

results = []

for root, dirs, files in os.walk(PATH):
    for file in files:
        if file.lower().endswith(EXTENSIONS):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "rb") as f:
                    content = f.read().decode("latin-1", errors="ignore")
                if re.search(PROCEDURE, content, re.IGNORECASE):
                    ext = os.path.splitext(file)[1].upper()
                    results.append((ext, filepath))
            except Exception as e:
                print(f"Error leyendo {filepath}: {e}")

print(f"\n{'='*55}")
print(f"Búsqueda: '{PROCEDURE}'")
print(f"{'='*55}")

by_type = {}
for ext, path in results:
    by_type.setdefault(ext, []).append(path)

for ext, paths in sorted(by_type.items()):
    print(f"\nArchivos {ext} ({len(paths)}):")
    for p in paths:
        print(f"   → {p}")

print(f"\n{'='*55}")
print(f"  Total encontrados: {len(results)} archivo(s)")
print(f"{'='*55}\n")