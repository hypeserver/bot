import os
from slack_bolt import App

import image as im

token = os.environ.get("SLACK_BOT_TOKEN")
secret = os.environ.get("SLACK_SIGNING_SECRET")

app = App(
    token=token,
    signing_secret=secret
)

@app.event('file_shared')
def file_shared(body, client, context, logger):
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


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))


