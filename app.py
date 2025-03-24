import os
import uuid
import logging
import subprocess
import re
import json
import shutil
import unicodedata
import traceback
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from urllib.parse import urlparse
from flask_cors import CORS
import yt_dlp
import zipfile
import requests
import time
import threading

app = Flask(__name__)
CORS(app)

# Configuración de carpetas
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
TOOLS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools')
FFMPEG_PATH = os.path.join(TOOLS_FOLDER, 'ffmpeg.exe')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(TOOLS_FOLDER, exist_ok=True)

# Configuración de tiempo de vida de los archivos (en segundos)
FILE_LIFETIME = 3600  # 1 hora

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
app.logger.setLevel(logging.DEBUG)

# Función para descargar FFmpeg si no está disponible
def ensure_ffmpeg():
    if not os.path.exists(FFMPEG_PATH):
        logger.info("FFmpeg no encontrado. Descargando...")
        try:
            # URL de FFmpeg para Windows (versión estática)
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            zip_path = os.path.join(TOOLS_FOLDER, "ffmpeg.zip")
            
            # Descargar el archivo zip
            response = requests.get(ffmpeg_url, stream=True)
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extraer el archivo zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(TOOLS_FOLDER)
            
            # Encontrar el ejecutable de FFmpeg en la carpeta extraída
            for root, dirs, files in os.walk(TOOLS_FOLDER):
                for file in files:
                    if file == "ffmpeg.exe":
                        ffmpeg_exe = os.path.join(root, file)
                        # Mover a la ubicación correcta
                        shutil.copy(ffmpeg_exe, FFMPEG_PATH)
                        logger.info(f"FFmpeg copiado a {FFMPEG_PATH}")
                        break
            
            # Limpiar archivos temporales
            os.remove(zip_path)
            logger.info("FFmpeg descargado y configurado correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al descargar FFmpeg: {str(e)}")
            return False
    return True

# Asegurar que FFmpeg esté disponible al iniciar la aplicación
ensure_ffmpeg()

# Función para limpiar nombre de archivo
def sanitize_filename(filename):
    if not filename:
        return "video"
    
    # Normalizar unicode
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
    
    # Eliminar caracteres no permitidos en nombres de archivo en Windows
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)
    
    # Reemplazar espacios y otros caracteres problemáticos
    cleaned = re.sub(r'[\s\-,;]+', "_", cleaned)
    
    # Eliminar caracteres no ASCII
    cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned)
    
    # Eliminar puntos al final del nombre (problema en Windows)
    cleaned = cleaned.rstrip('.')
    
    # Limitar la longitud del nombre del archivo
    if len(cleaned) > 50:
        cleaned = cleaned[:50]
    
    # Asegurarse de que el nombre no esté vacío
    if not cleaned:
        cleaned = "video"
    
    return cleaned

