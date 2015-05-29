# Sync sample integration with Slack

### Setup BitTorrent Sync
You need to have Sync with API v2 support installed. For more instructions on getting setup, click [here](https://github.com/bittorrent/sync_api_sample/blob/master/README.md).

### Setup Slack [Incoming Webhook](https://api.slack.com/incoming-webhooks)
This is used to post messages to Slack channels.

Go to your Slack integrations page and add a new Incoming Webhook. Use the following settings:
- **Post to Channel**: This can be set to any channel. We override this value.
- **Webhook Url**: This value needs to be copied to the SLACK_WEBHOOK_URL variable in config.py
- **Customize Name**: Sync (or whatever you wish to call this bot)
- **Customize Icon**: Anything you want, or you can use [this](https://s3-us-west-2.amazonaws.com/slack-files2/avatars/2015-05-22/5004574340_d2a19e84c39c02d57303_48.jpg).


### Setup [ngrok](https://ngrok.com/)
Ngrok allows you to expose your local webserver to the internet. We need this because our sample app will be running on localhost and this does not work well with Slack Slash Commands (next step).

Set up ngrok using [this](https://ngrok.com/docs#expose). We need to route our local 80 port. Once it is up and running you should get a forwarding address. ` http://92832de0.ngrok.io -> localhost:80` Take note of this, we will need it in the next step.


### Setup Slack [Slash Commands](https://bittorrent.slack.com/services/new/slash-commands)
Slash Commands allow you to listen for custom triggers in chat messages across all Slack channels. When a Slash Command is triggered, relevant data will be sent to an external URL in real-time. 

Go to your Slack integrations page and add a new Slash Command. We need to setup 3 in total and they are all very similar:
- **Command**: /sync-watch, /sync-stop, /sync-list (these are each a separate slash command).
- **URL**: the ngrok address you setup in the previous setup (i.e. http://92832de0.ngrok.io). The reason we need a public url is because slash commands currently need to recieve a 200 response from the URL they are posting to, so we need our script running on a publicly accessible server. Note: When restarting ngrok, it is possible the address will change, which can be annoying since you would need to update all your slash commands. You can setup custom reserved domains, but this requires a ngrok paid plan.
- **Token**: This needs to be copied to the variables in config.py. /sync-watch -> SLACK_WATCH_TOKEN, /sync-stop -> SLACK_STOP_TOKEN, /sync-list -> SLACK_LIST_TOKEN


### Usage 
Now we are ready to try out our new integration. Startup BitTorrent Sync, Slack, and run this sync_slack server (runserver.py).
From your Slack channel, you can now use the slash commands.

**/sync-list** - Print out a list of your Sync folders

**/sync-watch [folder_id]** - Start watching for changes to Sync folder. Sample app only supports files added/removed. When one of these events happen, a message should be posted into the Slack channel

**/sync-stop [folder_id]** - Stop watching for changes to Sync folder.
