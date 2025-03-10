# 🎬 CSI-VIT YouTube Video Downloader

A modern desktop application that allows you to download YouTube videos using yt-dlp with a GUI interface. This application that lets you download videos from YouTube. You can copy-paste URL of any video and download it directly to a format of your choice.

> Note: This application uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) under the hood to interact with YouTube. You can check this repository to learn more.

---
![image](https://github.com/user-attachments/assets/4e880a42-1433-4e04-8ef1-da3a627476fb)
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

1️⃣ Ensure you have [**Python 3.9 or higher**](https://www.python.org/downloads/) installed (Python 3.8 is deprecated).
2️⃣ Download the [ytdownloader.py](ytdownloader.py) and [requirements.txt](requirements.txt) file:
3️⃣ Install the required dependencies:
> ### NOTE:- The following command will automatically install the package dependencies.
```bash
pip install -r requirements.txt
```
4️⃣ **OPTIONAL** - If your video downloads without audio, follow these steps to install ffmpeg manually:
- 📁 Create a folder named **'ffmpeg'** in the application directory.
- 📥 Download **ffmpeg** from [this link](https://www.gyan.dev/ffmpeg/builds/).
- 🗂️ Extract and place `ffmpeg.exe` in the **'ffmpeg'** folder.

---

## 🚀 Usage

1️⃣ Run the application:
> Use the following command to run the application.
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

📌 This application is doesn't support or encourage piracy of any means.
📌 Please ensure you have **permission** to download any content before using this tool.

---

## ⚖️ Legal

🚨 **This tool is for educational purposes only.** Users are responsible for complying with **local laws** and **YouTube's terms of service** when downloading content.

