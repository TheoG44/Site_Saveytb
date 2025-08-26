from flask import Flask, render_template, request, send_from_directory
from main import main
import os

#=====================================#
#                                     #
#         FRAMEWORKS : Flask          #
#                                     #
#=====================================#

app = Flask(__name__)

VIDEO_FOLDER = "VideoFinis"  # dossier vidéos sont enregistrées
os.makedirs(VIDEO_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    video_file = None
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            video_file = main(url)  
    return render_template("index.html", video_file=video_file)

# Route pour servir les vidéos
@app.route("/videos/<filename>")
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)





