import datetime
import os

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient

import config as cfg
import image as im
from sheets import Sheet as pins_sheet
from utils.bolt_utils import channel_name_from_id
from utils.mention_helper import handle_mention
from views import root_bp

app = App(token=cfg.token, signing_secret=cfg.secret, process_before_response=True)
flask_app = Flask(__name__)
flask_app.register_blueprint(root_bp)
handler = SlackRequestHandler(app)


@app.middleware
def break_retry(logger, body, next):
    retry = request.headers.environ.get("HTTP_X_SLACK_RETRY_NUM", 0)
    if not retry:
        return next()


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@app.event("file_shared")
def file_shared(body, client: WebClient, context, logger):
    context.ack()
    file_id = body["event"]["file_id"]
    file_info = client.files_info(file=file_id)

    file_type = file_info["file"]["filetype"]
    if file_type not in ["jpg", "jpeg", "png"]:
        return

    url = file_info["file"]["url_private"]

    image = im.open_url(url, cfg.token)

    sides = ["left", "right"]
    uploaded_files = {}
    for side in sides:
        mirrored = im.mirror(image, side=side)
        mirrored.save(f"/tmp/{file_id}-{side}.{file_type}")

        with open(f"/tmp/{file_id}-{side}.{file_type}", "rb") as file_content:
            result = client.files_upload(file=file_content)
            uploaded_files[side] = result["file"]["permalink"]

    msg = f"<{uploaded_files['right']}| ><{uploaded_files['left']}| >"

    channel_name = channel_name_from_id(body["event"]["channel_id"])
    channel = "sapsik"
    if channel_name == "bot_testing":
        channel = channel_name

    sent = client.chat_postMessage(text=msg, channel=channel)
    for side in sides:
        try:
            client.reactions_add(channel=sent["channel"], timestamp=sent["ts"], name=f"point_{side}")
        except SlackApiError:
            pass


@app.event("pin_added")
def pin_added(body, client, context, logger):
    context.ack()
    event = body["event"]
    channel_id = event["channel_id"]
    channel_name = client.conversations_info(channel=channel_id)["channel"]["name"]
    pinned_at = datetime.datetime.fromtimestamp(event["item"]["created"])
    pinned_at = pinned_at.strftime("%d/%m/%Y %H:%M:%S")
    message = event["item"]["message"]["text"]
    message_by = client.users_info(user=event["item"]["message"]["user"])
    message_username = message_by["user"]["profile"]["display_name"]
    permalink = event["item"]["message"]["permalink"]

    row = [pinned_at, channel_name, message_username, message, permalink]

    pins_sheet.append(row)


@app.event("app_mention")
def handle_mentions(event, client, say):
    channel = event["channel"]
    thread_ts = event["thread_ts"]
    thread = client.conversations_replies(ts=thread_ts, channel=channel)
    handle_mention(event, thread)


# Only for local debug
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
