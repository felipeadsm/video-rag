import uuid
import yt_dlp
import re

def extract_video_id(url: str) -> str | None:
    """
    Extrai o ID do vídeo do YouTube a partir da URL usando regex.
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|&|\/|$)", url)
    if match:
        return match.group(1)
    return None

def download_audio(url: str) -> tuple[str, str]:
    """
    Downloads the audio from a YouTube video using yt-dlp.
    Returns a tuple: (path_to_audio_file, video_id)
    """
    # Recupera metadados do vídeo primeiro para pegar o ID
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_id = info_dict.get("id", str(uuid.uuid4()))
    
    output_path = f"/tmp/{video_id}.wav"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': f'/tmp/{video_id}.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
    return output_path, video_id
