from flask import Flask, render_template, request
import yt_dlp
from datetime import datetime, timedelta

app = Flask(__name__)

def get_video_info(video_url):
    ydl_opts = {}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        
        # Basic info
        video_info = {
            "title": info.get('title', 'Title not available'),
            "channel": info.get('channel', 'Channel not available'),
            "channel_url": info.get('channel_url', '#'),
            "video_url": info.get('webpage_url', '#'),
            "thumbnail": info.get('thumbnail', ''),
            "views": f"{info.get('view_count', 0):,}",
            "likes": f"{info.get('like_count', 0):,}" if info.get('like_count') is not None else 'Not available',
            "description": info.get('description', 'Description not available'),
        }

        # Upload time
        upload_time = datetime.utcfromtimestamp(info.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
        video_info["upload_time"] = upload_time

        # Video length
        duration_seconds = info.get('duration', 0)
        length = str(timedelta(seconds=duration_seconds))
        video_info["length"] = length

        # Available resolutions
        formats = info.get('formats', [])
        resolutions = set()
        for f in formats:
            if f.get('height'):
                resolutions.add(f"{f['height']}p")
        resolutions = sorted(resolutions, key=lambda x: int(x[:-1]), reverse=True)
        video_info["resolutions"] = ', '.join(resolutions)

        # Additional details
        video_info["age_limit"] = info.get('age_limit', 'Not specified')
        video_info["category"] = info.get('category', 'Not specified')
        video_info["tags"] = ', '.join(info.get('tags', ['None']))
        video_info["subtitles"] = ', '.join(info.get('subtitles', {}).keys()) or 'None'

        # Audio details
        audio_streams = [f for f in formats if f.get('acodec') != 'none']
        if audio_streams:
            best_audio = max(audio_streams, key=lambda x: x.get('abr') or 0)
            video_info["best_audio_bitrate"] = f"{best_audio.get('abr', 'Unknown')} kbps"
            video_info["audio_codec"] = best_audio.get('acodec', 'Unknown')
        else:
            video_info["best_audio_bitrate"] = "No audio stream information available"
            video_info["audio_codec"] = "Unknown"

        # Video details
        video_streams = [f for f in formats if f.get('vcodec') != 'none']
        if video_streams:
            best_video = max(video_streams, key=lambda x: x.get('height') or 0)
            video_info["best_video_resolution"] = f"{best_video.get('height', 'Unknown')}p"
            video_info["video_codec"] = best_video.get('vcodec', 'Unknown')
        else:
            video_info["best_video_resolution"] = "No video stream information available"
            video_info["video_codec"] = "Unknown"
        

        return video_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_info', methods=['POST'])
def fetch_info():
    youtube_url = request.form['youtube_url']
    info = get_video_info(youtube_url)
    return render_template('video_info.html', info=info)

if __name__ == '__main__':
    app.run(debug=True)
