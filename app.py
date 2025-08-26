from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from main import main
import os

app = Flask(__name__)

VIDEO_FOLDER = "VideoFinis"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

last_video = None  # garde en mémoire le dernier fichier généré

@app.route("/", methods=["GET", "POST"])
def index():
    global last_video

    # --- Si c'est un GET (refresh ou retour page) ---
    if request.method == "GET":
        # supprime la dernière vidéo si elle existe
        if last_video:
            file_path = os.path.join(VIDEO_FOLDER, last_video)
            if os.path.exists(file_path):
                os.remove(file_path)
            last_video = None
        return render_template("index.html", video_file=None)

    # --- Si c'est un POST (soumission d'URL) ---
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            full_path = main(url)  # ex: "VideoFinis/VideoFinale.mp4"
            last_video = os.path.basename(full_path)  # garde juste le nom
        return render_template("index.html", video_file=last_video)

@app.route("/videos/<filename>")
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)





