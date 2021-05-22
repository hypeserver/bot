from datetime import datetime

from slack_sdk.errors import SlackApiError

import config as cfg
from sheets import Sheet as pins_sheet
from utils.client import client

MESSAGE_SAVER_SHEET = "saved"
SHEET_LINK = f"https://docs.google.com/spreadsheets/d/{cfg.SPREADSHEET_ID}"


def handle_mention(mention_event, thread_content):
    raw_mention = mention_event["text"]
    words = raw_mention.split()
    for cmd, handler in COMMAND_HANDLERS.items():
        if detected_cmd := set(cmd) & set(words):
            print(f" handling {detected_cmd}")
            handler(mention_event, thread_content)


def message_saver(mention_event, thread_content):
    thread_start_msg = thread_content.data["messages"][0]
    txt = thread_start_msg["text"]
    channel = mention_event["channel"]
    thread_ts = mention_event["thread_ts"]
    try:
        client.reactions_add(channel=channel, timestamp=thread_ts, name="floppy_disk")
    except SlackApiError:
        pass
    username = client.users_info(user=thread_start_msg["user"])["user"]["profile"]["display_name"]
    dt = datetime.fromtimestamp(float(thread_ts)).strftime("%d/%m/%Y %H:%M:%S")
    pins_sheet.append([channel, dt, username, txt], subsheet=MESSAGE_SAVER_SHEET)
    client.chat_postMessage(text=f"```{txt}``` Aldim bunu.", thread_ts=thread_ts, channel=channel)


def post_sheet(mention_event, thread_content):
    thread_ts = mention_event["thread_ts"]
    channel = mention_event["channel"]
    client.chat_postMessage(text=f"Hemen sizi sheetliyorum: {SHEET_LINK}", thread_ts=thread_ts, channel=channel)


def ping_pong(mention_event, thread_content):
    thread_ts = mention_event["thread_ts"]
    channel = mention_event["channel"]
    client.chat_postMessage(text="PONG", thread_ts=thread_ts, channel=channel)


COMMAND_HANDLERS = {
    ("al", "gomcur", "kapakla", "yapistir"): message_saver,
    ("sheet", "shit", "sheetle"): post_sheet,
    ("ping",): ping_pong,
}
