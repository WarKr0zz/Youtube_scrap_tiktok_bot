import os
import threading
from tkinter import Tk, Label, Entry, Button, StringVar
from moviepy.editor import VideoFileClip
from googleapiclient.discovery import build
from pytube import YouTube
import random

def get_channel_name(api_key, channel_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.channels().list(
        part="snippet",
        id=channel_id,
    )
    response = request.execute()
    channel_name = response['items'][0]['snippet']['title']
    return channel_name

def get_latest_videos(api_key, channel_id, max_results=50):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        type="video",
        maxResults=max_results,
        order="date",
    )
    response = request.execute()
    videos = response["items"]
    return videos

def download_and_split_videos(api_key, channel_id, max_results=50, split_duration_range=(63, 76)):
    channel_name = get_channel_name(api_key, channel_id)
    output_folder = f"videos_{channel_name}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    videos = get_latest_videos(api_key, channel_id, max_results)
    for video in videos:
        video_id = video["id"]["videoId"]
        video_title = video["snippet"]["title"]
        video_link = f"https://www.youtube.com/watch?v={video_id}"

        try:
            yt = YouTube(video_link)
            stream = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
            file_name = stream.default_filename.rsplit(".", 1)[0]
            file_path = os.path.join(output_folder, f"{file_name}.mp4")

            if not os.path.exists(file_path):
                stream.download(output_path=output_folder, filename=f"{file_name}.mp4")

            clip = VideoFileClip(file_path)

            if channel_id == "":   #Replace with your channel ID
                clip = clip.subclip(6, clip.duration - 31)

            n_parts = int(clip.duration // random.uniform(*split_duration_range)) + 1
            for i in range(n_parts):
                split_file_path = os.path.join(output_folder, f"{file_name}_part{i+1}.mp4")
                if not os.path.exists(split_file_path):
                    start_time = i * random.uniform(*split_duration_range)
                    end_time = min((i + 1) * random.uniform(*split_duration_range), clip.duration)
                    subclip = clip.subclip(start_time, end_time)
                    subclip.write_videofile(split_file_path)

            print(f"Downloaded and split video: {video_title}")
        except Exception as e:
            print(f"Error while downloading or splitting video: {video_title}")
            print(str(e))


def start_download(api_key, channel_id):
    download_thread = threading.Thread(target=download_and_split_videos, args=(api_key, channel_id))
    download_thread.start()

# Tkinter GUI

def on_submit():
    channel_id = channel_id_var.get()
    start_download(api_key, channel_id)
    channel_id_var.set('')



if __name__ == "__main__":
    api_key = "API KEY"  # Replace with your API key

    root = Tk()
    root.title("YouTube Video Downloader")

    channel_id_var = StringVar()

    label = Label(root, text="Channel ID:")
    label.grid(row=0, column=0, padx=5, pady=5)

    entry = Entry(root, textvariable=channel_id_var)
    entry.grid(row=0, column=1, padx=5, pady=5)

    submit_button = Button(root, text="Download", command=on_submit)
    submit_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    root.mainloop()
                    
