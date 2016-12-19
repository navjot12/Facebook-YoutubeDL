#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
import os
import sys
import time
import requests
import pafy

VERIFY_TOKEN = 'youtube-download-karega'
PAGE_ACCESS_TOKEN = 'EAAO5LXdwYSwBADZClxlG8zxcgHdcmzhr87ZC6H3wvWQyypX1666JRcEJwhIk830av89OGoqtkogM0tJS74vQElsMyaKo9i1lG5J0GIAF9nfFQiSeyxjkkWJDRX8ZBdYeFujPujW7DRCjzZA8XGuN7d6o1SbXYLPZBa4kvForUJgZDZD'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '/credentials')
    credential_path = os.path.join(credential_dir,'drive-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    return credentials

def set_greeting_text():
	post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%PAGE_ACCESS_TOKEN
	response_msg = {
		"setting_type":"greeting",
		"greeting":{
			"text":"Just enter the youtube url you wish to download!"
		}
	}
	response_msg = json.dumps(response_msg)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
	print status

def post_facebook_quickreply(fbid, url):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg_quickreply = {
		"recipient":{
	  		"id":fbid
		},
		"message":{
			"text":"What would you like to download?",
		    "quick_replies":[
			    {
			    	"content_type":"text",
			        "title":'Audio',
			        "payload":'audio!$#@' + url
			    },
			    {
				    "content_type":"text",
			    	"title":'Video',
			    	"payload":'video!$#@' + url
			    }
		    ]
		}
	}
	response_msg_quickreply = json.dumps(response_msg_quickreply)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_quickreply)
	print status.json()

def handle_quickreply(sender_id, payload):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	url = payload.split('!$#@')[1]
	video = pafy.new(url)
	best = video.getbest()
	message_text = video.title + '\t(' + video.duration + ')'
	post_facebook_message(sender_id, message_text)
	
	if payload.split('!$#@')[0] == 'video':
		r = requests.get('http://tinyurl.com/api-create.php?url=' + best.url)
		post_facebook_video(sender_id, url)
		message_text = 'Download Video: ' + str(r.text)
		post_facebook_message(sender_id, message_text)
		message_text = 'Open the link, right click on the video to save it.'
		post_facebook_message(sender_id, message_text)

	elif payload.split('!$#@')[0] == 'audio':
		bestaudio = video.getbestaudio(preftype="m4a")
		r = requests.get('http://tinyurl.com/api-create.php?url=' + bestaudio.url)
		post_facebook_audio(sender_id, bestaudio.url)
		message_text = 'Download Audio: ' + str(r.text)
		post_facebook_message(sender_id, message_text)
		message_text = 'Open the link, right click on the audio and while saving, rename it to (anything).m4a.\nNOTE: You could also save with .mp3 extension, but m4a provides better quality!'
		post_facebook_message(sender_id,message_text)
		#post_facebook_file(sender_id, url, video.title)
	
	return

def post_facebook_message(fbid, message_text):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg = {
		"recipient":{
			"id":fbid
		},
		"message":{
			"text":message_text
		}
	}
	response_msg = json.dumps(response_msg)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
	print status.json()

def post_facebook_audio(fbid, url):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

	response_msg_audio = {
		"recipient":{
			"id":fbid
		},
		"message":{
			"attachment":{
		    	"type":"audio",
		    	"payload":{
		        	"url": url
		      	}
		    }
		}
	}
	response_msg_audio = json.dumps(response_msg_audio)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_audio)
	print status

'''def post_facebook_file(fbid, url, title):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	title = title.split('|')[0].split('(')[0].split('.')[0].strip()
	title = title.replace(' ', '_').replace('\'', '')
	title = title + '.mp3'
	print '-----' + title + '-----'
	cmd = 'youtube-dl --extract-audio --audio-format mp3 --audio-quality 0 --output \"' + title + '\" ' + url
	os.system(cmd)

	credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)


	os.system('git init')
	os.system('git config user.email \"singh_navjot75@yahoo.ca\"')
	os.system('git config user.name \"Navjot Singh\"')
	os.system('git add '+title)
	os.system('git commit -m \"'+fbid+' downloaded '+title+'\"')
	os.system('git remote add origin git+ssh://git@github.com:NSingh12/music.git')
	os.system('git push origin master')
	#os.system('NSingh12')
	#os.system('dtu/2k14/mc/045')
	
	response_msg_file = {
		"recipient":{
			"id": fbid
		},
		"message":{
			"attachment":{
				"type":"file",
				"payload":{
					"url":"https://raw.githubusercontent.com/NSingh12/music/master/"+title
				}
			}
		}
	}
	os.system('rm '+title)
	os.system('rm -rf .git')
	
	response_msg_file = json.dumps(response_msg_file)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_file)
	print status

	files = {
		'recipient':{
			"id":fbid
		},
		'message':{
			"attachment":{
				"type":"file",
				"payload":{}
			}
		},
		'filedata':str(open(title, 'rb'))
	}

	print '\n*********\n' + str(files) + '\n*********\n'
	status = requests.get(post_message_url, files=files)
	print status'''

def post_facebook_video(fbid, url):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg_video = {
		"recipient":{
			"id":fbid
		},
		"message":{
			"attachment":{
				"type":"video",
				"payload":{
					"url":url
				}
			}
		}
	}
	response_msg_video = json.dumps(response_msg_video)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_video)
	print status

class MyChatBotView(generic.View):
	def get (self, request, *args, **kwargs):
		if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
			return HttpResponse(self.request.GET['hub.challenge'])
		else:
			return HttpResponse('Invalid token.')

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return generic.View.dispatch(self, request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		incoming_message= json.loads(self.request.body.decode('utf-8'))
		print incoming_message

		for entry in incoming_message['entry']:
			for message in entry['messaging']:
				sender_id = message['sender']['id']
				try:
					if 'quick_reply' in message['message']:
						handle_quickreply(sender_id, message['message']['quick_reply']['payload'])
						continue
					else:
						pass
				except Exception as e:
					print e
					pass
				
				try:
					if 'text' in message['message']:
						message_text = message['message']['text']
						words = message_text.split(' ')
						flag_URL = 0
						flag_AV = 0
						url = ''
						AV = ''

						for word in words:
							if word.startswith('https://') or word.startswith('www.') or word.startswith('youtu'):
								flag_URL = 1
								url = word
							if word.lower() in ['audio','video']:
								flag_AV = 1
								AV = word.lower()

						if flag_URL == 0:
							message_text = 'Please enter a valid video link to download.'
							post_facebook_message(sender_id, message_text)

						elif flag_URL == 1 and flag_AV == 0:
							post_facebook_quickreply(sender_id, url)

						elif flag_URL == 1 and flag_AV == 1:
							payload = AV + '!$#@' + url
							handle_quickreply(sender_id, payload)

					else:
						pass

				except Exception as e:
					print e
					pass

		return HttpResponse()

def index(request):
	set_greeting_text()
	return HttpResponse('Building Youtube Downloader Bot!')