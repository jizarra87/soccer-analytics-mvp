import yt_dlp

url = "https://www.youtube.com/watch?v=x779K0Pjtv4"

ydl_opts = {
    'outtmpl': 'videos/%(title)s.%(ext)s',
    'format': 'best[ext=mp4]'
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])