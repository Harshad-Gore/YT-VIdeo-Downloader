/**
 * Darkrai Downloader - Main Application JavaScript
 */

// Define the main Alpine.js component
function ytDownloader() {
    return {
        // State variables
        url: '',
        loading: false,
        error: null,
        videoInfo: null,
        activeTab: 'video',
        theme: localStorage.getItem('theme') || 'dark',
        
        // Download status tracking
        downloadingVideo: false,
        downloadingAudio: false,
        downloadingSubtitle: false,
        currentDownloadItag: null,
        currentSubtitleCode: null,
        downloadProgress: 0,
        completedDownloads: [],
        
        // Toast notification system
        toasts: [],
        toastTimeout: 5000, // 5 seconds

        // Initialize the application
        init() {
            this.applyTheme();
            
            // Check if there's a URL in the query params
            const urlParams = new URLSearchParams(window.location.search);
            const urlFromParam = urlParams.get('url');
            if (urlFromParam) {
                this.url = urlFromParam;
                this.fetchVideoInfo();
            }
        },
        
        // Toggle between light and dark theme
        toggleTheme() {
            this.theme = this.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', this.theme);
            this.applyTheme();
        },
        
        // Apply the current theme to the document
        applyTheme() {
            if (this.theme === 'light') {
                document.body.classList.remove('from-darkrai-dark', 'to-darkrai-primary', 'text-darkrai-light');
                document.body.classList.add('from-slate-100', 'to-slate-200', 'text-darkrai-dark');
            } else {
                document.body.classList.remove('from-slate-100', 'to-slate-200', 'text-darkrai-dark');
                document.body.classList.add('from-darkrai-dark', 'to-darkrai-primary', 'text-darkrai-light');
            }
        },
        
        // Fetch video information from YouTube URL
        fetchVideoInfo() {
            if (!this.url) {
                this.showToast('Please enter a YouTube URL', 'error');
                return;
            }
            
            // Validate URL format
            if (!this.isValidYoutubeUrl(this.url)) {
                this.showToast('Please enter a valid YouTube URL', 'error');
                return;
            }
            
            this.loading = true;
            this.error = null;
            
            fetch('/api/fetch-info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: this.url }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to fetch video information');
                    });
                }
                return response.json();
            })
            .then(data => {
                this.videoInfo = data;
                this.loading = false;
                this.showToast('Video information fetched successfully', 'success');
            })
            .catch(error => {
                this.loading = false;
                this.error = error.message;
                this.showToast(error.message, 'error');
            });
        },
        
        // Download video with specified itag
        downloadVideo(itag) {
            if (this.downloadingVideo) return;
            
            this.downloadingVideo = true;
            this.currentDownloadItag = itag;
            this.downloadProgress = 0;
            
            fetch('/api/download-video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: this.url, itag: itag }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to start video download');
                    });
                }
                return response.json();
            })
            .then(data => {
                this.showToast('Darkrai has started capturing your video', 'info');
                this.pollDownloadStatus(data.task_id);
            })
            .catch(error => {
                this.downloadingVideo = false;
                this.showToast(error.message, 'error');
            });
        },
        
        // Download audio with specified itag
        downloadAudio(itag) {
            if (this.downloadingAudio) return;
            
            this.downloadingAudio = true;
            this.currentDownloadItag = itag;
            this.downloadProgress = 0;
            
            fetch('/api/download-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: this.url, itag: itag }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to start audio download');
                    });
                }
                return response.json();
            })
            .then(data => {
                this.showToast('Darkrai is now extracting the audio', 'info');
                this.pollDownloadStatus(data.task_id);
            })
            .catch(error => {
                this.downloadingAudio = false;
                this.showToast(error.message, 'error');
            });
        },
        
        // Download subtitle with specified language code
        downloadSubtitle(langCode) {
            if (this.downloadingSubtitle) return;
            
            this.downloadingSubtitle = true;
            this.currentSubtitleCode = langCode;
            
            fetch('/api/download-subtitle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: this.url, lang_code: langCode }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Failed to start subtitle download');
                    });
                }
                return response.json();
            })
            .then(data => {
                this.showToast('Darkrai is translating your subtitles', 'info');
                this.pollDownloadStatus(data.task_id);
            })
            .catch(error => {
                this.downloadingSubtitle = false;
                this.showToast(error.message, 'error');
            });
        },
        
        // Poll for download status updates
        pollDownloadStatus(taskId) {
            const checkStatus = () => {
                fetch(`/api/task-status/${taskId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Update progress (simulate progress if always 0)
                        if (data.status === 'downloading') {
                            if (data.progress && data.progress > 0) {
                                this.downloadProgress = data.progress;
                            } else {
                                // Simulate progress bar animation if backend progress is always 0
                                if (this.downloadProgress < 95) {
                                    this.downloadProgress += Math.floor(Math.random() * 5) + 1;
                                } else {
                                    this.downloadProgress = 95;
                                }
                            }
                        }
                        if (data.status === 'completed') {
                            this.downloadProgress = 100;
                            // Download completed successfully
                            this.showToast(`Darkrai has successfully delivered your ${data.type}!`, 'success');
                            
                            // Reset download status
                            if (data.type === 'video') this.downloadingVideo = false;
                            if (data.type === 'audio') this.downloadingAudio = false;
                            if (data.type === 'subtitle') this.downloadingSubtitle = false;
                            
                            // Add to completed downloads
                            this.completedDownloads.push(data);
                            
                        } else if (data.status === 'error') {
                            this.downloadProgress = 0;
                            // Download failed
                            this.showToast(`${this.capitalizeFirstLetter(data.type)} download failed: ${data.error}`, 'error');
                            
                            // Reset download status
                            if (data.type === 'video') this.downloadingVideo = false;
                            if (data.type === 'audio') this.downloadingAudio = false;
                            if (data.type === 'subtitle') this.downloadingSubtitle = false;
                            
                        } else {
                            // Download still in progress, poll again
                            setTimeout(checkStatus, 1000);
                        }
                    })
                    .catch(error => {
                        console.error('Error checking download status:', error);
                        
                        // Reset download status on error
                        this.downloadingVideo = false;
                        this.downloadingAudio = false;
                        this.downloadingSubtitle = false;
                        
                        this.showToast('Error checking download status', 'error');
                    });
            };
            
            // Start polling
            checkStatus();
        },
        
        // Show toast notification with Darkrai theme
        showToast(message, type = 'info') {
            const id = Date.now();
            const toast = {
                id,
                message,
                type,
                visible: true
            };
            
            this.toasts.push(toast);
            
            // Auto-hide toast after timeout
            setTimeout(() => {
                this.removeToast(this.toasts.findIndex(t => t.id === id));
            }, this.toastTimeout);
        },
        
        // Remove toast by index
        removeToast(index) {
            if (index > -1) {
                const toast = this.toasts[index];
                if (toast) {
                    toast.visible = false;
                    setTimeout(() => {
                        this.toasts.splice(index, 1);
                    }, 300); // Allow transition to complete
                }
            }
        },
        
        // Format number with commas (e.g., 1,000,000)
        formatNumber(number) {
            if (!number) return '0';
            return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        },
        
        // Format video duration from seconds to HH:MM:SS
        formatDuration(seconds) {
            if (!seconds) return '00:00';
            
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            
            let result = '';
            
            if (hours > 0) {
                result += `${hours}:${minutes.toString().padStart(2, '0')}:`;
            } else {
                result += `${minutes}:`;
            }
            
            result += secs.toString().padStart(2, '0');
            
            return result;
        },
        
        // Format date string to readable format
        formatDate(dateStr) {
            if (!dateStr) return 'Unknown date';
            
            try {
                const date = new Date(dateStr);
                return date.toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            } catch (e) {
                return 'Unknown date';
            }
        },
        
        // Capitalize first letter of string
        capitalizeFirstLetter(string) {
            if (!string) return '';
            return string.charAt(0).toUpperCase() + string.slice(1);
        },
        
        // Validate YouTube URL
        isValidYoutubeUrl(url) {
            const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
            return youtubeRegex.test(url);
        }
    };
}