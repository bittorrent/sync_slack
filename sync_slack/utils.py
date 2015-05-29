#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from sync_slack import config


def get_folder_name(folder_id):
    '''
    Get a sync folder name based on folder id.
    '''
    res = requests.get('%s/folders/%s' % (config.SYNC_API_BASE_URL, folder_id))
    folder_name = res.json().get('data').get('name')
    return folder_name


def get_folders():
    '''
    Get all sync folders
    '''
    res = requests.get('%s/folders' % config.SYNC_API_BASE_URL)
    folders = res.json().get('data').get('folders')
    return folders


def send_message(channel, message):
    '''
    Post a message to Slack channel.
    '''
    headers = { 'Content-type': 'application/json' }
    payload = { 'channel': channel, 'text': message }
    requests.post(config.SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)


def poll_for_events(channel, folder_id):
    '''
    Long poll the api for events and post a message to Slack channel.
    Only handles a few folder events (files added/removed).
    For full list of events, refer to api documentation
    '''
    last_event_id = -1
    while True:
        try:
            res = requests.get('%s/events?id=%s' % (config.SYNC_API_BASE_URL, last_event_id))
            events = res.json().get('data').get('events')

            # Sort events by id. We want lowest id (earliest) events first so they process first
            # By default we are returned highest id (most current) events
            sorted_events = sorted(events, key=lambda k: k['id'], reverse=False)

            for event in sorted_events:
                event_type = event.get('typename')
                event_id = event.get('id')

                # File added to folder
                if event_type in ['EVENT_LOCAL_FILE_ADDED', 'EVENT_REMOTE_FILE_ADDED']:
                    file_name = event.get('path')
                    folder_name = event.get('folder').get('name')
                    event_folder_id = event.get('folder').get('id')
                    if event_folder_id == folder_id:
                        send_message(channel, 'File "%s" added to folder "%s"' % (file_name, folder_name))

                # File removed from folder
                if event_type in ['EVENT_LOCAL_FILE_REMOVED', 'EVENT_REMOTE_FILE_REMOVED']:
                    file_name = event.get('path')
                    folder_name = event.get('folder').get('name')
                    event_folder_id = event.get('folder').get('id')
                    if event_folder_id == folder_id:
                        send_message(channel, 'File "%s" removed from folder "%s"' % (file_name, folder_name))

                # Set highest event id (most recent event) to last_event_id so we don't get duplicates
                if event_id > last_event_id:
                    last_event_id = event_id

        except Exception as e:
            print 'Error %s' % e
            # pass
