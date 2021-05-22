import random
from datetime import datetime

from slack_sdk.errors import SlackApiError

from sheets import Sheet as pins_sheet
from utils.client import client

LINK_CURATE_CHANNELS_NAMES = ["linx"]

IS_BITINCE_KOMIKLIKLER_SAKALAR = [
    "Kuskusuz ki o {channel_name} kanalindaki {links_len} linki arsivleyendir",
    "Slack ucar, spreadsheet kalir, {links_len} linkinizi {channel_name}'ten corladim",
    "{channel_name}'e {links_len} link aticaginiza biraz calisin be, valla biktim",
    "Mesajlarimin hepsi komikli degil, bu da onlardan biri. {channel_name}'ten {links_len} link, allah bereket versin!",
]


def log(msg):
    client.chat_postMessage(channel="#bot_log", text=msg)


def mark_message(channel_id, msg_ts):
    client.reactions_add(name="eyes", channel=channel_id, timestamp=msg_ts)


def recursive_link_type_finder(raw_blocks):
    if isinstance(raw_blocks, list):
        for item in raw_blocks:
            link = recursive_link_type_finder(item)
            if link:
                return link
    else:
        if raw_blocks.get("type") == "link":
            return raw_blocks["url"]
        for k, v in raw_blocks.items():
            if isinstance(v, dict):
                return recursive_link_type_finder(v)
            elif isinstance(v, list):
                for item in v:
                    link = recursive_link_type_finder(item)
                    if link:
                        return link


def filter_link_messages(raw_messages, channel_id):
    result = []
    for m_obj in raw_messages:
        if m_obj["type"] == "message" and "subtype" not in m_obj:
            attachments = m_obj.get("attachments")
            link = None
            title = None
            if attachments:
                if isinstance(attachments, dict):
                    title = attachments["title"]
                    link = attachments["title_link"]
                elif isinstance(attachments, list):
                    for attch in attachments:
                        if "title" in attch and "title_link" in attch:
                            title = attch["title"]
                            link = attch["title_link"]
            elif "blocks" in m_obj:
                link = recursive_link_type_finder(m_obj["blocks"])

            if link:
                msg_ts = m_obj["ts"]
                user_id = m_obj["user"]
                try:
                    mark_message(channel_id, msg_ts)
                except SlackApiError:
                    pass
                result.append((user_id, float(msg_ts), title, link))
    return result


def add_links_to_sheet(links, channel_name):
    today_start = datetime.today().replace(minute=0, hour=0, second=0, microsecond=0)
    inserted_link_count = 0
    user_map = {}
    links.sort(key=lambda tup: tup[1])
    for user_id, msg_ts, title, link in links:
        pinned_at = datetime.fromtimestamp(msg_ts)
        if pinned_at > today_start:
            username = user_map.get(user_id)
            if not username:
                username = user_map[user_id] = client.users_info(user=user_id)["user"]["profile"]["display_name"]
            pinned_at = pinned_at.strftime("%d/%m/%Y %H:%M:%S")
            pins_sheet.append([pinned_at, title, link, username], subsheet=channel_name)
            inserted_link_count += 1
    return inserted_link_count


def collect_target_channel_links():
    try:
        log("Hype Belediyesi is basinda! Hadi bugun ne bos linkler atmissiniz bakiyim")
        convs = client.conversations_list()
        channels = convs.data["channels"]
        for channel in channels:
            channel_name = channel["name"]
            if channel_name in LINK_CURATE_CHANNELS_NAMES:
                channel_id = channel["id"]
                channel_history = client.conversations_history(channel=channel_id)
                links = filter_link_messages(channel_history.data["messages"], channel_id)
                count = add_links_to_sheet(links, channel_name)
                if count:
                    log(
                        random.choice(IS_BITINCE_KOMIKLIKLER_SAKALAR).format(channel_name=channel_name, links_len=count)
                    )
                else:
                    log("Bisey yokmus, iyi calisin aferin")
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
        print(e.response)
