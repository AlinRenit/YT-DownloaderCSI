import sys
import os
import zipfile
import shutil
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLineEdit, QPushButton, QProgressBar,
                            QLabel, QFileDialog, QMessageBox, QComboBox,
                            QGridLayout, QFrame, QScrollArea, QTableWidget,
                            QTableWidgetItem, QHeaderView, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon, QLinearGradient, QPainter, QBrush
import yt_dlp
import requests
from io import BytesIO

def get_ffmpeg_path():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(app_dir, 'ffmpeg')
    ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    
    # If ffmpeg exists in the application directory, use it
    if os.path.exists(ffmpeg_exe):
        return ffmpeg_exe
    
    # If ffmpeg doesn't exist, print a message
    print("ffmpeg not found in the application directory.")
    print("Please place ffmpeg.exe in a folder named 'ffmpeg' in the same directory as this script.")
    return None

# Get ffmpeg path before initializing the application
FFMPEG_PATH = get_ffmpeg_path()

# CSI VIT Color Scheme
NAVY_BLUE = "#1A1B35"  # Deep navy background
DARKER_NAVY = "#12132A"  # Even darker background
CARD_BG = "#1E2144"  # Slightly lighter than navy for cards
BORDER_BLUE = "#2A3C77"  # Border color
ACCENT_BLUE = "#3B5998"  # Interactive elements
TEXT_COLOR = "#E6E6E6"  # Slightly off-white for better readability
MUTED_TEXT = "#A0A0A0"  # For secondary information
FLAG_ORANGE = "#FF9933"
FLAG_GREEN = "#138808"

