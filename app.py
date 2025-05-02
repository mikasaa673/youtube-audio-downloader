from flask import Flask, request, render_template, send_from_directory
import yt_dlp as youtube_dl
import os
import re

app = Flask(__name__)

# Define a directory to save downloaded audio files
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def clean_filename(filename):
    # Remove invalid characters from the filename
    cleaned_filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    return cleaned_filename

def save_audio(url):
    try:
        options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, clean_filename('%(title)s.%(ext)s')),
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = clean_filename(f"{info['title']}.mp3")  # Get the cleaned filename
            return os.path.join(DOWNLOAD_FOLDER, filename)  # Return the full path to the file
    except Exception as e:
        return None, f"An error occurred while downloading the audio: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        
        # Save the audio and get the filename
        file_path = save_audio(url)
        if file_path:
            # Return the download link
            return render_template('index.html', message='Audio download complete!', file_path=file_path)
        else:
            message = "Download failed."
            return render_template('index.html', message=message)
    
    return render_template('index.html', message='')

# Add a new route to serve the CSS file from the templates directory
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('templates', filename)

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    # Send the file for download
    return send_from_directory(DOWNLOAD_FOLDER, os.path.basename(filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)