# Función para validar URL
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# Función para detectar la plataforma
def detect_platform(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'YouTube'
    elif 'instagram.com' in url:
        return 'Instagram'
    elif 'facebook.com' in url or 'fb.com' in url:
        return 'Facebook'
    elif 'twitter.com' in url or 'x.com' in url:
        return 'Twitter'
    elif 'tiktok.com' in url:
        return 'TikTok'
    else:
        return 'Otra plataforma'

# Función para eliminar archivos antiguos
def cleanup_old_files():
    while True:
        try:
            now = time.time()
            for download_id in os.listdir(DOWNLOAD_FOLDER):
                download_path = os.path.join(DOWNLOAD_FOLDER, download_id)
                if os.path.isdir(download_path):
                    # Verificar la antigüedad de la carpeta
                    creation_time = os.path.getctime(download_path)
                    if now - creation_time > FILE_LIFETIME:
                        logger.info(f"Eliminando carpeta antigua: {download_path}")
                        shutil.rmtree(download_path)
        except Exception as e:
            logger.error(f"Error al limpiar archivos: {str(e)}")
        time.sleep(60)  # Verificar cada minuto

# Iniciar el hilo de limpieza
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

def download_video(video_url, format_option='mp4'):
    try:
        # Validar URL
        if not is_valid_url(video_url):
            logger.error("URL inválida")
            return jsonify({'error': 'URL inválida'}), 400
        
        # Generar un ID único para la descarga
        download_id = str(uuid.uuid4())
        
        # Crear directorio para la descarga
        download_path = os.path.join(DOWNLOAD_FOLDER, download_id)
        os.makedirs(download_path, exist_ok=True)
        
        # Crear un directorio temporal para archivos intermedios
        temp_dir = os.path.join(download_path, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Asegurar que FFmpeg esté disponible
        if not ensure_ffmpeg():
            logger.error("No se pudo configurar FFmpeg")
            return jsonify({'error': 'No se pudo configurar FFmpeg'}), 500
        
        # Obtener información del video
        logger.info(f"Obteniendo información del video: {video_url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'restrictfilenames': True,
            'windowsfilenames': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_title = sanitize_filename(info.get('title', 'video'))
            thumbnail = info.get('thumbnail', '')
            platform = info.get('extractor', 'unknown')
        
        logger.info(f"Título del video: {video_title}")
        
        # Preparar comando para descargar
        if format_option == 'mp3':
            output_file = os.path.join(download_path, f"{video_title}.mp3")
            cmd = ['yt-dlp', '--no-playlist', '--no-warnings', '--extract-audio', '--audio-format', 'mp3', '--audio-quality', '0']
            cmd.extend(['-o', output_file])
            cmd.append(video_url)
            
            # Ejecutar comando
            logger.debug(f"Ejecutando comando: {' '.join(cmd)}")
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Verificar si el archivo se descargó correctamente
            file_exists = os.path.exists(output_file) and os.path.getsize(output_file) > 0
            
        else:  # mp4
            # Nombres de archivos para video y audio
            video_file = os.path.join(temp_dir, f"{video_title}_video.mp4")
            audio_file = os.path.join(temp_dir, f"{video_title}_audio.m4a")
            output_file = os.path.join(download_path, f"{video_title}.mp4")
            
            # 1. Descargar el mejor video (sin audio)
            video_cmd = [
                'yt-dlp', 
                '--no-playlist', 
                '--no-warnings',
                '--geo-bypass',
                '--restrict-filenames',
                '--windows-filenames',
                '-f', 'bestvideo[height>=1080][ext=mp4]/bestvideo[ext=mp4]/bestvideo/best',
                '-o', video_file,
                video_url
            ]
            
            logger.debug(f"Descargando video: {' '.join(video_cmd)}")
            video_process = subprocess.run(video_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            video_stdout = video_process.stdout
            video_stderr = video_process.stderr
            logger.debug(f"Salida de video: {video_stdout}")
            logger.debug(f"Error de video: {video_stderr}")
            
            # Verificar si se descargó el video
            video_exists = os.path.exists(video_file) and os.path.getsize(video_file) > 0
            
            if not video_exists:
                logger.warning("No se pudo descargar el video de alta calidad, intentando con formato alternativo")
                
                # Intentar con un formato más simple
                alt_video_cmd = [
                    'yt-dlp',
                    '--no-playlist',
                    '--no-warnings',
                    '--geo-bypass',
                    '--restrict-filenames',
                    '--windows-filenames',
                    '-f', 'best[ext=mp4]/best',
                    '-o', video_file,
                    video_url
                ]
                
                logger.debug(f"Ejecutando comando alternativo: {' '.join(alt_video_cmd)}")
                alt_video_process = subprocess.run(alt_video_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Verificar nuevamente si el video existe
                video_exists = os.path.exists(video_file) and os.path.getsize(video_file) > 0
                
                if not video_exists:
                    logger.error("No se pudo descargar el video")
                    return jsonify({'error': 'No se pudo descargar el video'}), 500
            
            # 2. Descargar el mejor audio
            audio_cmd = [
                'yt-dlp',
                '--no-playlist',
                '--no-warnings',
                '--geo-bypass',
                '--restrict-filenames',
                '--windows-filenames',
                '-f', 'bestaudio[ext=m4a]/bestaudio/best',
                '-o', audio_file,
                video_url
            ]
            
            logger.debug(f"Descargando audio: {' '.join(audio_cmd)}")
            audio_process = subprocess.run(audio_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            audio_stdout = audio_process.stdout
            audio_stderr = audio_process.stderr
            logger.debug(f"Salida de audio: {audio_stdout}")
            logger.debug(f"Error de audio: {audio_stderr}")
            
            # Verificar si se descargó el audio
            audio_exists = os.path.exists(audio_file) and os.path.getsize(audio_file) > 0
            
            if not audio_exists:
                logger.warning("No se pudo descargar el audio, continuando sin audio")
                audio_file = None
            
            # 3. Combinar video y audio con FFmpeg
            if audio_file:
                ffmpeg_cmd = [
                    FFMPEG_PATH,
                    '-i', video_file,
                    '-i', audio_file,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-strict', 'experimental',
                    output_file
                ]
                
                logger.debug(f"Combinando archivos: {' '.join(ffmpeg_cmd)}")
                ffmpeg_process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                ffmpeg_stdout = ffmpeg_process.stdout
                ffmpeg_stderr = ffmpeg_process.stderr
                logger.debug(f"Salida de ffmpeg: {ffmpeg_stdout}")
                logger.debug(f"Error de ffmpeg: {ffmpeg_stderr}")
                
                # Verificar si se creó el archivo final
                file_exists = os.path.exists(output_file) and os.path.getsize(output_file) > 0
                
                # Si ffmpeg falló, intentar con método alternativo
                if not file_exists:
                    logger.warning("FFmpeg falló, intentando con método alternativo")
                    
                    # Intentar con yt-dlp directamente
                    alt_cmd = [
                        'yt-dlp',
                        '--no-playlist',
                        '--no-warnings',
                        '--geo-bypass',
                        '--restrict-filenames',
                        '--windows-filenames',
                        '-f', 'best[ext=mp4]/best',
                        '-o', output_file,
                        video_url
                    ]
                    
                    logger.debug(f"Ejecutando comando alternativo: {' '.join(alt_cmd)}")
                    alt_process = subprocess.run(alt_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    # Verificar nuevamente si el archivo existe
                    file_exists = os.path.exists(output_file) and os.path.getsize(output_file) > 0
            else:
                # Si no hay audio, copiar el video como archivo final
                shutil.copy(video_file, output_file)
                file_exists = True
            
            # Limpiar archivos temporales
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"No se pudieron eliminar los archivos temporales: {str(e)}")
        
        if file_exists:
            # Preparar la respuesta
            response = {
                'success': True,
                'message': 'Descarga completada',
                'download_id': download_id,
                'filename': os.path.basename(output_file),
                'title': video_title,
                'thumbnail': thumbnail,
                'platform': platform,
                'download_url': f'/get_file/{download_id}/{os.path.basename(output_file)}'
            }
            
            logger.info(f"Enviando respuesta exitosa: {response}")
            return jsonify(response)
        else:
            error_msg = "No se pudo descargar el archivo"
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 500
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error en la descarga: {error_message}")
        logger.error(traceback.format_exc())
        
        # Mensaje de error más amigable
        if "HTTP Error 400" in error_message:
            error_message = "YouTube ha bloqueado la solicitud. Esto puede ocurrir cuando YouTube detecta descargas automatizadas."
        elif "[Errno 22]" in error_message:
            error_message = "Error en el nombre del archivo. Intentando con un nombre más simple."
        
        return jsonify({'error': error_message}), 500

@app.route('/download', methods=['POST'])
def download_video_route():
    data = request.json
    video_url = data.get('url')
    format_option = data.get('format', 'mp4')
    
    return download_video(video_url, format_option)

@app.route('/get_file/<download_id>/<filename>', methods=['GET'])
def get_file(download_id, filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, download_id, filename)
    if os.path.exists(file_path):
        logger.info(f"Enviando archivo: {file_path}")
        # Programar la eliminación del archivo después de la descarga
        threading.Thread(target=lambda: (time.sleep(10), shutil.rmtree(os.path.join(DOWNLOAD_FOLDER, download_id)))).start()
        return send_from_directory(os.path.join(DOWNLOAD_FOLDER, download_id), filename, as_attachment=True)
    else:
        logger.error(f"Archivo no encontrado: {file_path}")
        # Buscar cualquier archivo en la carpeta
        download_path = os.path.join(DOWNLOAD_FOLDER, download_id)
        if os.path.exists(download_path):
            files = os.listdir(download_path)
            if files:
                alternative_file = os.path.join(download_path, files[0])
                logger.info(f"Enviando archivo alternativo: {alternative_file}")
                return send_from_directory(os.path.join(DOWNLOAD_FOLDER, download_id), files[0], as_attachment=True)
        
        return jsonify({'error': 'Archivo no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)
