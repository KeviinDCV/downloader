document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const videoUrlInput = document.getElementById('video-url');
    const formatSelector = document.getElementById('format-selector');
    const downloadBtn = document.getElementById('download-btn');
    const loadingSection = document.getElementById('loading');
    const resultSection = document.getElementById('result');
    const errorSection = document.getElementById('error-message');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoTitle = document.getElementById('video-title');
    const downloadMessage = document.getElementById('download-message');
    const downloadFileBtn = document.getElementById('download-file-btn');
    const newDownloadBtn = document.getElementById('new-download-btn');
    const tryAgainBtn = document.getElementById('try-again-btn');
    const errorText = document.getElementById('error-text');
    const platformBadge = document.getElementById('platform-badge');

    // Variables para almacenar datos de la descarga
    let currentDownloadId = null;
    let currentFilename = null;

    // Función para mostrar/ocultar secciones
    function showSection(section) {
        loadingSection.classList.add('hidden');
        resultSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        
        if (section) {
            section.classList.remove('hidden');
        }
    }

    // Función para establecer el icono de la plataforma
    function setPlatformIcon(platform) {
        let iconClass = 'fab fa-globe'; // Icono por defecto
        
        switch(platform.toLowerCase()) {
            case 'youtube':
                iconClass = 'fab fa-youtube';
                break;
            case 'instagram':
                iconClass = 'fab fa-instagram';
                break;
            case 'facebook':
                iconClass = 'fab fa-facebook';
                break;
            case 'twitter':
                iconClass = 'fab fa-twitter';
                break;
            case 'tiktok':
                iconClass = 'fab fa-tiktok';
                break;
        }
        
        platformBadge.innerHTML = `<i class="${iconClass}"></i>`;
    }

    // Función para iniciar la descarga
    function startDownload() {
        const videoUrl = videoUrlInput.value.trim();
        const format = formatSelector.value;
        
        if (!videoUrl) {
            showError('Por favor, ingresa una URL válida');
            return;
        }
        
        // Mostrar sección de carga
        showSection(loadingSection);
        
        // Enviar solicitud al servidor
        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: videoUrl,
                format: format
            }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Error en la descarga');
                });
            }
            return response.json();
        })
        .then(data => {
            // Guardar información de la descarga
            currentDownloadId = data.download_id;
            currentFilename = data.filename;
            
            // Actualizar la interfaz
            videoThumbnail.src = data.thumbnail || 'https://via.placeholder.com/240x135?text=No+Thumbnail';
            videoTitle.textContent = data.title;
            downloadMessage.textContent = '¡Descarga completada!';
            setPlatformIcon(data.platform);
            
            // Mostrar sección de resultado
            showSection(resultSection);
        })
        .catch(error => {
            showError(error.message);
        });
    }

    // Función para mostrar errores
    function showError(message) {
        errorText.textContent = message;
        showSection(errorSection);
    }

    // Función para descargar el archivo
    function downloadFile() {
        if (currentDownloadId && currentFilename) {
            window.location.href = `/get_file/${currentDownloadId}/${currentFilename}`;
        }
    }

    // Función para reiniciar la interfaz
    function resetInterface() {
        videoUrlInput.value = '';
        showSection(null);
    }

    // Event Listeners
    downloadBtn.addEventListener('click', startDownload);
    downloadFileBtn.addEventListener('click', downloadFile);
    newDownloadBtn.addEventListener('click', resetInterface);
    tryAgainBtn.addEventListener('click', resetInterface);
    
    // Permitir enviar con Enter
    videoUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            startDownload();
        }
    });
});
