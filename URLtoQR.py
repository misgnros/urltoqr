import os
import qrcode
import io
import re
import logging
from urllib.parse import urlparse
from slack_bolt import App
from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler # For Socket Mode

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load Slack token and signing secret from environment variables
# Exit if not found
try:
    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
except KeyError as e:
    logger.error(f"Environment variable {e} is not set. Exiting application.")
    exit(1)

app = App(token=slack_bot_token, signing_secret=slack_signing_secret)


def extract_and_validate_url(text: str) -> str | None:
    """
    Extracts and performs basic validation on a URL from the given text.
    Returns a valid URL with http or https scheme, or None.
    """
    match = re.search(r"<?(https?://[^\s>]+)>?", text)
    if match:
        url = match.group(1)
        parsed_url = urlparse(url)
        if parsed_url.scheme in ["http", "https"] and parsed_url.netloc:
            return url
    return None


def generate_qr(url: str) -> io.BytesIO:
    """
    Generates a QR code for the given URL and returns it as a PNG byte stream.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    logger.info(f"Generated QR code for: {url}")
    return buffer


@app.event("app_mention")
def reply_qr(event: dict, client: WebClient, say):
    """
    Generates a QR code and replies when the app is mentioned.
    """
    msg_text = event["text"]
    channel = event["channel"]
    thread_ts = event["ts"]
    user_id = event["user"]  # User ID who mentioned the app

    logger.info(
        f"Received app_mention event. User: {user_id}, Channel: {channel}, Message: {msg_text}"
    )

    url = extract_and_validate_url(msg_text)
    if url:
        try:
            buffer = generate_qr(url)
            client.files_upload_v2(
                channel=channel, file=buffer, title="image.png", thread_ts=thread_ts
            )
            logger.info(f"Uploaded QR code to channel {channel}.")
        except Exception as e:
            logger.error(f"Error during app_mention processing: {e}", exc_info=True)
            say(
                channel=channel,
                text=f"ERROR: An error occurred while generating or uploading the QR code: {e}",
                thread_ts=thread_ts,
            )
    else:
        say(
            channel=channel,
            text="ERROR: Please enter a valid URL. Check your message:\n> " + msg_text,
            thread_ts=thread_ts,
        )


@app.command("/qr")
def slash_qr(ack, command: dict, client: WebClient):
    """
    Generates a QR code and sends it via DM when the /qr slash command is executed.
    """
    ack()  # Acknowledge the command
    msg_text = command["text"].strip()
    user_id = command["user_id"]

    logger.info(f"Received /qr command. User: {user_id}, Command text: {msg_text}")

    try:
        dm_response = client.conversations_open(users=user_id)
        dm_channel_id = dm_response["channel"]["id"]
    except Exception as e:
        logger.error(
            f"Could not open DM channel for user {user_id}: {e}", exc_info=True
        )
        return

    url = extract_and_validate_url(msg_text)
    if url:
        try:
            buffer = generate_qr(url)
            client.files_upload_v2(
                channel=dm_channel_id,
                file=buffer,
                title="image.png",
            )
            logger.info(f"Sent QR code via DM to user {user_id}.")
        except Exception as e:
            logger.error(f"Error during /qr command processing: {e}", exc_info=True)
            client.chat_postMessage(
                channel=dm_channel_id,
                text=f"ERROR: An error occurred while generating or uploading the QR code: {e}",
            )
    else:
        client.chat_postMessage(
            channel=dm_channel_id,
            text="ERROR: Please enter a valid URL. Check your message:\n> " + msg_text,
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    logger.info(f"Starting Bolt app on port {port}.")
    try:
        # Start in Socket Mode if SLACK_APP_TOKEN is provided, otherwise use HTTP mode.
        # This avoids attempting to start both modes at the same time.
        if "SLACK_APP_TOKEN" in os.environ:
            logger.info("SLACK_APP_TOKEN detected — starting in Socket Mode.")
            SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
        else:
            logger.info("SLACK_APP_TOKEN not found — starting in HTTP mode.")
            app.start(port=port)
    except KeyError:
        logger.error(
            "Environment variable SLACK_APP_TOKEN is not set. It is required for Socket Mode."
        )
        logger.info("Starting in HTTP mode.")
        app.start(port=port)
    except Exception as e:
        logger.critical(
            f"A fatal error occurred during application startup: {e}", exc_info=True
        )
