import os
import sys
import re
import json
import uuid
import time
import threading
import subprocess
from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
for folder in ['videos', 'audio', 'subtitles']:
    os.makedirs(os.path.join(DOWNLOAD_DIR, folder), exist_ok=True)

download_tasks = {}

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_video_info_yt_dlp(url):
    # Language code to human-readable name mapping (partial, can be extended)
    LANG_MAP = {
        'en': 'English', 'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
        'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean', 'zh-Hans': 'Chinese (Simplified)',
        'zh-Hant': 'Chinese (Traditional)', 'pt': 'Portuguese', 'it': 'Italian', 'ar': 'Arabic',
        'tr': 'Turkish', 'vi': 'Vietnamese', 'id': 'Indonesian', 'th': 'Thai', 'pl': 'Polish',
        'uk': 'Ukrainian', 'ro': 'Romanian', 'nl': 'Dutch', 'sv': 'Swedish', 'fi': 'Finnish',
        'no': 'Norwegian', 'da': 'Danish', 'cs': 'Czech', 'el': 'Greek', 'hu': 'Hungarian',
        'he': 'Hebrew', 'fa': 'Persian', 'bn': 'Bengali', 'ta': 'Tamil', 'te': 'Telugu',
        'ml': 'Malayalam', 'mr': 'Marathi', 'gu': 'Gujarati', 'pa': 'Punjabi', 'ur': 'Urdu',
        'en-US': 'English (US)', 'en-GB': 'English (UK)', 'zh': 'Chinese', 'zh-CN': 'Chinese (China)',
        'zh-TW': 'Chinese (Taiwan)', 'zh-HK': 'Chinese (Hong Kong)',
    }
    try:
        result = subprocess.run([
            sys.executable, '-m', 'yt_dlp', '--dump-json', url
        ], capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        video_streams = []
        audio_streams = []
        for fmt in info.get('formats', []):
            fmt_id = fmt.get('format_id')
            ext = fmt.get('ext')
            filesize = fmt.get('filesize') or fmt.get('filesize_approx')
            filesize_mb = round((filesize or 0) / 1024 / 1024, 2) if filesize else None
            mime_type = fmt.get('mime_type') or ext or 'Unknown'
            width = fmt.get('width')
            height = fmt.get('height')
            resolution = fmt.get('resolution') or (f"{width}x{height}" if width and height else None)
            # Determine stream type
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                stream_type = 'video+audio'
            elif fmt.get('vcodec') != 'none' and fmt.get('acodec') == 'none':
                stream_type = 'video'
            elif fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                stream_type = 'audio'
            else:
                continue  # skip unknown
            stream_obj = {
                'format_id': fmt_id,
                'itag': fmt_id,
                'type': stream_type,
                'ext': ext,
                'mime_type': mime_type,
                'filesize': filesize,
                'size_mb': filesize_mb,
                'format_note': fmt.get('format_note'),
                'fps': fmt.get('fps'),
                'resolution': resolution,
                'abr': fmt.get('abr'),
            }
            if stream_type == 'audio':
                audio_streams.append(stream_obj)
            else:
                video_streams.append(stream_obj)
        # Remove duplicates (same itag)
        seen_itags = set()
        video_streams = [s for s in video_streams if not (s['itag'] in seen_itags or seen_itags.add(s['itag']))]
        audio_streams = [s for s in audio_streams if not (s['itag'] in seen_itags or seen_itags.add(s['itag']))]
        # Sort video+audio streams first, then video-only, then by resolution (descending)
        def res_key(s):
            if s['resolution'] and 'x' in s['resolution']:
                try:
                    return int(s['resolution'].split('x')[1])
                except:
                    return 0
            return 0
        video_streams.sort(key=lambda s: (s['type'] != 'video+audio', -res_key(s)), reverse=False)
        # For audio streams, ensure abr, ext, and size_mb have fallbacks
        for s in audio_streams:
            if not s.get('abr'):
                s['abr'] = 'N/A'
            if not s.get('ext'):
                s['ext'] = 'N/A'
            if s.get('size_mb') is None:
                s['size_mb'] = 'N/A'
        # Subtitles
        captions = []
        subs = info.get('subtitles', {})
        for lang, tracks in subs.items():
            # Try to get human-readable name
            lang_short = lang.split('-')[0]
            name = LANG_MAP.get(lang, LANG_MAP.get(lang_short, lang))
            captions.append({
                'code': lang,
                'name': name,
                'exts': [track.get('ext') for track in tracks]
            })
        return {
            'title': info.get('title'),
            'author': info.get('uploader'),
            'length': info.get('duration'),
            'thumbnail_url': info.get('thumbnail'),
            'views': info.get('view_count'),
            'publish_date': info.get('upload_date'),
            'video_streams': video_streams,
            'audio_streams': audio_streams,
            'captions': captions
        }
    except subprocess.CalledProcessError as e:
        print("yt-dlp error:", e.stderr)
        return {'error': e.stderr.strip() or str(e)}
    except Exception as e:
        print("get_video_info_yt_dlp error:", e)
        return {'error': str(e)}

def run_yt_dlp_download(url, format_id, outdir, outtmpl, extra_args=None):
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '-f', format_id,
        '-o', os.path.join(outdir, outtmpl),
        url
    ]
    if extra_args:
        cmd.extend(extra_args)
    try:
        subprocess.run(cmd, check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.stderr or str(e)

def download_video(url, format_id, task_id):
    try:
        info = get_video_info_yt_dlp(url)
        title = sanitize_filename(info.get('title', 'video'))
        outtmpl = f"{title}_%(resolution)s.%(ext)s"
        outdir = os.path.join(DOWNLOAD_DIR, 'videos')
        download_tasks[task_id]['status'] = 'downloading'
        ok, err = run_yt_dlp_download(url, format_id, outdir, outtmpl)
        if ok:
            download_tasks[task_id]['status'] = 'completed'
            download_tasks[task_id]['filename'] = f"{title}.mp4"
            download_tasks[task_id]['filepath'] = os.path.join('videos', f"{title}.mp4")
        else:
            download_tasks[task_id]['status'] = 'error'
            download_tasks[task_id]['error'] = err
    except Exception as e:
        download_tasks[task_id]['status'] = 'error'
        download_tasks[task_id]['error'] = str(e)

def download_audio(url, format_id, task_id):
    try:
        info = get_video_info_yt_dlp(url)
        title = sanitize_filename(info.get('title', 'audio'))
        outtmpl = f"{title}_audio.%(ext)s"
        outdir = os.path.join(DOWNLOAD_DIR, 'audio')
        download_tasks[task_id]['status'] = 'downloading'
        ok, err = run_yt_dlp_download(url, format_id, outdir, outtmpl, ['--extract-audio', '--audio-format', 'mp3'])
        if ok:
            download_tasks[task_id]['status'] = 'completed'
            download_tasks[task_id]['filename'] = f"{title}_audio.mp3"
            download_tasks[task_id]['filepath'] = os.path.join('audio', f"{title}_audio.mp3")
        else:
            download_tasks[task_id]['status'] = 'error'
            download_tasks[task_id]['error'] = err
    except Exception as e:
        download_tasks[task_id]['status'] = 'error'
        download_tasks[task_id]['error'] = str(e)

def download_subtitle(url, lang_code, task_id):
    try:
        info = get_video_info_yt_dlp(url)
        title = sanitize_filename(info.get('title', 'subtitle'))
        outtmpl = f"{title}_{lang_code}.%(ext)s"
        outdir = os.path.join(DOWNLOAD_DIR, 'subtitles')
        download_tasks[task_id]['status'] = 'downloading'
        ok, err = run_yt_dlp_download(url, 'bestaudio', outdir, outtmpl, [
            '--write-subs', f'--sub-langs={lang_code}', '--skip-download'
        ])
        if ok:
            # Find the downloaded subtitle file
            for ext in ['vtt', 'srt', 'ass']:
                sub_path = os.path.join(outdir, f"{title}_{lang_code}.{ext}")
                if os.path.exists(sub_path):
                    download_tasks[task_id]['status'] = 'completed'
                    download_tasks[task_id]['filename'] = f"{title}_{lang_code}.{ext}"
                    download_tasks[task_id]['filepath'] = os.path.join('subtitles', f"{title}_{lang_code}.{ext}")
                    return
            download_tasks[task_id]['status'] = 'error'
            download_tasks[task_id]['error'] = 'Subtitle file not found.'
        else:
            download_tasks[task_id]['status'] = 'error'
            download_tasks[task_id]['error'] = err
    except Exception as e:
        download_tasks[task_id]['status'] = 'error'
        download_tasks[task_id]['error'] = str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fetch-info', methods=['POST'])
def fetch_info():
    data = request.get_json()
    url = data.get('url', '')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    info = get_video_info_yt_dlp(url)
    if 'error' in info:
        return jsonify(info), 400
    return jsonify(info)

@app.route('/api/download-video', methods=['POST'])
def api_download_video():
    data = request.get_json()
    url = data.get('url', '')
    format_id = data.get('itag') or data.get('format_id')
    if not url or not format_id:
        return jsonify({'error': 'URL and format_id are required'}), 400
    task_id = str(uuid.uuid4())
    download_tasks[task_id] = {
        'type': 'video',
        'status': 'queued',
        'progress': 0
    }
    thread = threading.Thread(target=download_video, args=(url, format_id, task_id))
    thread.daemon = True
    thread.start()
    return jsonify({'task_id': task_id})

@app.route('/api/download-audio', methods=['POST'])
def api_download_audio():
    data = request.get_json()
    url = data.get('url', '')
    format_id = data.get('itag') or data.get('format_id')
    if not url or not format_id:
        return jsonify({'error': 'URL and format_id are required'}), 400
    task_id = str(uuid.uuid4())
    download_tasks[task_id] = {
        'type': 'audio',
        'status': 'queued',
        'progress': 0
    }
    thread = threading.Thread(target=download_audio, args=(url, format_id, task_id))
    thread.daemon = True
    thread.start()
    return jsonify({'task_id': task_id})

@app.route('/api/download-subtitle', methods=['POST'])
def api_download_subtitle():
    data = request.get_json()
    url = data.get('url', '')
    lang_code = data.get('lang_code')
    if not url or not lang_code:
        return jsonify({'error': 'URL and language code are required'}), 400
    task_id = str(uuid.uuid4())
    download_tasks[task_id] = {
        'type': 'subtitle',
        'status': 'queued',
        'progress': 0
    }
    thread = threading.Thread(target=download_subtitle, args=(url, lang_code, task_id))
    thread.daemon = True
    thread.start()
    return jsonify({'task_id': task_id})

@app.route('/api/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    if task_id not in download_tasks:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(download_tasks[task_id])

@app.route('/downloads/<path:filename>', methods=['GET'])
def download_file(filename):
    directory = os.path.dirname(os.path.join(DOWNLOAD_DIR, filename))
    file = os.path.basename(filename)
    return send_from_directory(directory, file, as_attachment=True)

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)