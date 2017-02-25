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
from bs4 import BeautifulSoup as BS

VERIFY_TOKEN = 'new_youtube_downloader_12'
PAGE_ACCESS_TOKEN = 'EAAO5LXdwYSwBANq4EEGYD8ON5NDLJMC3QU8ZAkWFARQOWDLQy85vsEVkC1bpmmkbZCcEOquD5DPZCEIA8oPfAEjRO61hz9IKUgxBEpH1ADhCM00cISgtfLnwBnCZC7JMQ7mDAu6nXvygZCEKgiCSK2d8EkhiKPt6VtInZBc4PcOQZDZD'

def scraper(search):
	url = "https://www.youtube.com/results?search_query="
	print '\n'*2
	print '_'*20
	print '\n\nScraper Up!'

	for char in search:
		if not (char.isalnum() or char==' '):
			search = search.replace(char, '%' + hex(ord(char)).split('0x')[1])
	search = search.replace(' ', '+')
	url = url + search
	print url
	r=requests.get(url)
	soup=BS(r.text, "html.parser")
	links = soup.find_all('div', {'class': 'yt-lockup yt-lockup-tile yt-lockup-video clearfix'})
	videos = soup.find_all('div', {'class' : 'yt-lockup-dismissable yt-uix-tile'})
	
	COLLECTION = {}
	COLLECTION['heading'] = []
	COLLECTION['url'] = []
	COLLECTION['duration'] = []
	COLLECTION['uploader'] = []
	COLLECTION['uploaded_on'] = []
	COLLECTION['views'] = []
	COLLECTION['image'] = []

	for video in videos:
		thumbnail = video.find('div', {'class': 'yt-lockup-thumbnail contains-addto'})
		data = video.find('div', {'class': 'yt-lockup-content'})
		try:
			uploader = data.find('div', {'class': 'yt-lockup-byline'}).find('a').text.encode('utf-8', 'ignore')
			heading = data.find_all('h3', {'class': 'yt-lockup-title'})[0].find_all('a')[0].text.encode('utf-8', 'ignore')
			url = 'https://www.youtube.com' + data.find('h3', {'class': 'yt-lockup-title'}).find('a')['href'].encode('utf-8', 'ignore')
			duration = data.find('h3', {'class': 'yt-lockup-title'}).find('span').text.encode('utf-8', 'ignore')
			uploaded_on = data.find('div', {'class': 'yt-lockup-meta'}).find('ul').find_all('li')[0].text.encode('utf-8', 'ignore')
			views = data.find('div', {'class': 'yt-lockup-meta'}).find('ul').find_all('li')[1].text.encode('utf-8', 'ignore')
			image = thumbnail.find('span', {'class': 'yt-thumb-simple'}).find('img')['src'].encode('utf-8', 'ignore')
		except Exception as e:
			print e
			continue
		
		print heading + '--' + duration + '--' +  uploader + '--' + uploaded_on + '--' + views + '--' + image + '\n'

		COLLECTION['heading'].append(heading)
		COLLECTION['url'].append(url)
		COLLECTION['duration'].append(duration)
		COLLECTION['uploader'].append(uploader)
		COLLECTION['uploaded_on'].append(uploaded_on)
		COLLECTION['views'].append(views)
		COLLECTION['image'].append(image)
	
	print '\n\nScraper Down!'
	print '_'*20
	print '\n'*2
	return COLLECTION

def scraper2(uid):

	print '\n'*2
	print '_'*20
	print '\n\nSecondary Scraper Up!'


	url = 'https://www.yt-download.org/grab?vidID=' + uid + '&format=mp3'

	headers = {
		'accept' : 'text/html, */*; q=0.01',
		'accept-encoding' : 'gzip, deflate, sdch, br',
		'accept-language' : 'en-IN,en-GB;q=0.8,en-US;q=0.6,en;q=0.4',
		'cookie' : '__cfduid=d5f48ffbb246c30eb1b77b9694df6950a1487244481; PHPSESSID=s15; _popfired=2; _ga=GA1.2.7205434.1487244483',
		'referer' : 'https://www.yt-download.org/api-console/audio/' + uid,
		'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
		'x-requested-with' : 'XMLHttpRequest'
	}

	r = requests.get(url=url, headers=headers)
	soup = BS(r.text, "html.parser")
	soup = soup.find('a')['href']
	down_url = 'https:' + soup

	print down_url
	print '\n\nSecondary Scraper Down!'
	print '_'*20
	print '\n'*2
	return down_url

