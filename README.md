# py-fmb 🔍

Buscador de dependencias en Oracle Forms (archivos .fmb) mediante conexión remota SSH/SFTP.

## 📋 Descripción

`py-fmb` es una herramienta de línea de comandos escrita en Python que permite buscar y analizar archivos de Oracle Forms en servidores remotos a través de conexiones SSH. Ideal para encontrar dependencias, procedimientos y realizar auditorías de código en proyectos Oracle Forms distribuidos.

## ✨ Características

- 🔐 Conexión segura mediante SSH/SFTP
- 📁 Búsqueda recursiva en múltiples directorios
- 🎯 Filtrado por extensiones de archivo
- 📏 Control de tamaño máximo de archivos a procesar
- 📊 Sistema de logging integrado
- ⚡ Procesamiento eficiente de archivos grandes por chunks

## 🛠️ Requisitos

- Python 3.6+
- paramiko

## 📦 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/devcastro9/py-fmb.git
cd py-fmb
```

2. Instala las dependencias:
```bash
pip install paramiko
```

## 🚀 Uso

### Sintaxis básica

```bash
python main.py --host <servidor> --user <usuario> --password <contraseña> \
               --procedure <procedimiento> --paths <rutas> --extensions <extensiones>
```

### Parámetros

| Parámetro | Requerido | Descripción | Ejemplo |
|-----------|-----------|-------------|---------|
| `--host` | ✅ | Dirección del servidor remoto | `192.168.1.100` |
| `--port` | ❌ | Puerto SSH (default: 22) | `22` |
| `--user` | ✅ | Usuario SSH | `oracle` |
| `--password` | ✅ | Contraseña SSH | `password123` |
| `--procedure` | ✅ | Procedimiento a ejecutar/buscar | `PKG_USUARIOS` |
| `--paths` | ❌ | Rutas a buscar (múltiples) | `/opt/forms /app/oracle` |
| `--extensions` | ❌ | Extensiones de archivo | `.fmb .pll .mmb` |
| `--max-size-mb` | ❌ | Tamaño máximo en MB | `50` |

### Ejemplos de uso

**Buscar procedimientos en archivos .fmb:**
```bash
python main.py --host 192.168.1.100 --user oracle --password pass123 \
               --procedure "PKG_FACTURACION" \
               --paths /opt/oracle/forms \
               --extensions .fmb .pll
```

**Buscar en múltiples directorios con límite de tamaño:**
```bash
python main.py --host servidor.empresa.com --port 2222 \
               --user admin --password secret \
               --procedure "PROC_VALIDACION" \
               --paths /app/forms /backup/forms \
               --extensions .fmb .mmb \
               --max-size-mb 100
```

## 📂 Estructura del proyecto

```
py-fmb/
├── main.py          # Script principal
├── README.md        # Documentación
└── .gitignore      # Archivos ignorados por Git
```

## 🔒 Seguridad

⚠️ **Advertencias importantes:**

- No incluyas contraseñas directamente en scripts
- Considera usar variables de entorno para credenciales
- Implementa autenticación por clave SSH cuando sea posible
- Revisa los permisos de acceso antes de ejecutar búsquedas

### Uso con variables de entorno (recomendado)

```bash
export SSH_HOST="192.168.1.100"
export SSH_USER="oracle"
export SSH_PASS="password123"

python main.py --host $SSH_HOST --user $SSH_USER --password $SSH_PASS \
               --procedure "MI_PROCEDIMIENTO" \
               --paths /opt/forms \
               --extensions .fmb
```

## 🐛 Solución de problemas

### Error de conexión SSH
```
Error during processing: [Errno 111] Connection refused
```
**Solución:** Verifica que el servicio SSH esté activo y el puerto sea correcto.

### Error de autenticación
```
Error during processing: Authentication failed
```
**Solución:** Verifica las credenciales y permisos del usuario.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Roadmap

- [ ] Soporte para autenticación mediante clave SSH
- [ ] Exportación de resultados a CSV/JSON
- [ ] Interfaz web básica
- [ ] Análisis de dependencias cruzadas
- [ ] Caché de resultados para búsquedas repetidas

## 📄 Licencia

Este proyecto está bajo una licencia abierta. Por favor, revisa el archivo LICENSE para más detalles.

## 👤 Autor

**devcastro9**
- GitHub: [@devcastro9](https://github.com/devcastro9)

## 🙏 Agradecimientos

- [Paramiko](https://www.paramiko.org/) - Librería SSH para Python
- Comunidad de Oracle Forms

---

⭐ Si este proyecto te ha sido útil, considera darle una estrella en GitHub.