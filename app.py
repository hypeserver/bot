import os
import datetime

from slack_bolt import App

import image as im
from sheets import Sheet as pins_sheet

token = os.environ.get("SLACK_BOT_TOKEN")
secret = os.environ.get("SLACK_SIGNING_SECRET")

app = App(
    token=token,
    signing_secret=secret
)

@app.event('file_shared')
def file_shared(body, client, context, logger):
    print(client)
    file_id = body["event"]["file_id"]
    file_info = client.files_info(file=file_id)

    if file_info['file']['filetype'] not in ['jpg']:
        return

    url = file_info['file']['url_private']

    image = im.open_url(url, token)

    mirrored = im.mirror(image)
    mirrored.save('/tmp/%s.jpg'%file_id)

    with open('/tmp/%s.jpg'%file_id, 'rb') as file_content:
        response = client.files_upload(
            file=file_content,
            channels="sapsik"
            )

@app.event('pin_added')
def pin_added(body, client, context, logger):
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

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))