def set_greeting_text():
	post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%PAGE_ACCESS_TOKEN
	response_msg = {
		"setting_type": "greeting",
		"greeting":{
			"text":"Hello! Just enter a word relating to which you'd like to search a video on YouTube. You can also simply enter the youtube url you wish to download! Alternatively, enter \"youtube-url \'audio\'\" or \"youtube-url \'video\'\" to directly download audio/video of the YouTube video."
		}
	}
	response_msg = json.dumps(response_msg)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
	print status

def post_facebook_quickreply(fbid, url):
	
	print '\n'*2
	print '_'*20
	print '\n\nPost FB Quickreply!'
	
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
	print '_'*20
	print '\n'*2

def handle_quickreply(sender_id, payload):
	
	print '\n'*2
	print '_'*20
	print '\n\nHandling Quickreply!'

	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	url = payload.split('!$#@')[1]
	video = pafy.new(url)
	best = video.getbest()
	message_text = video.title + '\t(' + video.duration + ')'
	post_facebook_message(sender_id, message_text)
	
	if payload.split('!$#@')[0] == 'video':
		r = requests.get('http://tinyurl.com/api-create.php?url=' + best.url)
		message_text = 'Download Video: ' + str(r.text)
		post_facebook_message(sender_id, message_text)
		message_text = 'Open the link, right click or long tap on the video to save it.'
		post_facebook_message(sender_id, message_text)

	elif payload.split('!$#@')[0] == 'audio':
		
		url2 = url.split('watch?v=')[1]
		audiolink = scraper2(url2)
		bestaudio = video.getbestaudio(preftype='m4a')

		audiostat1 = post_facebook_audio(sender_id, audiolink)
		if 'Response [200]' not in (str(audiostat1)):
			audiostat2 = post_facebook_audio(sender_id, bestaudio.url)

		message_text = 'Download audio at 320kbps bitrate:'
		post_facebook_message(sender_id, message_text)	
		filestat1 = post_facebook_file(sender_id, audiolink)
		
		if 'Response [200]' not in (str(filestat1)):

			message_text = audiolink
			post_facebook_message(sender_id, message_text)
			
			message_text = 'Alternatively, download audio at ' + bestaudio.bitrate + 'bps bitrate:'
			post_facebook_message(sender_id, message_text)
			filestat2 = post_facebook_file(sender_id, bestaudio.url)
			
			if 'Response [200]' not in (str(filestat2)):
				r = requests.get('http://tinyurl.com/api-create.php?url=' + bestaudio.url)
				message_text = str(r.text) + '\n\nYou would need to rename this file after download. Importantly, append the ".' + bestaudio.extension + '" extension to the filename!'
				post_facebook_message(sender_id, message_text)
		
		'''
		message_text = 'Download audio at 320kbps bitrate:\n\n' + audiolink
		post_facebook_message(sender_id, message_text)
		#r = requests.get('http://tinyurl.com/api-create.php?url=' + bestaudio.url)
		message_text = 'Alternatively, download audio at ' + bestaudio.bitrate + 'bps bitrate:\n\n' + str(bestaudio.url)
		post_facebook_message(sender_id, message_text)
		message_text = 'After downloading, you would need to rename this file after download. Importantly, append the ".' + bestaudio.extension + '" extension to the filename!'
		post_facebook_message(sender_id, message_text)
		'''

	print '_'*20
	print '\n'*2
	return

