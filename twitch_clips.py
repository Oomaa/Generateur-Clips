import requests
import moviepy as mp
import os

# Configuration de l'API
CLIENT_ID = "4lw8awe386w7lhqc7p9qt34nm14sj1"
CLIENT_SECRET = "a3l1uk0p024bjyew6kdytt6hwn87d0"
BASE_URL = "https://api.twitch.tv/helix/"

def get_access_token():
    """
    Obtenir un jeton d'accès pour l'API Twitch.
    """
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]

def get_streamer_id(username, access_token):
    """
    Obtenir l'ID Twitch d'un streamer à partir de son nom d'utilisateur.
    """
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }
    params = {"login": username}
    response = requests.get(BASE_URL + "users", headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    if data["data"]:
        return data["data"][0]["id"]
    else:
        raise ValueError(f"Utilisateur Twitch '{username}' introuvable.")

def get_clips(broadcaster_id, access_token, limit=5):
    """
    Récupérer les clips populaires d'un streamer.
    """
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "first": limit
    }
    response = requests.get(BASE_URL + "clips", headers=headers, params=params)
    response.raise_for_status()
    return response.json()["data"]

def download_clip(clip_url, output_dir="clips"):
    """
    Télécharger un clip à partir de son URL.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    clip_name = clip_url.split("/")[-1].split("?")[0] + ".mp4"
    file_path = os.path.join(output_dir, clip_name)
    
    response = requests.get(clip_url)
    with open(file_path, "wb") as f:
        f.write(response.content)
    
    return file_path

def create_highlight(clips, output_file="highlight.mp4"):
    """
    Créer un highlight vidéo à partir des clips.
    """
    clips_videos = [mp.VideoFileClip(clip) for clip in clips]
    final_video = mp.concatenate_videoclips(clips_videos)
    final_video.write_videofile(output_file, codec="libx264")
    print(f"Highlight créé : {output_file}")

if __name__ == "__main__":
    streamer_username = input("Nom d'utilisateur Twitch du streamer : ")
    access_token = get_access_token()

    try:
        # Étape 1 : Obtenir l'ID du streamer
        broadcaster_id = get_streamer_id(streamer_username, access_token)

        # Étape 2 : Récupérer les clips
        clips_data = get_clips(broadcaster_id, access_token)
        clips_files = []
        
        for clip in clips_data:
            clip_url = clip["thumbnail_url"].split("-preview")[0] + ".mp4"
            clip_path = download_clip(clip_url)
            clips_files.append(clip_path)
        
        # Étape 3 : Créer le highlight
        create_highlight(clips_files)

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")