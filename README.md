# URLtoQR

A Slack app that returns a QR code when you send a URL.

## Overview

There are many easy ways to create QR codes these days. This app is intended for cases where you want to make a small number of QR codes and share them easily with others. If you need to generate many ones at once, it is better to use a script and share them from cloud service, but for a few URLs that process can be tedious (create → upload → share).

This Slack app generates a QR code when you send a URL with the following two usage modes:
1. Send a URL with the slash command, the app will DM you the QR code.
2. Mention the app in a channel with a URL, the app replies in thread with the QR code.

The first mode is for private use, the second is for sharing with others.

## Environment

- Python 3.11 or later
- Slack app configuration (Bot Token, Signing Secret)
- Socket mode configuration (App Token)
  - If using HTTP mode locally, make the app reachable from Slack (e.g. with ngrok)

## Setup

### Clone the repository

```bash
git clone https://github.com/misgnros/urltoqr
cd urltoqr
```

### Dependencies

Install dependencies according to your environment. The project relies on:

- `qrcode>=8.2` : QR code generation
- `slack-bolt>=1.26.0` : Slack Bolt framework
- `slack-sdk>=3.37.0` : Slack SDK

### Environment variables

Set the following environment variables:

- `SLACK_BOT_TOKEN`: the Bot User OAuth Token for your Slack app
- `SLACK_SIGNING_SECRET`: the Signing Secret for your Slack app
- `SLACK_APP_TOKEN`: the App Token for Socket mode (If needed)
- `PORT`: optional — port for the app to listen on (default: 3000)

### Slack app configuration

1. Create an app at the Slack API: https://api.slack.com/apps
2. Add the following Bot Token scopes:
   - `app_mentions:read`
   - `chat:write`
   - `commands`
   - `files:write`
   - `im:write`
3. Register the slash command `/qr`.
4. Enable Event Subscriptions and subscribe to the `app_mentions` event.
5. If using Socket mode, setup according to https://docs.slack.dev/tools/java-slack-sdk/guides/socket-mode/. Or running locally in HTTP mode, expose your local server (for example using ngrok) and set the Request URL accordingly in Slack.

### Starting the app

```bash
python3 URLtoQR.py
```

## Usage

The app interprets a URL as a string starting with `http...`. Any other string will not be treated as a URL and an error message will be returned.

### Slash command

Use the slash command `/qr` followed by a URL. The app will send you a DM with a QR code for the URL.

### Mention

Add the app to a channel and mention it with a URL in the message. The app will reply in the thread with the QR code.
