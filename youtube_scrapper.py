import os
import isodate
import requests
from googleapiclient.discovery import build
from pytube import YouTube

def get_channel_videos(api_key, channel_id, max_results=50):
    youtube = build("youtube", "v3", developerKey=api_key)

    try:
        request = youtube.search().list(
            part="id,snippet",
            channelId=channel_id,
            type="video",
            maxResults=max_results,
            order="date"
        )
        response = request.execute()
        video_ids = [item['id']['videoId'] for item in response['items']]

        video_details_request = youtube.videos().list(
            part="contentDetails",
            id=','.join(video_ids)
        )
        video_details_response = video_details_request.execute()
        video_durations = [isodate.parse_duration(item['contentDetails']['duration']).total_seconds() for item in video_details_response['items']]

        return list(zip(response["items"], video_durations))
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []

def download_thumbnail(url, output_folder, file_name):
    response = requests.get(url)
    with open(f"{output_folder}/{file_name}_thumbnail.jpg", "wb") as file:
        file.write(response.content)

def download_shorts(api_key, channel_id, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    videos = get_channel_videos(api_key, channel_id)
    for video, duration in videos:
        video_id = video["id"]["videoId"]
        video_title = video["snippet"]["title"]
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        thumbnail_url = video["snippet"]["thumbnails"]["high"]["url"]

        if duration < 60:  # Vérifie si la vidéo est un short (moins de 60 secondes)
            try:
                yt = YouTube(video_link)
                stream = yt.streams.filter(file_extension='mp4', progressive=True).first()
                file_name = stream.default_filename.rsplit(".", 1)[0]
                stream.download(output_path=output_folder, filename=file_name)
                print(f"Vidéo téléchargée: {video_title}")

                download_thumbnail(thumbnail_url, output_folder, file_name)
                print(f"Miniature téléchargée: {file_name}_thumbnail.jpg")
            except Exception as e:
                print(f"Erreur lors du téléchargement de la vidéo ou de la miniature: {video_title}")
                print(str(e))

if __name__ == "__main__":
    api_key = "AIzaSyCxlrDmgPKQS0Abv1b5od_deY3G-AlYJHU"  # Remplacez par votre clé API
    channel_id = "UChgE6R4QauGAJAlYiJOcCGw"  # Remplacez par l'ID de la chaîne YouTube
    output_folder = f"videos_{channel_id}" 

    download_shorts(api_key, channel_id, output_folder)