# Modern styling with CSI VIT branding
STYLE_SHEET = f"""
QMainWindow {{
    background-color: {DARKER_NAVY};
}}

QWidget#centralWidget {{
    background-color: {DARKER_NAVY};
}}

.CardFrame {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER_BLUE};
    border-radius: 10px;
    padding: 15px;
}}

QLabel {{
    color: {TEXT_COLOR};
    font-size: 12px;
    padding: 1px;
}}

QLabel[heading="true"] {{
    color: {TEXT_COLOR};
    font-size: 20px;
    font-weight: bold;
    padding: 3px;
}}

QLabel[subheading="true"] {{
    color: {MUTED_TEXT};
    font-size: 14px;
    padding: 2px;
}}

QLabel[info="true"] {{
    color: {MUTED_TEXT};
    font-size: 12px;
    padding: 2px;
}}

QLineEdit {{
    background-color: {NAVY_BLUE};
    border: 1px solid {BORDER_BLUE};
    border-radius: 4px;
    padding: 8px;
    color: {TEXT_COLOR};
    font-size: 12px;
    selection-background-color: {ACCENT_BLUE};
}}

QLineEdit:focus {{
    border: 2px solid {ACCENT_BLUE};
}}

QPushButton {{
    background-color: {ACCENT_BLUE};
    color: {TEXT_COLOR};
    border: none;
    border-radius: 4px;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {BORDER_BLUE};
}}

QPushButton[secondary="true"] {{
    background-color: transparent;
    border: 1px solid {BORDER_BLUE};
}}

QPushButton[secondary="true"]:hover {{
    background-color: rgba(58, 89, 152, 0.1);
}}

QPushButton[download="true"] {{
    background-color: {FLAG_GREEN};
    color: {TEXT_COLOR};
    border: none;
    border-radius: 4px;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: bold;
    margin: 5px;
    min-width: 100px;
}}

QPushButton[download="true"]:hover {{
    background-color: #1EA51E;
}}

QProgressBar {{
    background-color: {NAVY_BLUE};
    border: 1px solid {BORDER_BLUE};
    border-radius: 5px;
    text-align: center;
    color: {TEXT_COLOR};
}}

QProgressBar::chunk {{
    background-color: {ACCENT_BLUE};
    border-radius: 4px;
}}

QTableWidget {{
    background-color: {NAVY_BLUE};
    border: 1px solid {BORDER_BLUE};
    border-radius: 4px;
    gridline-color: {BORDER_BLUE};
    color: {TEXT_COLOR};
    font-size: 12px;
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {BORDER_BLUE};
}}

QTableWidget::item:selected {{
    background-color: {ACCENT_BLUE};
}}

QHeaderView::section {{
    background-color: {CARD_BG};
    color: {TEXT_COLOR};
    padding: 10px;
    border: none;
    border-bottom: 2px solid {BORDER_BLUE};
    font-weight: bold;
    font-size: 12px;
}}

QScrollBar:vertical {{
    background-color: {NAVY_BLUE};
    width: 10px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {BORDER_BLUE};
    border-radius: 5px;
    min-height: 20px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

class VideoInfo:
    def __init__(self):
        self.title = ""
        self.duration = ""
        self.thumbnail_url = ""
        self.formats = []
        self.thumbnail = None
        self.channel = ""
        self.views = ""
        self.upload_date = ""
        self.available_formats = []

class DownloadWorker(QThread):
    progress = Signal(float)
    finished = Signal()
    error = Signal(str)
    info_ready = Signal(VideoInfo)
    
    def __init__(self, url, save_path, format_id='best'):
        super().__init__()
        # Convert short URLs to full URLs
        if 'youtu.be' in url:
            video_id = url.split('/')[-1].split('?')[0]
            self.url = f'https://www.youtube.com/watch?v={video_id}'
        else:
            self.url = url
        self.save_path = save_path
        self.format_id = format_id
        self.is_downloading = False
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                if 'total_bytes' in d:
                    total = d['total_bytes']
                    downloaded = d['downloaded_bytes']
                elif 'total_bytes_estimate' in d:
                    total = d['total_bytes_estimate']
                    downloaded = d['downloaded_bytes']
                else:
                    return
                    
                if total > 0:
                    percentage = (downloaded / total) * 100
                    self.progress.emit(percentage)
            except:
                pass
        elif d['status'] == 'finished':
            self.progress.emit(100)
            
    def fetch_thumbnail(self, url):
        try:
            response = requests.get(url)
            image = QImage()
            image.loadFromData(response.content)
            return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Thumbnail error: {str(e)}")
            return QPixmap()
            
    def run(self):
        try:
            print(f"Attempting to process URL: {self.url}")
            
            base_opts = {
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'ignoreerrors': False,
                'no_color': True,
                'nocheckcertificate': True,
                'socket_timeout': 30,
                'verbose': True,
                'no_check_certificates': True,
                'extractor_retries': 3,
                'format_sort': ['res', 'ext:mp4:m4a', 'codec:h264'],
                'merge_output_format': 'mp4'
            }

            # Add ffmpeg location if available
            if FFMPEG_PATH:
                base_opts['ffmpeg_location'] = FFMPEG_PATH

            # First, get available formats
            if not self.is_downloading:
                ydl_opts = {
                    **base_opts,
                    'format': 'best',
                    'listformats': True,
                    'skip_download': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        print("Extracting video info...")
                        info = ydl.extract_info(self.url, download=False)
                        
                        if info:
                            print("Successfully retrieved video info")
                            video_info = VideoInfo()
                            video_info.title = info.get('title', '')
                            video_info.duration = str(info.get('duration', 0))
                            video_info.thumbnail_url = info.get('thumbnail', '')
                            video_info.channel = info.get('channel', '')
                            video_info.views = str(info.get('view_count', 0))
                            video_info.upload_date = info.get('upload_date', '')
                            
                            # Get available formats
                            formats = info.get('formats', [])
                            video_info.available_formats = []
                            
                            print("\nAvailable formats:")
                            for f in formats:
                                format_id = f.get('format_id', '')
                                ext = f.get('ext', '')
                                resolution = f.get('resolution', 'N/A')
                                filesize = f.get('filesize', 0)
                                format_note = f.get('format_note', '')
                                acodec = f.get('acodec', 'none')
                                vcodec = f.get('vcodec', 'none')
                                
                                # Skip formats without video
                                if vcodec == 'none':
                                    continue
                                
                                # Calculate size in MB
                                size_mb = filesize / (1024 * 1024) if filesize else 0
                                
                                # Create format description
                                quality = format_note if format_note else resolution
                                if not quality:
                                    quality = 'N/A'
                                
                                # Add audio indicator (removed from display)
                                has_audio = acodec != 'none'
                                quality_text = quality
                                
                                format_info = {
                                    'format_id': f"{format_id}+bestaudio" if not has_audio else format_id,
                                    'ext': ext,
                                    'quality': quality_text,
                                    'size': f"{size_mb:.1f} MB" if size_mb > 0 else "N/A",
                                }
                                
                                print(f"Format ID: {format_id}, Extension: {ext}, Quality: {quality_text}, Size: {format_info['size']}")
                                video_info.available_formats.append(format_info)
                            
                            if video_info.thumbnail_url:
                                print(f"\nFetching thumbnail from: {video_info.thumbnail_url}")
                                video_info.thumbnail = self.fetch_thumbnail(video_info.thumbnail_url)
                            
                            self.info_ready.emit(video_info)
                            
                        else:
                            print("No video information retrieved")
                            self.error.emit("Could not retrieve video information. Please check if the video exists and is not private.")
                    except Exception as e:
                        print(f"Error getting video info: {str(e)}")
                        self.error.emit(f"Error: {str(e)}")
            else:
                # Download with selected format
                format_spec = self.format_id
                if format_spec == 'best':
                    format_spec = 'bestvideo+bestaudio/best'
                
                ydl_opts = {
                    **base_opts,
                    'format': format_spec,
                    'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook]
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        print(f"\nStarting download with format: {format_spec}")
                        ydl.download([self.url])
                        self.finished.emit()
                    except Exception as e:
                        print(f"Download error: {str(e)}")
                        self.error.emit(f"Download Error: {str(e)}")
                        
        except Exception as e:
            print(f"Fatal error: {str(e)}")
            self.error.emit(f"Fatal Error: {str(e)}")

class VideoInfoWidget(QFrame):
    download_clicked = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Left section (Thumbnail)
        left_section = QFrame()
        left_section.setProperty("class", "CardFrame")
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setMinimumSize(400, 300)
        self.thumbnail_label.setMaximumSize(600, 400)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet(f"""
            QLabel {{
                background-color: {NAVY_BLUE};
                border: 1px solid {BORDER_BLUE};
                border-radius: 5px;
            }}
        """)
        left_layout.addWidget(self.thumbnail_label)
        main_layout.addWidget(left_section)
        
        # Right section
        right_section = QVBoxLayout()
        right_section.setSpacing(20)
        
        # Video info card
        info_card = QFrame()
        info_card.setProperty("class", "CardFrame")
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(10)
        
        self.title_label = QLabel()
        self.title_label.setProperty("heading", True)
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)
        
        details_widget = QWidget()
        details_layout = QGridLayout(details_widget)
        details_layout.setSpacing(5)
        details_layout.setContentsMargins(5, 5, 5, 5)
        
        # Video details in grid layout
        self.channel_label = QLabel()
        self.views_label = QLabel()
        self.duration_label = QLabel()
        self.upload_date_label = QLabel()
        
        for label in [self.channel_label, self.views_label, self.duration_label, self.upload_date_label]:
            label.setProperty("info", True)
        
        details_layout.addWidget(self.channel_label, 0, 0)
        details_layout.addWidget(self.views_label, 0, 1)
        details_layout.addWidget(self.duration_label, 1, 0)
        details_layout.addWidget(self.upload_date_label, 1, 1)
        
        info_layout.addWidget(details_widget)
        right_section.addWidget(info_card)
        
        # Formats card
        formats_card = QFrame()
        formats_card.setProperty("class", "CardFrame")
        formats_layout = QVBoxLayout(formats_card)
        formats_layout.setSpacing(10)
        formats_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with icon and text
        header_layout = QHBoxLayout()
        formats_header = QLabel("Available Formats")
        formats_header.setProperty("heading", True)
        header_layout.addWidget(formats_header)
        header_layout.addStretch()
        formats_layout.addLayout(header_layout)
        
        # Format table with improved styling
        self.format_table = QTableWidget()
        self.format_table.setColumnCount(4)
        self.format_table.setHorizontalHeaderLabels(['Format', 'Quality', 'Size', ''])
        self.format_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.format_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Back to Stretch
        self.format_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.format_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.format_table.setColumnWidth(0, 80)  # Format column
        self.format_table.setColumnWidth(2, 100)  # Size column - original width
        self.format_table.setColumnWidth(3, 100)  # Download button column - original width
        self.format_table.verticalHeader().setVisible(False)
        self.format_table.setShowGrid(False)
        self.format_table.setMinimumHeight(200) 
        
        # Additional styling
        self.format_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {BORDER_BLUE};
                border-radius: 8px;
                padding: 5px;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {BORDER_BLUE};
                margin: 5px;
            }}
        """)
        
        formats_layout.addWidget(self.format_table)
        right_section.addWidget(formats_card)
        
        main_layout.addLayout(right_section)
        
        # Set stretch factors for better scaling
        main_layout.setStretchFactor(left_section, 50)
        main_layout.setStretchFactor(right_section, 50)

    def update_info(self, video_info):
        # Update title
        self.title_label.setText(video_info.title)
        
        # Format numbers with commas
        try:
            views = "{:,}".format(int(video_info.views))
        except:
            views = video_info.views
            
        # Convert duration to HH:MM:SS
        try:
            duration = int(video_info.duration)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
        except:
            duration_str = video_info.duration
        
        # Format date as YYYY-MM-DD
        try:
            upload_date = f"{video_info.upload_date[0:4]}-{video_info.upload_date[4:6]}-{video_info.upload_date[6:8]}"
        except:
            upload_date = video_info.upload_date
        
        # Update info labels
        self.channel_label.setText(f"Channel: {video_info.channel}")
        self.views_label.setText(f"Views: {views}")
        self.duration_label.setText(f"Duration: {duration_str}")
        self.upload_date_label.setText(f"Upload Date: {upload_date}")
        
        # Update thumbnail
        if video_info.thumbnail:
            scaled_pixmap = video_info.thumbnail.scaled(
                self.thumbnail_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.thumbnail_label.setPixmap(scaled_pixmap)
        
        # Clear and update format table
        self.format_table.setRowCount(0)
        
        # Add "best" quality option first
        self.add_format_row({
            'format_id': 'best',
            'ext': 'AUTO',
            'quality': 'Best Quality',
            'size': 'Auto'
        })
        
        # Add available formats
        for fmt in video_info.available_formats:
            self.add_format_row(fmt)

    def add_format_row(self, fmt):
        row = self.format_table.rowCount()
        self.format_table.insertRow(row)
        
        # Format
        format_item = QTableWidgetItem(fmt['ext'].upper())
        format_item.setTextAlignment(Qt.AlignCenter)
        format_item.setBackground(QBrush(QColor(NAVY_BLUE)))
        self.format_table.setItem(row, 0, format_item)
        
        # Quality
        quality_item = QTableWidgetItem(fmt['quality'])
        quality_item.setTextAlignment(Qt.AlignCenter)
        quality_item.setBackground(QBrush(QColor(NAVY_BLUE)))
        self.format_table.setItem(row, 1, quality_item)
        
        # Size
        size_item = QTableWidgetItem(fmt['size'])
        size_item.setTextAlignment(Qt.AlignCenter)
        size_item.setBackground(QBrush(QColor(NAVY_BLUE)))
        self.format_table.setItem(row, 2, size_item)
        
        # Download button with improved styling and emoji
        download_btn = QPushButton("Download")
        download_btn.setProperty("download", True)
        download_btn.setProperty("format_id", fmt['format_id'])
        download_btn.clicked.connect(lambda: self.download_clicked.emit(fmt['format_id']))
        self.format_table.setCellWidget(row, 3, download_btn)
        
        # Set row height
        self.format_table.setRowHeight(row, 45)

class BrandingWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "CardFrame")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Title and subtitle
        text_container = QVBoxLayout()
        text_container.setSpacing(5)
        
        # Organization name with party popper emoji
        org_name = QLabel("Computer Society of India 🎉")
        org_name.setProperty("heading", True)
        text_container.addWidget(org_name)
        
        # Title container for YouTube icon and text
        title_container = QHBoxLayout()
        title_container.setSpacing(5)
        
        # YouTube icon (using text emoji as fallback)
        youtube_icon = QLabel("▶️")
        youtube_icon.setProperty("subheading", True)
        title_container.addWidget(youtube_icon)
        
        # Video Downloader text
        title = QLabel("Video Downloader    ⬇️")
        title.setProperty("subheading", True)
        title_container.addWidget(title)
        title_container.addStretch()
        
        text_container.addLayout(title_container)
        
        subtitle = QLabel("      ~     Powered by yt-dlp     ~      ")
        subtitle.setProperty("info", True)
        text_container.addWidget(subtitle)
        
        layout.addLayout(text_container)
        layout.addStretch()
        
        # Tricolor flag
        flag_container = QHBoxLayout()
        flag_container.setSpacing(0)
        
        for color in [FLAG_ORANGE, TEXT_COLOR, FLAG_GREEN]:
            flag = QFrame()
            flag.setStyleSheet(f"background-color: {color};")
            flag.setFixedSize(25, 25)
            flag_container.addWidget(flag)
        
        layout.addLayout(flag_container)

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('CSI-VIT YouTube Downloader')
        self.setMinimumSize(800, 600)
        self.setStyleSheet(STYLE_SHEET)
        
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)  
        main_layout.setContentsMargins(15, 15, 15, 15) 
        
        # Branding
        branding = BrandingWidget()
        main_layout.addWidget(branding)
        
        # URL input card
        url_card = QFrame()
        url_card.setProperty("class", "CardFrame")
        url_layout = QHBoxLayout(url_card)
        url_layout.setContentsMargins(20, 20, 20, 20)
        url_layout.setSpacing(15)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('Enter YouTube URL')
        self.url_input.textChanged.connect(self.on_url_changed)
        url_layout.addWidget(self.url_input)
        
        self.browse_btn = QPushButton('Select Folder')
        self.browse_btn.setProperty("secondary", True)
        self.browse_btn.clicked.connect(self.browse_location)
        url_layout.addWidget(self.browse_btn)
        
        main_layout.addWidget(url_card)
        
        # Video info
        self.video_info = VideoInfoWidget()
        self.video_info.download_clicked.connect(self.start_download)
        main_layout.addWidget(self.video_info)
        
        # Bottom status card
        status_card = QFrame()
        status_card.setProperty("class", "CardFrame")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 15, 20, 15)
        
        self.location_label = QLabel('Save location: Not selected')
        self.location_label.setProperty("info", True)
        status_layout.addWidget(self.location_label)
        
        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        status_layout.addWidget(self.progress)
        
        main_layout.addWidget(status_card)
        
        self.save_path = ''
        self.current_worker = None
        self.url_check_timer = QTimer()
        self.url_check_timer.setSingleShot(True)
        self.url_check_timer.timeout.connect(self.fetch_video_info)
        
        self.center_on_screen()
        self.show()
        
    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)
        
    def on_url_changed(self):
        self.url_check_timer.start(1000)  # Wait 1 second after typing
        
    def fetch_video_info(self):
        if not self.url_input.text():
            return
            
        self.progress.setValue(0)
        
        self.current_worker = DownloadWorker(self.url_input.text(), "")
        self.current_worker.info_ready.connect(self.handle_video_info)
        self.current_worker.error.connect(self.handle_error)
        self.current_worker.start()
        
    def handle_video_info(self, video_info):
        self.video_info.update_info(video_info)
        
    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Download Location')
        if folder:
            self.save_path = folder
            self.location_label.setText(f'Save location: {folder}')
            
    def start_download(self, format_id):
        if not self.url_input.text():
            QMessageBox.warning(self, 'Error', 'Please enter a YouTube URL')
            return
            
        if not self.save_path:
            QMessageBox.warning(self, 'Error', 'Please select a save location')
            return
            
        self.progress.setValue(0)
        
        self.current_worker = DownloadWorker(self.url_input.text(), self.save_path, format_id)
        self.current_worker.progress.connect(self.update_progress)
        self.current_worker.finished.connect(self.download_finished)
        self.current_worker.error.connect(self.handle_error)
        self.current_worker.is_downloading = True
        self.current_worker.start()
        
    def update_progress(self, value):
        self.progress.setValue(int(value))
        
    def download_finished(self):
        QMessageBox.information(self, 'Success', 'Download completed successfully!')
        
    def handle_error(self, error_msg):
        QMessageBox.critical(self, 'Error', f'Operation failed: {error_msg}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloader()
    sys.exit(app.exec()) 