import os, re

PROCEDURE = "NOMBRE_PROCEDIMIENTO"
PATH = "/ruta/a/tus/fmb"
results = []

for root, dirs, files in os.walk(PATH):
    for file in files:
        if file.endswith(".fmb"):
            filepath = os.path.join(root, file)
            with open(filepath, "rb") as f:
                content = f.read().decode("latin-1", errors="ignore")
            if re.search(PROCEDURE, content, re.IGNORECASE):
                results.append(filepath)

print(f"\n{'='*50}")
print(f"Formularios que usan '{PROCEDURE}':")
for r in results:
    print(f"  → {r}")
print(f"\nTotal: {len(results)} formulario(s)")