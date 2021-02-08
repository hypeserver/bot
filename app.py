import os
from slack_bolt import App

import image as im

token = os.environ.get("SLACK_BOT_TOKEN")
secret = os.environ.get("SLACK_SIGNING_SECRET")

# Initializes your app with your bot token and signing secret
app = App(
    token=token,
    signing_secret=secret
)

@app.event('file_shared')
def file_shared(body, client, context, logger):
    print('file_shared')
    file_id = body["event"]["file_id"]
    file_info = client.files_info(file=file_id)

    if file_info['file']['filetype'] not in ['jpg']:
        return

    url = file_info['file']['url_private']
    print('opening remote image')
    image = im.open_url(url, token)
    print('mirroring image')
    mirrored = im.mirror(image)
    mirrored.save('/tmp/%s.jpg'%file_id)
    print('image_saved')
    with open('/tmp/%s.jpg'%file_id, 'rb') as file_content:
        response = client.files_upload(file=file_content,
                channels="sapsik"
            )
    print(response)


from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# Only for local debug
if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))