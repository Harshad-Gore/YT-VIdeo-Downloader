# 🎬 YouTube Video Downloader

A modern, feature-rich YouTube video downloader web application built with Flask and yt-dlp. Download videos, audio, and subtitles with a beautiful dark-themed interface.

![Darkrai Downloader](https://img.shields.io/badge/Platform-Web-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![Flask](https://img.shields.io/badge/Flask-2.0+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🎥 Video Downloads
- **Multiple Quality Options**: Download videos in various resolutions (144p to 4K+)
- **Format Selection**: Choose from different video formats (MP4, WebM, etc.)
- **Combined & Separate Streams**: Options for video+audio combined or video-only streams
- **File Size Information**: Preview file sizes before downloading

### 🎵 Audio Downloads
- **High-Quality Audio**: Extract audio in MP3 format
- **Various Bitrates**: Multiple audio quality options
- **Audio-Only Downloads**: Direct audio extraction without video processing

### 📝 Subtitle Downloads
- **Multi-Language Support**: Download subtitles in 40+ languages
- **Format Options**: VTT, SRT, and ASS subtitle formats
- **Auto-Generated & Manual**: Both auto-generated and manually created subtitles

### 🎨 User Interface
- **Modern Dark Theme**: Beautiful dark interface with Darkrai-inspired colors
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Real-Time Progress**: Live download status and progress tracking
- **Toast Notifications**: User-friendly success/error messages
- **Tabbed Interface**: Organized tabs for Videos, Audio, and Subtitles

### 🔧 Technical Features
- **Async Downloads**: Background processing with threading
- **Progress Tracking**: Real-time download status monitoring
- **Error Handling**: Comprehensive error reporting and recovery
- **File Management**: Organized downloads in separate folders
- **API Endpoints**: RESTful API for programmatic access

## 🚀 Quick Start

### Prerequisites

Before running the application, ensure you have:

- **Python 3.7 or higher**
- **pip** (Python package installer)
- **yt-dlp** (YouTube downloader)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Harshad-Gore/darkrai-youtube-downloader.git
   cd darkrai-youtube-downloader
   ```

2. **Install all dependencies** (Recommended - One Command Install)
   ```bash
   pip install -r requirements.txt
   ```
   
   **OR Install manually** (if you prefer individual packages)
   ```bash
   pip install Flask>=2.3.0 Flask-CORS>=4.0.0 yt-dlp>=2024.7.1
   ```

3. **Verify installation**
   ```bash
   python -m yt_dlp --version
   ```

### Running the Application

1. **Start the Flask server**
   ```bash
   python Download.py
   ```

2. **Open your browser**
   Navigate to: `http://localhost:5000`

3. **Start downloading!**
   - Paste a YouTube URL
   - Click "Fetch Info"
   - Choose your preferred format
   - Click "Download"

## 📋 Requirements

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher (recommended)
- **Memory**: Minimum 1GB RAM
- **Storage**: At least 2GB free space for downloads and dependencies

### Python Dependencies

**Core Application Packages:**
```txt
Flask>=2.3.0                # Web framework
Flask-CORS>=4.0.0           # Cross-origin request handling
yt-dlp>=2024.7.1            # YouTube downloader
```

**Complete Dependencies List:**
All required packages are listed in `requirements.txt`. Install with:
```bash
pip install -r requirements.txt
```

**Key Dependencies Include:**
- **Flask Framework**: Werkzeug, Jinja2, click, MarkupSafe, itsdangerous, blinker
- **HTTP Libraries**: requests, certifi, urllib3, charset-normalizer, idna
- **yt-dlp Dependencies**: rich, pycryptodome, mutagen, websockets
- **Additional**: Pillow (image processing)

**Fresh Python Installation:**
If you have a brand new Python installation, the `requirements.txt` file includes all necessary packages and their dependencies to get you up and running immediately.

### Optional Dependencies
- **FFmpeg**: For advanced video/audio processing and format conversion (highly recommended)
  ```bash
  # Windows (via chocolatey)
  choco install ffmpeg
  
  # macOS (via homebrew)
  brew install ffmpeg
  
  # Ubuntu/Debian
  sudo apt install ffmpeg
  ```

## 🗂️ Project Structure

```
YT Video Downloader/
├── Download.py              # Main Flask application
├── README.md               # Project documentation
├── LICENSE                 # MIT License file
├── requirements.txt        # Python dependencies
├── downloads/              # Downloaded files storage
│   ├── videos/            # Video downloads
│   ├── audio/             # Audio downloads
│   └── subtitles/         # Subtitle downloads
├── static/                # Static web assets
│   ├── css/
│   │   └── styles.css     # Custom CSS styles
│   ├── img/               # Images and icons
│   └── js/
│       └── app.js         # Frontend JavaScript
└── templates/             # HTML templates
    └── index.html         # Main page template
```

## 🛠️ Usage Guide

### Basic Usage

1. **Enter YouTube URL**
   - Paste any YouTube video URL in the input field
   - Supports various YouTube URL formats

2. **Fetch Video Information**
   - Click "Fetch Info" to retrieve video details
   - View available formats, resolutions, and file sizes

3. **Choose Download Type**
   - **Video Tab**: Download video files with/without audio
   - **Audio Tab**: Extract audio only (MP3 format)
   - **Subtitles Tab**: Download subtitle files

4. **Select Format & Download**
   - Choose your preferred quality/format
   - Click the download button
   - Monitor progress in real-time

### Advanced Features

#### API Usage
The application provides REST API endpoints for programmatic access:

- `POST /api/fetch-info` - Get video information
- `POST /api/download-video` - Start video download
- `POST /api/download-audio` - Start audio download
- `POST /api/download-subtitle` - Start subtitle download
- `GET /api/task-status/<task_id>` - Check download status

#### Direct File Access
Downloaded files are accessible via:
- Videos: `http://localhost:5000/downloads/videos/filename.mp4`
- Audio: `http://localhost:5000/downloads/audio/filename.mp3`
- Subtitles: `http://localhost:5000/downloads/subtitles/filename.vtt`

## ⚙️ Configuration

### Environment Variables
You can customize the application behavior:

```bash
# Set custom download directory
export DOWNLOAD_DIR="/path/to/downloads"

# Set Flask debug mode
export FLASK_DEBUG=1

# Set custom port
export FLASK_PORT=8080
```

### Custom Styling
Modify `static/css/styles.css` to customize the appearance or update the Tailwind configuration in `templates/index.html`.

## 📱 Supported Platforms

### Video Platforms
- **YouTube**: Full support for all video types
- **YouTube Music**: Audio downloads
- **YouTube Shorts**: Short-form videos
- **YouTube Live**: Live stream recordings

### Video Formats
- **MP4**: Most common format (recommended)
- **WebM**: Google's open format
- **MKV**: High-quality container
- **FLV**: Legacy Flash format

### Audio Formats
- **MP3**: Default audio format
- **M4A**: High-quality audio
- **OGG**: Open-source format
- **WAV**: Uncompressed audio

### Subtitle Formats
- **VTT**: WebVTT format
- **SRT**: SubRip format
- **ASS**: Advanced SubStation format

## 🔍 Troubleshooting

### Common Issues

1. **"yt-dlp not found" error**
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **Download fails with format error**
   - Try a different video format
   - Check if the video is available in your region

3. **Slow downloads**
   - Check your internet connection
   - Try downloading during off-peak hours

4. **Permission errors**
   - Ensure write permissions to the downloads folder
   - Run with administrator privileges if necessary

### Debug Mode
Enable debug mode for detailed error information:
```bash
python Download.py --debug
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
python -m black .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Notice

This tool is for educational and personal use only. Please respect YouTube's Terms of Service and copyright laws. Users are responsible for ensuring they have the right to download and use the content.

## 🙏 Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - Powerful YouTube downloader
- **[Flask](https://flask.palletsprojects.com/)** - Lightweight web framework
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Alpine.js](https://alpinejs.dev/)** - Minimal JavaScript framework

## 📞 Support

If you encounter any issues or have questions:

1. **Check the troubleshooting section**
2. **Search existing issues** on GitHub
3. **Create a new issue** with detailed information
4. **Join our community** for discussions

---

**Made with ❤️**

*Happy downloading! 🎉*
