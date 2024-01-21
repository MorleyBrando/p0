import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = os.getenv("BOT_ID")
GROUP_ID = os.getenv("GROUP_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LAST_TIMESTAMP = None  # Use timestamp instead of message ID to track the latest message


def send_message(text, attachments=None):
    """Send a message to the group using the bot."""
    post_url = "https://api.groupme.com/v3/bots/post"
    data = {"bot_id": BOT_ID, "text": text, "attachments": attachments or []}
    response = requests.post(post_url, json=data)
    return response.status_code == 202


def get_group_messages():
    """Retrieve recent messages from the group."""
    params = {"token": ACCESS_TOKEN}
    get_url = f"https://api.groupme.com/v3/groups/{GROUP_ID}/messages"
    response = requests.get(get_url, params=params)
    if response.status_code == 200:
        return response.json().get("response", {}).get("messages", [])
    return []


import giphy_client
from giphy_client.rest import ApiException

giphy_api_key = os.getenv("GIPHY_API_KEY")
api_instance = giphy_client.DefaultApi()

def send_gif(tag):
    try:
        # Get a random GIF based on the tag
        response = api_instance.gifs_random_get(giphy_api_key, tag=tag, rating='g')
        gif_url = response.data.image_url
        send_message(gif_url)
    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_random_get: %s\n" % e)

def process_message(message):
    global LAST_TIMESTAMP
    sender_id = message["sender_id"]
    sender_name = message["name"]
    text = message["text"].lower()
    timestamp = message["created_at"]

    if LAST_TIMESTAMP is None or timestamp > LAST_TIMESTAMP:
        # Responding to your message only
        if sender_id == 90793732:
            send_message("Hello! This is your bot responding to your message.")

        #Not own Bot
        if message["sender_type"] != "bot":
        # Good Morning/Good Night
            if "good morning" in text:
                send_message(f"Good morning, {sender_name}!")
            elif "good night" in text:
                send_message(f"Good night, {sender_name}!")

            
            if "giphy" in text:    
                search_term = text.replace("/giphy", "").strip()
                if search_term:
                    send_gif(search_term)

        LAST_TIMESTAMP = timestamp

def main():
    global LAST_TIMESTAMP 
    LAST_TIMESTAMP = get_group_messages()[0]["created_at"]

    while True:
        messages = get_group_messages()

        for message in reversed(messages):
            process_message(message)

        time.sleep(10)
        print("check")


if __name__ == "__main__":
    main()
