from utils.client import client


def channel_name_from_id(channel_id: str):
    return client.conversations_info(channel=channel_id)["channel"]["name"]
