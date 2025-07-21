#backend/youtube.py
import json
import os
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


def fetch_subscriptions(creds: Credentials, user_email: str) -> list[dict]:
    youtube = build('youtube', 'v3', credentials=creds)

    subscriptions = []
    next_page_token = None

    try:
        while True:
            request = youtube.subscriptions().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            subscriptions += response.get("items", [])
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
    except HttpError as e:
        print("YouTube API Error:", e)
        return []

    channel_ids = [
        item.get('snippet', {}).get('resourceId', {}).get('channelId')
        for item in subscriptions
        if item.get('snippet', {}).get('resourceId', {}).get('channelId')
    ]

    channel_data = []
    for i in range(0, len(channel_ids), 50):
        try:
            res = youtube.channels().list(
                part="snippet,contentDetails,statistics,brandingSettings,topicDetails,status",
                id=",".join(channel_ids[i:i + 50])
            ).execute()
        except HttpError as e:
            print(f"Error fetching channels {i}-{i+50}:", e)
            continue

        for item in res.get("items", []):
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})
            content_details = item.get('contentDetails', {})

            snippet['title'] = snippet.get('title', '❓ Unknown Title')
            stats.setdefault('subscriberCount', 0)
            stats.setdefault('videoCount', 0)
            stats.setdefault('viewCount', 0)

            latest_date = None
            try:
                uploads_playlist = content_details.get("relatedPlaylists", {}).get("uploads")
                if uploads_playlist:
                    upload_res = youtube.playlistItems().list(
                        part="contentDetails",
                        playlistId=uploads_playlist,
                        maxResults=1
                    ).execute()
                    latest_item = upload_res.get("items", [])[0]
                    latest_date = latest_item["contentDetails"].get("videoPublishedAt")
            except Exception:
                latest_date = None

            channel_id = item.get("id")
            if not channel_id:
                continue

            item["channelUrl"] = f"https://www.youtube.com/channel/{channel_id}"
            item["latestVideoDate"] = latest_date
            item["snippet"] = snippet
            item["statistics"] = stats
            channel_data.append(item)

    # Save to user folder
    user_dir = f'users/{user_email}'
    os.makedirs(user_dir, exist_ok=True)
    try:
        with open(f"{user_dir}/youtube_subscriptions.json", 'w', encoding='utf-8') as f:
            json.dump(channel_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to write subscription data for {user_email}: {e}")

    return channel_data
