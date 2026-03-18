# 🐧 The Penguin Was Replace

## 📌 Procesos básicos del equipo

---

## 1. Activar entorno virtual

```bash
source venv/bin/activate
# Activa el entorno virtual para usar dependencias aisladas del proyecto.
```

## 2. Instalar paquetes

```bash
pip install nombre_paquete
# Instala un paquete nuevo dentro del entorno virtual activo.
```
Ejemplo:
```bash
pip install pygame
# Instala la librería pygame en el entorno virtual del proyecto.
```

## 3. Agregar paquetes instalados a requirements.txt
```bash
pip freeze > requirements.txt
# Guarda todas las dependencias instaladas y sus versiones en requirements.txt.
```

## 4. Agregar archivo al .gitignore
```bash
echo "nombre_archivo_o_carpeta" >> .gitignore
# Agrega archivos o carpetas que Git no debe rastrear.
```
Ejemplo:
```
echo "venv/" >> .gitignore
# Evita que Git rastree la carpeta del entorno virtual.
```

## 5. Crear una nueva rama desde staging
```bash
git checkout staging
# Cambia a la rama staging para usarla como base.

git pull origin staging
# Actualiza la rama staging local con la última versión remota.

git checkout -b [NUEVA_RAMA]
# Crea una nueva rama basada en staging y cambia a ella.

git push -u origin [NUEVA_RAMA]
# Sube la nueva rama al remoto y la vincula localmente.
```

## 6. Recibir cambios de staging en tu rama
```bash
git checkout [TU_RAMA]
# Cambia a tu rama de trabajo actual.

git fetch origin
# Trae información actualizada del remoto sin modificar tu rama.

git merge origin/staging
# Integra en tu rama los últimos cambios existentes en staging.
```

## 7. Integrar tu rama a staging
```bash
git checkout staging
# Cambia a la rama staging para integrar cambios.

git pull origin staging
# Actualiza staging local antes de fusionar otra rama.

git merge [TU_RAMA]
# Fusiona los cambios de tu rama dentro de staging.

git push origin staging
# Sube al remoto la versión actualizada de staging.
```

## 8. Clonar el repositorio

```bash
git clone https://github.com/Leonshy/the-penguin-was-replace.git
# Descarga el repositorio remoto a tu computadora local.
```

## 9. Instalar dependencias desde requirements.txt
```bash
pip install -r requirements.txt
# Instala todas las dependencias necesarias definidas en requirements.txt.
```
## 10. Ver ramas disponibles
``` bash
git branch
# Lista todas las ramas locales del repositorio.
git branch -a
# Lista ramas locales y remotas disponibles.
```

## 11. Guardar cambios (commit)
``` bash
git add .
# Prepara todos los cambios para ser guardados.

git commit -m "Descripción del cambio"
# Guarda los cambios con un mensaje descriptivo.
```

## 12. Subir cambios de una rama
```bash
git push origin [TU_RAMA]
# Envía los cambios de tu rama al repositorio remoto.
```

## 13. Traer cambios de una rama remota
```bash 
git pull origin [RAMA]
# Descarga y mezcla los cambios de la rama remota especificada.
```

## 14. Resolver conflictos
```bash
git status
# Identifica archivos en conflicto tras un merge.

git add .
# Marca conflictos como resueltos.

git commit -m "Resolución de conflictos"
# Finaliza el proceso de merge tras resolver conflictos.
```

## 15. Eliminar una rama local
```bash
git branch -d [RAMA]
# Elimina una rama local que ya fue integrada.
```

## 16. Eliminar una rama remota
```bash
git push origin --delete [RAMA]
# Elimina una rama del repositorio remoto.
```

## 17. Ver historial del proyecto
```bash
git log --oneline --graph --all --decorate
# Muestra el historial de commits de forma visual y resumida.
```

## 18. Limpiar archivos temporales Python
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
# Elimina carpetas temporales generadas por Python.
```

## 19. Cambiar de rama
```bash
git checkout [RAMA]
# Cambia a la rama especificada.

git switch [RAMA]
# Alternativa moderna para cambiar de rama.
```

## ⚠️ Buenas prácticas
No trabajar directamente en main
Actualizar tu rama antes de hacer merge
Usar mensajes de commit claros
No subir venv, __pycache__ ni archivos temporales