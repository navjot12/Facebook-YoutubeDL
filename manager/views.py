#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import sys
import os
import time
import requests
from bs4 import BeautifulSoup as BS

VERIFY_TOKEN = 'youtube-download-karega'
PAGE_ACCESS_TOKEN = 'EAAO5LXdwYSwBAFNtQwyXBAgswtxV9wVMQMoUO887BT4dE8qFykRoyqEftoe2GHJe35HuLHL8ZAPmWWoW4evqBTO6cYUdFO7CYqKtyBLXvMrIxApNQe5iZBRmC3S6g0HEZBKOwzZAG0OXSrcZBGMcBlEHtKO57ownY3cDvAYMevwZDZD'

def post_facebook_message(fbid, message_text):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":message_text}})
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
	print status.json()

def sendAudio(fbid, file_name):
	pass

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
				print message
				try:
					sender_id = message['sender']['id']
					message_text = message['message']['text']
					
					words = message_text.split(' ')
					flag_URL = 0
					title = ''
					url = ''
					for text in words:
						if text.startswith('https://') or text.startswith('www.') or text.startswith('youtu'):
							url = text
							r = requests.get(url)
							soup=BS(r.text, "html.parser")
							title = soup.title.string
							title = title.split(' - YouTube')[0]
							title = title.split('|')[0].split('(')[0].split('.')[0].strip()
							title = title.replace(' ', '_').replace('\'', '')
							message_text = title
							flag_URL = 1
					
					if flag_URL == 0:
						message_text = 'Please enter a video link to download.'
					
					else :
					    cmd = 'youtube-dl --extract-audio --audio-format mp3 --audio-quality 0 --output \"' + title + '.mp3\" ' + url
						#os.system(cmd)
						message_text = 'Please wait while we fetch the audio file for you. Title: ' + title
						#sendAudio(fbid, title+'.mp3')
						#os.system('rm '+title+'.mp3')

					post_facebook_message(sender_id,message_text) 
				except Exception as e:
					print e
					pass

		return HttpResponse()

def index(request):
	return HttpResponse('Building Youtube Downloader Bot!')