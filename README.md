# VideoDownloader

Una aplicación web minimalista y profesional para descargar videos de YouTube y otras redes sociales.

## Características

- Descarga videos de YouTube, Instagram, Facebook, Twitter, TikTok y más
- Opción para descargar en formato MP4 (video) o MP3 (audio)
- Interfaz de usuario intuitiva y responsive
- Diseño minimalista y profesional

## Requisitos

- Python 3.7 o superior
- Flask
- yt-dlp
- FFmpeg (para la conversión de audio)

## Instalación

1. Clona este repositorio o descarga los archivos
2. Instala las dependencias:

```
pip install -r requirements.txt
```

3. Instala FFmpeg (necesario para la conversión a MP3):
   - Windows: Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y añade a PATH
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

## Uso

1. Ejecuta la aplicación:

```
python app.py
```

2. Abre tu navegador y ve a `http://localhost:5000`
3. Pega la URL del video que deseas descargar
4. Selecciona el formato (MP4 o MP3)
5. Haz clic en "Descargar"

## Tecnologías utilizadas

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Biblioteca de descarga: yt-dlp
- Iconos: Font Awesome
- Fuentes: Google Fonts (Poppins)

## Limitaciones

- La aplicación está diseñada para uso personal y educativo
- Respeta los términos de servicio de las plataformas
- No utilices la aplicación para descargar contenido con derechos de autor sin permiso

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
