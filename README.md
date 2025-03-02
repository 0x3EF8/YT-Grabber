
# YT Grabber

YT Grabber is a simple GUI-based YouTube downloader built using Python and Tkinter. It utilizes [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading videos or extracting audio, and leverages FFmpeg to process media files. This tool offers a modern interface with custom-styled buttons, progress tracking, and system tray integration.

## Features

- **Video & Audio Downloads:** Choose between downloading full videos (MP4) or extracting audio (MP3).
- **Multiple Quality Options:** Select your desired video resolution or audio bitrate.
- **Custom GUI:** Modern look with a custom title bar, rounded buttons, and progress updates.
- **System Tray Integration:** Minimize the application to the system tray for unobtrusive operation.
- **FFmpeg Automation:** Automatically checks for and attempts to install FFmpeg on Windows using winget.

## Installation

1. **Prerequisites:**
   - Python 3.6 or higher.
   - On Windows, [winget](https://docs.microsoft.com/en-us/windows/package-manager/winget/) for FFmpeg installation.
   - FFmpeg is required for media processing. If not installed automatically, install it manually.

2. **Clone the Repository or Download the Source:**

   ```bash
   git clone https://github.com/0x3EF8/YT-Grabber.git
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application:**

   ```bash
   cd src
   python main.py
   ```

2. **Enter the YouTube URL:** Input the URL of the YouTube video you want to download.

3. **Select Options:**
   - **Format:** Choose between video (MP4) or audio (MP3).
   - **Quality:** Select the desired quality from the dropdown.
   - **Save Location:** Use the Browse button to choose a download folder (defaults to `~/Downloads`).

4. **Start Download:** Click the **Download** button. The progress bar and status messages will update as the download proceeds.

5. **Minimize to Tray:** Use the minimize button to send the app to the system tray and restore it later if needed.

## Dependencies

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** For downloading video/audio content.
- **[Pillow](https://python-pillow.org/):** For image processing within the GUI.
- **[pystray](https://github.com/moses-palmer/pystray):** For system tray integration.
- **Tkinter:** Standard Python GUI toolkit (bundled with Python).

## Troubleshooting

- **FFmpeg Installation Issues:** If FFmpeg fails to install automatically, download and install it manually from the [official website](https://ffmpeg.org/download.html).
- **OS Compatibility:** This script is primarily designed for Windows. Users on other platforms might need to manually install FFmpeg and adapt the script if necessary.

## License

This project is open source and available under the [MIT License](LICENSE).

```

These files should help set up and document your project effectively.
