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
        print(f"Erreur lors de la recherche de l'ID de la chaîne : {custom_channel_name}")
        print(str(e))
        return None

if __name__ == "__main__":
    api_key = "AIzaSyCxlrDmgPKQS0Abv1b5od_deY3G-AlYJHU"  # Remplacez par votre clé API
    custom_channel_name = "YomiDenzel"  # Remplacez par le nom personnalisé de la chaîne

    channel_id = get_channel_id(api_key, custom_channel_name)
    print(f"L'ID de la chaîne pour {custom_channel_name} est : {channel_id}")