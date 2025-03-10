# 🎬 CSI-VIT YouTube Video Downloader

A modern desktop application that allows you to download YouTube videos using yt-dlp with a professional GUI interface.

---

## ✨ Features

✅ **Modern, professional UI** with CSI-VIT branding\
✅ **Real-time video information display**:

- 📌 Video title and thumbnail
- 🎥 Channel name
- 👁️ View count
- 📅 Upload date
- ⏳ Duration ✅ **Multiple format options**:
- 🔹 Best quality (automatic)
- 🔹 Various resolutions (144p to 4K)
- 🔹 Different formats (MP4, WebM) ✅ **Built-in features**:
- 🎵 Integrated ffmpeg support
- 📊 Progress tracking
- ⚠️ Error handling
- 📂 Custom download location
- ℹ️ Format size information ✅ **User-friendly interface**:
- 🃏 Card-based layout
- 🎯 Clear visual hierarchy
- 📱 Responsive design
- 🌙 Dark mode

---

## 🛠️ Installation

1️⃣ Ensure you have **Python 3.9 or higher** installed (Python 3.8 is deprecated).\
2️⃣ Clone this repository:

```bash
git clone [repository-url]
cd ytdldownloader
```

3️⃣ Install the required dependencies:

```bash
pip install -r requirements.txt
```

4️⃣ *(OPTIONAL - If your video downloads without audio, follow these steps to install ffmpeg)*:

- 📁 Create a folder named **'ffmpeg'** in the application directory.
- 📥 Download **ffmpeg** from [this link](https://www.gyan.dev/ffmpeg/builds/).
- 🗂️ Extract and place `ffmpeg.exe` in the **'ffmpeg'** folder.

---

## 🚀 Usage

1️⃣ Run the application:

```bash
python youtube_downloader.py
```

2️⃣ Enter a **YouTube URL** in the input field.\
3️⃣ The **video information** will be automatically loaded.\
4️⃣ Click **"Select Folder"** to choose where you want to save the video.\
5️⃣ Choose your **preferred format** from the available options.\
6️⃣ Click the **"Download"** button next to your chosen format.\
7️⃣ Monitor the **progress** through the progress bar.\
8️⃣ Once complete, you'll find your video in the **selected folder**.

---

## 📌 Requirements

- 🐍 **Python** 3.9+ *(3.8 is deprecated)*
- 🎭 **PySide6** >= 6.5.0 *(Qt for Python)*
- 🎞 **yt-dlp** >= 2024.3.10
- 🌐 **requests** >= 2.31.0
- 🖼 **Pillow** >= 10.0.0
- 🎶 **ffmpeg** *(included in the ffmpeg folder)*

---

## 🔔 Note

📌 This application is developed by **CSI-VIT** and downloads videos in your chosen quality.\
📌 Please ensure you have **permission** to download any content before using this tool.

---

## ⚖️ Legal

🚨 **This tool is for educational purposes only.** Users are responsible for complying with **local laws** and **YouTube's terms of service** when downloading content.

