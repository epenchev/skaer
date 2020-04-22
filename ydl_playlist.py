import os
import json
import youtube_dl
import time


def download(v):
    """
    Download youtube video.
    :param v: id of the video to download.

    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True,
        'source_address': '0.0.0.0',
        'user_agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'format': 'bestaudio/best',
        'extractaudio' : True,
        'audioformat' : 'mp3'
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([v])
    except youtube_dl.utils.ExtractorError as err:
        print(err)
    except youtube_dl.utils.DownloadError as err:
        print(err)
 

def playlist_items(lid):
    with youtube_dl.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
        json_out = ydl.extract_info(lid, download=False)
    for count, entry  in enumerate(json_out['entries']):
        print(entry['id'], entry['title'])
        download(entry['id'])
        if count and count % 10 == 0:
            print('wait a bit')
            time.sleep(10)


if __name__ == '__main__':
    playlist_items('PLVsbpXIf2w4k0yf-iMcvsDDkQ3830k0hl')

