# Buscador de dependencias en Oracle Forms
Buscador de dependencias en fmb

# Abrir Anaconda Prompt (Miniconda3)

# Crear un nuevo entorno virtual
conda create -n py-fmb python=3.10

# Activar el entorno
conda activate py-fmb

# Instalar la dependencia necesaria
pip install paramiko

python main.py ^
  --host 192.168.1.100 ^
  --port 22 ^
  --user mi_usuario ^
  --password mi_contraseña ^
  --procedure buscar ^
  --paths /home/usuario/documentos /var/log ^
  --extensions .txt .log
