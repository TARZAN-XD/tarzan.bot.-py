import os
import yt_dlp

def download_media(url, folder="downloads", audio_only=False):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    ydl_opts = {}
    if audio_only:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # استرجاع اسم الملف
    info_dict = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
    title = info_dict.get('title', 'video')
    ext = 'mp3' if audio_only else 'mp4'
    return f"{folder}/{title}.{ext}"
