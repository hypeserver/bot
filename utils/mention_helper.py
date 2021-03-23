from datetime import datetime

from slack_sdk.errors import SlackApiError

from utils.client import client
from sheets import Sheet as pins_sheet

MESSAGE_SAVER_SHEET = "saved"


def handle_mention(mention_event, thread_content):
    raw_mention = mention_event["text"]
    words = raw_mention.split()
    for cmd, handler in COMMAND_HANDLERS.items():
        if set(cmd) & set(words):
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


COMMAND_HANDLERS = {
    ("al", "gomcur", "kapakla", "yapistir"): message_saver,
}
