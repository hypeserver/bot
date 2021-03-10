import os
import datetime

from slack_bolt import App
from utils.link_helper import collection_links
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

import image as im
from sheets import Sheet as pins_sheet
import config as cfg

app = App(
    token=cfg.token,
    signing_secret=cfg.secret,
    process_before_response=True
)
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/tasks/link-collector", methods=["POST"])
def collect_liks_view():
    collection_links()
    return {}

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@app.middleware
def break_retry(logger, body, next):
    retry = request.headers.environ.get('HTTP_X_SLACK_RETRY_NUM', 0)
    if not retry:
        return next()

@app.event('file_shared')
def file_shared(body, client, context, logger):
    context.ack()

    file_id = body["event"]["file_id"]
    file_info = client.files_info(file=file_id)

    file_type = file_info['file']['filetype']
    if file_type not in ['jpg', "png"]:
        return

    url = file_info['file']['url_private']

    image = im.open_url(url, cfg.token)

    mirrored = im.mirror(image)
    mirrored.save(f"/tmp/{file_id}.{file_type}")

    with open(f"/tmp/{file_id}.{file_type}", 'rb') as file_content:
        response = client.files_upload(
            file=file_content,
            channels="sapsik"
        )

@app.event('pin_added')
def pin_added(body, client, context, logger):
    context.ack()
    event = body['event']
    channel_id = event['channel_id']
    channel_name = client.conversations_info(channel=channel_id)['channel']['name']
    pinned_at = datetime.datetime.fromtimestamp(event['item']['created'])
    pinned_at = pinned_at.strftime('%d/%m/%Y %H:%M:%S')
    pinned_by = event['user']
    pinned_by = client.users_info(user=event['user'])
    message = event['item']['message']['text']
    message_by = client.users_info(user=event['item']['message']['user'])
    message_username = message_by['user']['profile']['display_name']
    permalink = event['item']['message']['permalink']
    message_type = event['item']['message']['type']

    row = [pinned_at, channel_name, message_username, message, permalink]

    pins_sheet.append(row)

# Only for local debug
if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))

