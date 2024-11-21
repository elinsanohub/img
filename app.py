import os
import requests
from flask import Flask, send_file, abort

app = Flask(__name__)

# Directorio temporal donde se guardarán las miniaturas e íconos
THUMBNAIL_DIR = '/tmp/thumbnails'
ICON_DIR = '/tmp/icons'
os.makedirs(THUMBNAIL_DIR, exist_ok=True)
os.makedirs(ICON_DIR, exist_ok=True)

@app.route('/vi/<video_id>/mqdefault.jpg', methods=['GET'])
def serve_thumbnail(video_id):
    """
    Sirve la miniatura desde el servidor local. Si no existe, la descarga.
    """
    try:
        if not video_id or len(video_id) != 11:
            abort(400, description="ID de video inválido.")

        thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{video_id}_mqdefault.jpg")

        if not os.path.exists(thumbnail_path):
            youtube_thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
            response = requests.get(youtube_thumbnail_url, stream=True)
            if response.status_code == 200:
                with open(thumbnail_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
            else:
                abort(404, description="Miniatura no encontrada en YouTube.")

        return send_file(thumbnail_path, mimetype='image/jpeg')
    except Exception as e:
        abort(500, description=str(e))

@app.route('/ggpht/<path:icon_id>', methods=['GET'])
def serve_icon(icon_id):
    """
    Sirve los íconos desde el servidor local. Si no existe, lo descarga.
    """
    try:
        # Verificar y adaptar la URL completa del ícono según el formato
        if icon_id.startswith('ytc/'):
            google_icon_url = f"https://yt3.ggpht.com/{icon_id}"
        else:
            google_icon_url = f"https://yt3.ggpht.com/{icon_id}"

        # Reemplazar caracteres conflictivos en el nombre del archivo
        icon_filename = icon_id.replace("/", "_").replace("=", "_")
        icon_path = os.path.join(ICON_DIR, icon_filename)

        if not os.path.exists(icon_path):
            response = requests.get(google_icon_url, stream=True)
            if response.status_code == 200:
                with open(icon_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
            else:
                abort(404, description="Ícono no encontrado en Google.")

        return send_file(icon_path, mimetype='image/jpeg')
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
