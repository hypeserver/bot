import os
from slack_bolt import App

from handlers import file_shared

token = os.environ.get("SLACK_BOT_TOKEN")
secret = os.environ.get("SLACK_SIGNING_SECRET")

app = App(
    token=token,
    signing_secret=secret
)

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))