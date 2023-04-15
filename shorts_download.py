import os
import isodate
from googleapiclient.discovery import build
from pytube import YouTube

def get_channel_name(api_key, channel_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.channels().list(
        part="snippet",
        id=channel_id,
    )
    response = request.execute()
    channel_name = response['items'][0]['snippet']['title']
    return channel_name

def get_channel_videos(api_key, channel_id, max_results=50):
    youtube = build("youtube", "v3", developerKey=api_key)
    videos = []

    try:
        next_page_token = None
        while True:
            request = youtube.search().list(
                part="id,snippet",
                channelId=channel_id,
                type="video",
                maxResults=max_results,
                order="date",
                pageToken=next_page_token,
            )
            response = request.execute()
            video_ids = [item['id']['videoId'] for item in response['items']]

            video_details_request = youtube.videos().list(
                part="contentDetails",
                id=','.join(video_ids)
            )
            video_details_response = video_details_request.execute()
            video_durations = [isodate.parse_duration(item['contentDetails']['duration']).total_seconds() for item in video_details_response['items']]

            videos.extend(list(zip(response["items"], video_durations)))

            next_page_token = response.get('nextPageToken', None)
            if not next_page_token:
                break

        return videos
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []
      
def download_shorts(api_key, channel_id):
    channel_name = get_channel_name(api_key, channel_id)
    output_folder = f"videos_{channel_name}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    videos = get_channel_videos(api_key, channel_id)
    for video, duration in videos:
        if duration < 80:  # Check if the video is a short (less than 80 seconds)
            video_id = video["id"]["videoId"]
            video_title = video["snippet"]["title"]
            video_link = f"https://www.youtube.com/watch?v={video_id}"

            try:
                yt = YouTube(video_link)
                video_stream = yt.streams.filter(file_extension='mp4', adaptive=True, only_video=True).order_by('resolution').desc().first()
                audio_stream = yt.streams.filter(file_extension='mp4', adaptive=True, only_audio=True).order_by('abr').desc().first()
                video_file = video_stream.download(output_path=output_folder, filename=f"{video_id}_video.mp4", skip_existing=True)
                audio_file = audio_stream.download(output_path=output_folder, filename=f"{video_id}_audio.mp4", skip_existing=True)
                
                output_file = os.path.join(output_folder, f"{video_id}.mp4")

                os.system(f"ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac -strict -2 -y {output_file}")
                os.remove(video_file)
                os.remove(audio_file)

                print(f"Short downloaded: {video_title}")
            except Exception as e:
                print(f"Error downloading short: {video_title}")
                print(str(e))

if __name__ == "__main__":
    api_key = "API-KEY"  # Replace with your API key
    channel_id = "CHANNEL_ID"  # Replace with the YouTube channel ID

    download_shorts(api_key, channel_id)
