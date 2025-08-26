import os
import logging
from pytubefix import YouTube
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
import shutil
import sys

# ---- Setup Logging ---- #
logging.basicConfig(
    level=logging.INFO,
    filename=".log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'
)

###############################################################
# Télécharge une vidéo à partir d'une url Youtube.            #
# Args:                                                       #
#  None                                                       #
#                                                             #
#                                                             #
###############################################################

def main(url: str): # Prend l'url de la vidéo youtube
    # ---- Paramètres ---- #
    logging.info(f"Téléchargement depuis l'URL : {url}")
    output_folder = "VideoFinis"
    os.makedirs(output_folder, exist_ok=True)

    # ---- Téléchargement en Piste Audio & Vidéo ---- #
    logging.info("⌛ Démarrage du téléchargement...")
    yt = YouTube(url)

    # Meilleure vidéo (adaptive, sans audio)
    video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", type="video").order_by("resolution").desc().first()
    video_path = video_stream.download(filename="video.mp4")  # type: ignore
    logging.info(f"✅ Vidéo téléchargée en {video_stream.resolution}")  # type: ignore

    # Meilleure piste audio
    logging.info("⌛ Découpage de la vidéo lancé...")
    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
    audio_path = audio_stream.download(filename="audio.mp3")  # type: ignore
    logging.info("✅ Audio téléchargé")

    # ---- Fusion des Pistes Audio & Vidéo ---- #
    logging.info("⌛ Assemblage des segments lancé...")
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    final_clip = video_clip.with_audio(audio_clip)

    final_path = os.path.join(output_folder, "VideoFinale1080p.mp4")
    final_clip.write_videofile(final_path, codec="libx264", audio_codec="aac")
    logging.info(f"✅ Vidéo finale sauvegardée dans : {final_path}")

    # ---- Nettoyage fichiers temporaires ---- #
    video_clip.close()
    audio_clip.close()
    final_clip.close()
    os.remove(video_path) # type: ignore
    os.remove(audio_path) # type: ignore
    logging.info("✅ Fusion terminée et fichiers temporaires supprimés")

    # ---- Étape 2 : Découper la vidéo ---- #
    decouper_video(final_path, os.path.join(output_folder, "segments"))

    # ---- Étape 3 : Assembler les segments ---- #
    assembler_videos(
        os.path.join(output_folder, "segments"),
        os.path.join(output_folder, "segments"),
        os.path.join(output_folder, "VideoMonte")
    )
    
    # Récupérer tous les segments montés
    output_folder = os.path.join(output_folder, "VideoMonte")
    all_videos = sorted([
      os.path.join(output_folder, f)
    for f in os.listdir(output_folder)
    if f.endswith(".mp4")
    ])
    return all_videos  # renvoie une liste de chemins


#################################################################################
# Découpe une vidéo en segments de durée fixe.                                  #
# Args:                                                                         #
#  input_path (str): Chemin vers la vidéo d'entrée.                             #
#  output_folder (str): Dossier où sauvegarder les segments.                    #
#  segment_length (int): Longueur de chaque segment en secondes (par défaut 60) #
#################################################################################

def decouper_video(input_path: str, output_folder: str, segment_length: int = 60):

    os.makedirs(output_folder, exist_ok=True)

    # On récupère la durée totale de la vidéo
    with VideoFileClip(input_path) as video:
        duration = int(video.duration)

    # Boucle pour découper la vidéo en morceaux
    for i, start in enumerate(range(0, duration, segment_length)):
        end = min(start + segment_length, duration)

        # Recharge la vidéo à chaque itération pour éviter bugs de MoviePy
        with VideoFileClip(input_path) as video:
            segment = video.subclipped(start, end)
            segment_filename = os.path.join(output_folder, f"segment_{i+1:03d}.mp4")
            logging.info(f"⌛ Découpage de {input_path} en segments de {segment_length}s...")
            segment.write_videofile(
                segment_filename,
                codec="libx264",
                audio_codec="aac",
                threads=4
            )
            logging.info(f"✅ Segment {i+1} sauvegardé : {segment_filename}")
            segment.close()
    
    logging.info(f"✅ Découpage terminé. {i+1} segments créés dans {output_folder}")
    
    
#################################################################################
# Assemble les vidéos de deux dossiers en une seule vidéo.                      #
# Args:                                                                         #
#  folder_path1 (str): Chemin du premier dossier contenant les vidéos.          #
#  folder_path2 (str): Chemin du deuxième dossier contenant les vidéos.         #
#  output_folder (str): Dossier où sauvegarder les vidéos assemblées.           #
#################################################################################
    
def assembler_videos(folder_path1: str, folder_path2: str, output_folder: str):

    os.makedirs(output_folder, exist_ok=True)

    # Vérifier si les dossiers existent
    if not os.path.exists(folder_path1):
        logging.error(f"❌ Le dossier {folder_path1} n'existe pas.")
        raise FileNotFoundError(f"Le dossier {folder_path1} n'existe pas.")
    if not os.path.exists(folder_path2):
        logging.error(f"❌ Le dossier {folder_path2} n'existe pas.")
        raise FileNotFoundError(f"Le dossier {folder_path2} n'existe pas.")

    # Récupérer les fichiers vidéos
    videos1 = sorted([os.path.join(folder_path1, f) for f in os.listdir(folder_path1) if f.endswith(('.mp4', '.mov', '.avi'))])
    videos2 = sorted([os.path.join(folder_path2, f) for f in os.listdir(folder_path2) if f.endswith(('.mp4', '.mov', '.avi'))])
    logging.info(f"{len(videos1)} vidéos trouvées dans {folder_path1}")
    logging.info(f"{len(videos2)} vidéos trouvées dans {folder_path2}")

    for i in range(len(videos1)):
        # Charger les vidéos
        clip1 = VideoFileClip(videos1[i])
        clip2 = VideoFileClip(videos2[i])

        # Redimensionner à la même largeur
        width = max(clip1.w, clip2.w)
        clip1 = clip1.resized(width=width)
        clip2 = clip2.resized(width=width)

        # Déterminer la hauteur totale
        height = clip1.h + clip2.h # type: ignore

        # Créer une vidéo composite
        final_clip = CompositeVideoClip([
            clip1.with_position(("center", "top")), # type: ignore
            clip2.with_position(("center", "bottom")) # type: ignore
        ], size=(width, height))

        # Sauvegarder la vidéo assemblée
        output_path = os.path.join(output_folder, f'AutoTok_video_0{i+1}.mp4')
        final_clip.write_videofile(output_path, codec='libx264')

        # Libérer mémoire
        clip1.close()
        clip2.close()
        final_clip.close()
    
    logging.info("✅ Les vidéos ont été assemblées avec succès.")
    
    # ---- Nettoyage des fichiers intermédiaires ---- #
    try:
        # Supprimer le fichier vidéo finale avant découpage
        video_finale = os.path.join("VideoFinis", "VideoFinale1080p.mp4")
        if os.path.exists(video_finale):
            os.remove(video_finale)
            logging.info("✅ Suppression de VideoFinale1080p.mp4")


        # Supprimer tout le dossier segments
        if os.path.exists(folder_path1):
            shutil.rmtree(folder_path1)
            logging.info(f"✅ Suppression du dossier {folder_path1}")


    except Exception:
        logging.exception(f"❌ Erreur lors du nettoyage") 
    
