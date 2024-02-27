import json
import logging
import os

from slack_bolt import App, BoltContext, Complete, Fail
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore

app = App(
    attaching_function_token_enabled=False,
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    oauth_settings=OAuthSettings(
        client_id=os.environ["SLACK_CLIENT_ID"],
        client_secret=os.environ["SLACK_CLIENT_SECRET"],
        user_scopes=["chat:write"],
    ),
)
logging.basicConfig(level=logging.INFO)


@app.function("sample_function")
def handle_sample_function_event(
    context: BoltContext, inputs: dict, complete: Complete, fail: Fail, client: WebClient, logger: logging.Logger
):
    user_id = inputs["user_id"]

    installation = app.installation_store.find_installation(
        enterprise_id=context.enterprise_id, team_id=context.team_id, user_id=user_id
    )
    user_client = WebClient(token=installation.user_token)
    try:
        response = user_client.chat_postMessage(
            as_user=True,
            channel=os.environ["SLACK_CHANNEL"],
            text="Click button to complete function!",
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Hello from impersonated user"},
                }
            ],
        )
        logger.info(response.status_code)
        logger.info(json.dumps(response.data))
        complete({"user_id": user_id})
    except Exception as e:
        logger.exception(e)
        fail(f"Failed to handle a function request (error: {e})")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).connect()
    app.start()
