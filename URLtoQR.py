from slack_bolt import App
import qrcode
import io
import re

# Enter your Slack app token and signing secret here
app = App(
	token="*****",
	signing_secret="*****"
)

@app.event("app_mention")
def reply_qr(event,client,say):
	msg_text=event["text"]
	channel = event["channel"]
	thread_ts = event["ts"]

	include_url=re.search(r".+\s<\s*(http.+)\s*>",msg_text)
	if include_url is not None:
		url=include_url.group(1)
		buffer=generate_qr(url)

		client.files_upload_v2(
			channel=channel,
			file=buffer,
			title="image.png",
			thread_ts=thread_ts
		)
	else:
		say(
			channel=channel,
			text="ERROR: Please enter a URL. Check your message:\n> " + msg_text,
			thread_ts=thread_ts
		)

@app.command("/qr")
def slash_qr(ack, command, client):
	ack()

	msg_text = command["text"].strip()
	user_id = command["user_id"]

	include_url=re.search(r"\s*(http.+)\s*",msg_text)
	if include_url is not None:
		buffer = generate_qr(msg_text)
		
		dm_response = client.conversations_open(users=user_id)
		dm_channel_id = dm_response["channel"]["id"]
		
		client.files_upload_v2(
			channel=dm_channel_id,
			file=buffer,
			title="image.png",
		)
	else:
		client.conversations_open(users=user_id)
		dm_channel_id = client.conversations_open(users=user_id)["channel"]["id"]
		client.chat_postMessage(
			channel=dm_channel_id,
			text="ERROR: Please enter a URL. Check your message:\n> " + msg_text,
		)

def generate_qr(url):
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=10,
		border=4,
	)
	qr.add_data(url)
	qr.make(fit=True)

	img = qr.make_image(fill_color="black", back_color="white")
	buffer = io.BytesIO()
	img.save(buffer, format="PNG")
	buffer.seek(0)

	return buffer

if __name__ == "__main__":
	# Enter your port number here
	app.start(port=3000)
	print("Bolt app is running!")
