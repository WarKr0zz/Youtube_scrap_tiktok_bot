from googleapiclient.discovery import build

def get_channel_id(api_key, custom_channel_name):
    youtube = build("youtube", "v3", developerKey=api_key)

    try:
        request = youtube.search().list(
            part="snippet",
            type="channel",
            q=custom_channel_name,
            maxResults=1
        )
        response = request.execute()
        channel_id = response['items'][0]['snippet']['channelId']
        return channel_id
    except Exception as e:
        print(f"Error while searching for channel ID: {custom_channel_name}")
        print(str(e))
        return None

if __name__ == "__main__":
    api_key = "API_KEY"  # Replace with your API key
    custom_channel_name = "Name_channel"  # Replace with custom channel name

    channel_id = get_channel_id(api_key, custom_channel_name)
    print(f"The channel ID for {custom_channel_name} is: {channel_id}")
