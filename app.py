from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from main import main
import os

app = Flask(__name__)

VIDEO_FOLDER = "VideoFinis"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

last_video = None
video_displayed = False  # 👈 nouvelle variable

@app.route("/", methods=["GET", "POST"])
def index():
    global last_video, video_displayed

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            full_path = main(url)  # Télécharge la vidéo
            last_video = os.path.basename(full_path)
            video_displayed = False
        return redirect(url_for("index"))

    # --- GET ---
    if last_video:
        if not video_displayed:
            # Première fois qu'on affiche la vidéo → on montre le lien
            video_displayed = True
            return render_template("index.html", video_file=last_video)
        else:
            # Deuxième refresh → on supprime la vidéo
            path = os.path.join(VIDEO_FOLDER, last_video)
            if os.path.exists(path):
                os.remove(path)
            last_video = None
            video_displayed = False

    return render_template("index.html", video_file=None)

@app.route("/videos/<filename>")
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)





