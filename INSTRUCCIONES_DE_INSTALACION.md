# Instrucciones de Instalación para VideoDownloader

## 1. Instalar Python

Primero, necesitas instalar Python en tu sistema:

1. Ve a [python.org](https://www.python.org/downloads/)
2. Descarga la última versión de Python para Windows
3. Ejecuta el instalador
4. **IMPORTANTE**: Marca la casilla "Add Python to PATH" durante la instalación
5. Haz clic en "Install Now"

## 2. Instalar FFmpeg (necesario para la conversión a MP3)

1. Descarga FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html#build-windows) o desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (versión "essentials")
2. Extrae el archivo zip descargado
3. Copia los archivos de la carpeta "bin" a una ubicación permanente (por ejemplo, `C:\ffmpeg\bin`)
4. Añade esta ubicación a tu PATH:
   - Busca "Variables de entorno" en el menú de inicio
   - Haz clic en "Variables de entorno"
   - En la sección "Variables del sistema", selecciona "Path" y haz clic en "Editar"
   - Haz clic en "Nuevo" y añade la ruta donde colocaste los archivos bin de FFmpeg (por ejemplo, `C:\ffmpeg\bin`)
   - Haz clic en "Aceptar" en todas las ventanas

## 3. Instalar las dependencias y ejecutar la aplicación

1. Abre una nueva ventana de PowerShell o Command Prompt (para asegurarte de que los cambios en PATH se apliquen)
2. Navega hasta la carpeta del proyecto:
   ```
   cd e:\Donwloader2
   ```
3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Ejecuta la aplicación:
   ```
   python app.py
   ```
5. Abre tu navegador y ve a `http://localhost:5000`

## Solución de problemas

Si encuentras algún error durante la instalación o ejecución:

- Asegúrate de que Python está correctamente añadido al PATH
- Verifica que FFmpeg está correctamente instalado ejecutando `ffmpeg -version` en la terminal
- Si tienes problemas con la instalación de dependencias, intenta:
  ```
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  ```

## Nota sobre el uso

Esta aplicación utiliza yt-dlp para descargar videos. Ten en cuenta que:

1. Debes respetar los términos de servicio de las plataformas
2. No utilices la aplicación para descargar contenido con derechos de autor sin permiso
3. La aplicación está diseñada para uso personal y educativo
