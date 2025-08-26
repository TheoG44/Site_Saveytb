import os
import logging
from pytubefix import YouTube
import subprocess

# -----------------------------
# Setup logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------
# Téléchargement et fusion vidéo/audio
# -----------------------------
def main(url, output_folder="VideoFinis"):
    logging.info(f"🌐 Téléchargement de la vidéo : {url}")

    os.makedirs(output_folder, exist_ok=True) # Crée le folder

    yt = YouTube(url) # Crée l'objet YTBS
    logging.info(f"🎬 Titre de la vidéo : {yt.title}")

    # Meilleure vidéo sans audio
    video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", type="video").order_by("resolution").desc().first()
    # Meilleure piste audio
    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()

    logging.info("📥 Téléchargement de la vidéo et de l'audio...")
    video_path = video_stream.download(filename="video.mp4") # type: ignore
    audio_path = audio_stream.download(filename="audio.mp3") # type: ignore

    final_path = os.path.join(output_folder, "VideoFinale.mp4")

    # Fusion audio + vidéo
    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-i", audio_path, "-c", "copy", final_path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) # type: ignore

    # Supprimer les fichiers temporaires
    os.remove(video_path) # type: ignore
    os.remove(audio_path) # type: ignore

    logging.info(f"✅ Vidéo téléchargée : {final_path}")
    return os.path.basename(final_path)  