def post_facebook_list(fbid, results):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	print '\n'*3
	print '_'*20
	print '\n\nPosting List!'

	response_msg_list = {
		"recipient":{
			"id": fbid
		},
		"message": {
	    	"attachment": {
	        	"type": "template",
	        	"payload": {
		            "template_type": "list",
	            	"elements": [
	                	{
		                    "title": results['heading'][0],
		                    "image_url": results['image'][0],
		                    "subtitle": results['uploader'][0] + ', ' + results['uploaded_on'][0] + ' with ' + results['views'][0],
		                    "default_action": {
		                        "type": "web_url",
	                        	"url": results['url'][0],
	                    	},
		                    "buttons": [
	                        	{
		                            "type": "postback",
		                            "title": "Download",
	                            	"payload": results['url'][0]
	                        	}
	                    	]
	                	},
		            ],
		        }
		    }
		}
	}

	i = 1
	length = results['views'].__len__()
	while i<4 and i<length:
		item = {
			"title": results['heading'][i],
			"image_url": results['image'][i],
			"subtitle": results['uploader'][i] + ', ' + results['uploaded_on'][i] + ' with ' + results['views'][i],
			"default_action": {
				"type": "web_url",
				"url": results['url'][i],
			},
			"buttons": [
				{
					"title": "Download",
					"type": "postback",
					"payload": results['url'][i]
				}
			]                
		}
		i = i + 1
		response_msg_list['message']['attachment']['payload']['elements'].append(item)

	response_msg_list = json.dumps(response_msg_list)
	print response_msg_list
	
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_list)
	print status.json()

	print '_'*20
	print '\n'*3

def post_facebook_message(fbid, message_text):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	print '\n'*2
	print '_'*20
	print '\n\nSending Message!'

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
	print '_'*20
	print '\n'*2

def post_facebook_audio(fbid, url):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	print '\n'*2
	print '_'*20
	print '\n\nSending Audio!'

	response_msg_audio = {
		"recipient":{
			"id":fbid
		},
		"message":{
			"attachment":{
		    	"type":"audio",
		    	"payload":{
		        	"url":url
		      	}
		    }
		}
	}
	response_msg_audio = json.dumps(response_msg_audio)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_audio)
	print status
	print '_'*20
	print '\n'*2
	return status

def post_facebook_file(fbid, url):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	print '\n'*2
	print '_'*20
	print '\n\nSending File!'
	
	response_msg_file = {
		'recipient':{
			"id":fbid
		},
		'message':{
			"attachment":{
				"type":"file",
				"payload":{
					"url":url
				}
			}
		}
	}
	response_msg_file = json.dumps(response_msg_file)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_file)
	print status
	print '_'*20
	print '\n'*2
	return status

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
					if 'postback' in message:
						post_facebook_quickreply(sender_id, message['postback']['payload'])

					elif 'is_echo' in message['message']:
						post_facebook_message(sender_id, 'Facebook is conking me in the head.')
					
					elif 'quick_reply' in message['message']:
						handle_quickreply(sender_id, message['message']['quick_reply']['payload'])
					
					elif 'text' in message['message']:
						message_text = message['message']['text'] or ' '
						words = message_text.split(' ')
						flag_URL = 0
						flag_AV = 0
						url = ''
						AV = ''

						for word in words:
							if word.startswith('https://' or 'http://' or 'www.' or 'youtu'):
								flag_URL = 1
								url = word.replace("m.you", "you")
							if word.lower() in ['audio','video']:
								flag_AV = 1
								AV = word.lower()

						if flag_URL == 0:
							send_text = 'Searching for \"' + message_text +'\" on YouTube.'
							post_facebook_message(sender_id, send_text)

							results = scraper(message_text)
							if results['views'].__len__() == 0:
								send_text = 'Sorry, no results found. Please try again!'
								post_facebook_message(sender_id, send_text)
							else:
								post_facebook_list(sender_id, results)

						elif flag_URL == 1 and flag_AV == 0:
							post_facebook_quickreply(sender_id, url)

						elif flag_URL == 1 and flag_AV == 1:
							payload = AV + '!$#@' + url
							handle_quickreply(sender_id, payload)

					else:
						pass

				except Exception as e:
					print e

		return HttpResponse()

def index(request):
	set_greeting_text()
	return HttpResponse('Building Youtube Downloader Bot!')