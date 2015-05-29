#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import json

from multiprocessing import Process
from flask import Flask, request
from sync_slack.utils import poll_for_events, send_message, get_folder_name, get_folders

app = Flask(__name__)
app.config.from_object('sync_slack.config')

processes = {}

@app.route('/folder/start', methods=['POST'])
def start_folder_watch():
    '''
    Start watching a sync folder for changes.
    This will spawn a separate process that polls the api for events.
    '''
    # Verify request comes from your Slack slash command
    token = request.form.get('token', None)
    if not token or token != config.SLACK_WATCH_TOKEN:
        return 'Error: Invalid token'

    # Channel id should always come in from Slack slash command
    channel_id = request.form.get('channel_id', None)
    if not channel_id:
        return 'Error: Missing channel id'

    folder_id = request.form.get('text', None)
    if not folder_id:
        return 'Error: Missing folder id argument'

    channel_folder_hash = '%s_%s' % (channel_id, folder_id)

    if channel_folder_hash in processes:
        return 'Error: Already watching folder "%s" in current channel' % folder_id

    p = Process(target=poll_for_events, args=(channel_id, folder_id))
    p.start()
    processes[channel_folder_hash] = p

    folder_name = get_folder_name(folder_id)
    send_message(channel_id, "Watching for changes to folder '%s'"% folder_name)
    return ''


@app.route('/folder/stop', methods=['POST'])
def stop_folder_watch():
    '''
    Stop watching a sync folder for changes.
    Terminates existing process that is polling the api for events.
    '''
    # Verify request comes from your Slack slash command
    token = request.form.get('token', None)
    if not token or token != config.SLACK_STOP_TOKEN:
        return 'Error: Invalid token'

    # Channel id should always come in from Slack slash command
    channel_id = request.form.get('channel_id', None)
    if not channel_id:
        return 'Error: Missing channel id'

    folder_id = request.form.get('text')
    if not folder_id:
        return 'Error: Missing folder id argument'

    channel_folder_hash = '%s_%s' % (channel_id, folder_id)

    if not processes.get(channel_folder_hash, None):
        return 'Error: Not watching folder "%s" in current channel' % folder_id

    processes[channel_folder_hash].terminate()
    processes.pop(channel_folder_hash, None)

    folder_name = get_folder_name(folder_id)
    send_message(channel_id, "Stop watching folder '%s'" % folder_name)
    return ''


@app.route('/folders', methods=['POST'])
def list_folders():
    '''
    Posts a message to Slack channel with list of sync folders and
    their corresponding id.
    '''
    # Verify request comes from your Slack slash command
    token = request.form.get('token', None)
    if not token or token != config.SLACK_LIST_TOKEN:
        return 'Error: Invalid token'

    # # Channel name should always come in from Slack slash command
    channel_id = request.form.get('channel_id', None)
    if not channel_id:
        return 'Error: Missing channel id'

    folders = get_folders()

    # Format display message nicely
    message = '*Folder List*\n'
    for f in folders:
        message += '%s: %s\n' % (f['name'], f['id'])

    send_message(channel_id, message)
    return ''


if __name__ == '__main__':
    app.run()
