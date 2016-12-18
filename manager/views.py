#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import sys
import time
import requests
import pafy

VERIFY_TOKEN = 'youtube-download-karega'
PAGE_ACCESS_TOKEN = 'EAAO5LXdwYSwBAFNtQwyXBAgswtxV9wVMQMoUO887BT4dE8qFykRoyqEftoe2GHJe35HuLHL8ZAPmWWoW4evqBTO6cYUdFO7CYqKtyBLXvMrIxApNQe5iZBRmC3S6g0HEZBKOwzZAG0OXSrcZBGMcBlEHtKO57ownY3cDvAYMevwZDZD'

'''def set_greeting_text():
	post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%PAGE_ACCESS_TOKEN
	response_msg = {
		"setting_type":"greeting",
		"greeting":{
			"text":"This chatbot allows you to download youtube videos in the best quality!\nJust paste the url of a youtube video to download it's audio. Or enter \"<video url> video\" to download the video."
		}
	}
	response_msg = json.dumps(response_msg)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
	print status
'''

def post_facebook_quickreply(fbid, url):
	post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%PAGE_ACCESS_TOKEN
	response_msg_quickreply = {
		"setting_type" : "call_to_actions",
		"thread_state":"new_thread",
		"call_to_actions":[
			"recipient":{
			    "id":fbid
			},
			"message":{
				"text":"What would you like to download?",
			    "quick_replies":[
			    {
			    	"content_type":"text",
			        "title":'Audio',
			        "payload":'Audio :' + url
			    },
			    {
				    "content_type":"text",
			    	"title":'Video',
			    	"payload":'Video :' + url
			    }
			    ]
			}
		]
	}
	response_msg_quickreply = json.dumps(response_msg_quickreply)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_quickreply)
	print status.json()

def handle_quickreply(fbid, payload):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	url = payload.split(':')[1]
	video = pafy.new(url)
	best = video.getbest()
	message_text = video.title + '\t(' + video.duration + ')'
	post_facebook_message(sender_id,message_text)
	
	if payload.split(':')[0] == 'Video':
		r = requests.get('http://tinyurl.com/api-create.php?url=' + best.url)
		message_text = 'Download Video: ' + str(r.text)
		post_facebook_message(sender_id, message_text)
		message_text = 'Open the link, right click on the video to save it.'
		post_facebook_message(sender_id,message_text)
		#post_facebook_video(sender_id, best.url)
		post_facebook_file(sender_id, best.url)
	
	elif payload.split(':')[0] == 'Audio':
		bestaudio = video.getbestaudio(preftype="m4a")
		r = requests.get('http://tinyurl.com/api-create.php?url=' + bestaudio.url)
		post_facebook_audio(sender_id, bestaudio.url)
		message_text = 'Download Audio: ' + str(r.text)
		post_facebook_message(sender_id,message_text)
		message_text = 'Open the link, right click on the audio and while saving, rename it to (anything).m4a.\nNOTE: You could also save in .mp3 extension, but m4a provides better quality!'
		post_facebook_message(sender_id,message_text)
		post_facebook_file(sender_id, bestaudio.url)
	
	return

def post_facebook_message(fbid, message_text):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":message_text}})
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
	print status.json()

def post_facebook_audio(fbid, message_text):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

	response_msg_audio = {
		"recipient":{
			"id":fbid
		},
		"message":{
			"attachment":{
		    	"type":"audio",
		    	"payload":{
		        	"url":message_text
		      	}
		    }
		}
	}
	response_msg_audio = json.dumps(response_msg_audio)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_audio)
	print status

def post_facebook_file(fbid, message_text):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

	response_msg_file = {
		"recipient":{
			"id":fbid
		},
		"message":{
			"attachment":{
				"type":"file",
				"payload":{
					"url":"https://petersapparel.com/bin/receipt.pdf"
				}
			}
		}
	}
	response_msg_file = json.dumps(response_msg_file)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_file)
	print status

'''def post_facebook_video(fbid, message_text):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg_video = {
		"recipient":{
			"id":fbid
		},
		"message":{
			"attachment":{
				"type":"video",
				"payload":{
					"url":message_text
				}
			}
		}
	}
	response_msg_video = json.dumps(response_msg_video)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_video)
	print status'''

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
					else:
						pass
				except Exception as e:
					print e
					pass
				
				try:
					message_text = message['message']['text']

					words = message_text.split(' ')
					flag_URL = 0

					for word in words:
						if word.startswith('https://') or word.startswith('www.') or word.startswith('youtu'):
							post_facebook_quickreply(sender_id, word)
							flag_URL = 1

					if flag_URL == 0:
						message_text = 'Please enter a valid video link to download.'
						post_facebook_message(sender_id, message_text)

				except Exception as e:
					print e
					pass

		return HttpResponse()

def index(request):
	#set_greeting_text()
	return HttpResponse('Building Youtube Downloader Bot!')