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

VERIFY_TOKEN = 'youtube-download-karega'
PAGE_ACCESS_TOKEN = 'EAAO5LXdwYSwBADZClxlG8zxcgHdcmzhr87ZC6H3wvWQyypX1666JRcEJwhIk830av89OGoqtkogM0tJS74vQElsMyaKo9i1lG5J0GIAF9nfFQiSeyxjkkWJDRX8ZBdYeFujPujW7DRCjzZA8XGuN7d6o1SbXYLPZBa4kvForUJgZDZD'

def scraper(search):
	url = "https://www.youtube.com/results?search_query="
	print '*****'*5
	print '*****'*7
	print '\n\nScraper Up!'

	for char in search:
		if not (char.isalnum() or char==' '):
			search = search.replace(char, '%'+hex(ord(char)).split('0x')[1])
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
			uploader = data.find('div', {'class': 'yt-lockup-byline'}).find('a').text.decode('utf-8', 'ignore')
			heading = data.find_all('h3', {'class': 'yt-lockup-title'})[0].find_all('a')[0].text.decode('utf-8', 'ignore')
			url = 'https://www.youtube.com' + data.find('h3', {'class': 'yt-lockup-title'}).find('a')['href'].decode('utf-8', 'ignore')
			duration = data.find('h3', {'class': 'yt-lockup-title'}).find('span').text.decode('utf-8', 'ignore')
			uploaded_on = data.find('div', {'class': 'yt-lockup-meta'}).find('ul').find_all('li')[0].text.decode('utf-8', 'ignore')
			views = data.find('div', {'class': 'yt-lockup-meta'}).find('ul').find_all('li')[1].text.decode('utf-8', 'ignore')
			image = thumbnail.find('span', {'class': 'yt-thumb-simple'}).find('img')['src'].decode('utf-8', 'ignore')
		except:
			continue

		if image.endswith('.gif'):
			break
		
		print heading + '--' + duration + '--' +  uploader + '--' + uploaded_on + '--' + views + '--' + image + '\n'

		COLLECTION['heading'].append(heading)
		COLLECTION['url'].append(url)
		COLLECTION['duration'].append(duration)
		COLLECTION['uploader'].append(uploader)
		COLLECTION['uploaded_on'].append(uploaded_on)
		COLLECTION['views'].append(views)
		COLLECTION['image'].append(image)
	
	print '\n\nScraper Down!'
	print '*****'*7
	print '*****'*5
	return COLLECTION

def set_greeting_text():
	post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%PAGE_ACCESS_TOKEN
	response_msg = {
		"setting_type": "greeting",
		"greeting":{
			"text":"Hello! Just enter a word relating to which you'd like to search a video on YouTube. If you are on messenger app or www.messenger.com: You can also simply enter the youtube url you wish to download!\nIf you are on browser: Enter \"youtube-url \'audio\'\" or \"youtube-url \'video\'\" to download audio/video of the YouTube video."
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
		message_text = 'Open the link, right click on the audio and while saving, rename it to (anything).mp3'
		post_facebook_message(sender_id,message_text)
		#post_facebook_file(sender_id, bestaudio.url, video.title)
	
	return

def post_facebook_list(fbid, results):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
	
	print '\n\n'
	print '$'*25

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

	print '$'*20
	print '\n\n'

def post_facebook_button(fbid, results):
	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

	response_msg_button = {
	  	"recipient":{
	    	"id":fbid
	  	},
	  	"message":{
	    	"attachment":{
	    	  	"type":"template",
	    	  	"payload":{
		        	"template_type": "button",
	        		"text": results['heading'][0],
	        		"buttons":[
		          		{
		            		"type": "postback",
		            		"title": 'Uploaded by: ' + results['uploader'][0] + ', ' + results['uploaded_on'][0] + ' with ' + results['views'][0],
		            		"payload": results['url'][0]
		          		}
	       			]
	    		}
	    	}
	  	}
	}
	
	response_msg_button = json.dumps(response_msg_button)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_button)
	print status.json()

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
	
	url = url + '.mp3'
	print '-----' + url + '-----'
	
	'''cmd = 'youtube-dl --extract-audio --audio-format mp3 --audio-quality 0 --output \"' + title + '\" ' + url
	os.system(cmd)
	'''
	
	response_msg_file = {
		"recipient":{
			"id": fbid
		},
		"message":{
			"attachment":{
				"type":"file",
				"payload":{
					"url": url
				}
			}
		}
	}
	#os.system('rm '+title)
	
	response_msg_file = json.dumps(response_msg_file)
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg_file)
	print '\n'*3
	print '*'*25
	print status
	print '*'*25
	print '\n'*3

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
	status = requests.get(post_message_url, files=files)
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
							if word.startswith('https://') or word.startswith('http://') or word.startswith('www.') or word.startswith('youtu'):
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
					pass

		return HttpResponse()

def index(request):
	set_greeting_text()
	return HttpResponse('Building Youtube Downloader Bot!')