from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
import json
import os
import sys
import string
import random
import requests
import time
import math
import spotipy
from spotipy import oauth2
import spotipy.util as util

from .models import Username, Recommend, Answer

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# My app info
SPOTIPY_REDIRECT_URI = "https://recspotify.herokuapp.com/callback"
#SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8000/callback"
SPOTIPY_CLIENT_SECRET = ""
SPOTIPY_CLIENT_ID = ""
access_token = ""

# scopes I want to ask the user access for
scope = "user-follow-read user-read-email user-top-read user-library-read\
 user-library-modify user-read-currently-playing \
 user-read-playback-state user-read-private \
 user-read-recently-played playlist-modify-public playlist-modify-private \
 playlist-read-collaborative playlist-read-private"
code = ''
cache_path = ".cache-"
sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope, cache_path=cache_path)

# function to refine my search
def helpsearch(query):
	q = query.split(" ")
	x = len(q)
	k = ""
	for y in range(x):
		k += q[y] + "*"
		if y == x - 1:
			break
		k += " AND "
		
	return k

# So I can refresh tokens through sessions
def is_token_expired(token_info):
    now = int(time.time())
    return token_info - now < 60

# decorator function for login
def require_login(function):
    def wrap(request, *args, **kwargs):
    	try:
    		if request.session['refresh_token'] is None:
    			return HttpResponseRedirect('/login')
    	except:
    		return HttpResponseRedirect('/login')
    	if is_token_expired(request.session['expires_at']):
    		return HttpResponseRedirect('/login')
    	else:
    		return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

# main page with info about the website and login
def index(request):
	try:
		if request.session['username']:
			return HttpResponseRedirect('/home')
	except:
		return render(request, 'network/index.html')

def logout(request):
	request.session.flush()
	return HttpResponseRedirect('/')


def needusername(request):
	return render(request, 'network/needusername.html')

# where people get redirected after clicking the login button
def login(request):
	if request.method =='POST':
		request.session['username'] = request.POST['newusername']
		
		# confirm this username is his
		try:
			access_token = request.session['access_token']
			sp = spotipy.Spotify(access_token)
			r = sp.current_user()
			y = Username.objects.get(user=request.session['username'])
			if y.email != r['email']:
				return render(request, 'network/index.html', {'alert' : "That username already exists, and it isnt you!"})
			else:
				return HttpResponseRedirect('/login')
		except:
			pass
		return HttpResponseRedirect('/login')
	try:
		if request.session['username'] != None:
			if is_token_expired(request.session['expires_at']):
				x = sp_oauth.refresh_access_token(request.session['refresh_token'])
				request.session['access_token'] = x['access_token']
				request.session['refresh_token'] = x['refresh_token']
				request.session['expires_at'] = x['expires_at']
			

	# If I can't fetch tokens from sessions, go to login+callback
	except:
		auth_url = sp_oauth.get_authorize_url()
		return redirect(auth_url)

	# check if user is in the db, if not insert it and send back to home
	try:
		access_token = request.session['access_token']
		sp = spotipy.Spotify(access_token)
		r = sp.current_user()
		

		# update the tokens and other info if changed
		# in the database to use them to check info on others
		p = Username.objects.get(user=request.session['username'])
		if p.rtoken != request.session['refresh_token']:
			p.rtoken=request.session['refresh_token']
			p.atoken=request.session['access_token']
			p.texpiresat=request.session['expires_at']
			p.save()

		try:
			if p.image != r['images'][0]['url']:
				p.image = r['images'][0]['url']
				p.save()
			if p.followers != r['followers']['total']:
				p.followers = r['followers']['total']
				p.save()
		except:
			pass

		return HttpResponseRedirect('/home')

	except:
		sp = spotipy.Spotify(access_token)
		r = sp.current_user()

		# add user to the database
		try:
				if r['display_name'] != None:
					u = Username(user=r['display_name'], country=r['country'], image=r['images'][0]['url'], \
					URL=r['external_urls']['spotify'], followers=r['followers']['total'], \
					email=r['email'], rtoken=request.session['refresh_token'],\
					atoken=request.session['access_token'], texpiresat=request.session['expires_at'])
					u.save()
					return HttpResponseRedirect('/home')
				else:
					u = Username(user=request.session['username'], country=r['country'], image=r['images'][0]['url'], \
					URL=r['external_urls']['spotify'], followers=r['followers']['total'], \
					email=r['email'], rtoken=request.session['refresh_token'],\
					atoken=request.session['access_token'], texpiresat=request.session['expires_at'])
					u.save()
					return HttpResponseRedirect('/home')


		# stil got to separate not having user + image
		except:
			if r['display_name'] != None:
				u = Username(user=r['display_name'], country=r['country'], image='https://cdn.vox-cdn.com/thumbor/ITErCh1_JR7_GwWdMVmM9WRFwu4=/0x0:1200x675/1200x0/filters:focal(0x0:1200x675):no_upscale()/cdn.vox-cdn.com/uploads/chorus_asset/file/10838143/monkas.png', \
				URL=r['external_urls']['spotify'], followers=r['followers']['total'], \
				email=r['email'], rtoken=request.session['refresh_token'],\
				atoken=request.session['access_token'], texpiresat=request.session['expires_at'])
				u.save()
				return HttpResponseRedirect('/home')
			else:
				u = Username(user=request.session['username'], country=r['country'], image='https://cdn.vox-cdn.com/thumbor/ITErCh1_JR7_GwWdMVmM9WRFwu4=/0x0:1200x675/1200x0/filters:focal(0x0:1200x675):no_upscale()/cdn.vox-cdn.com/uploads/chorus_asset/file/10838143/monkas.png', \
				URL=r['external_urls']['spotify'], followers=r['followers']['total'], \
				email=r['email'], rtoken=request.session['refresh_token'],\
				atoken=request.session['access_token'], texpiresat=request.session['expires_at'])
				u.save()
				return HttpResponseRedirect('/home')


		return HttpResponseRedirect('/home')

	
				
# after all the login I still need this callback for the midpart
def callback(request):
	code = request.GET.get('code')
	token_info = sp_oauth.get_access_token(code)
	access_token = token_info['access_token']
	sp = spotipy.Spotify(access_token)
	r = sp.current_user()
	ok = r['email']
		
	# send the user's info through session
	request.session['username'] = r['display_name']
	request.session['access_token'] = token_info['access_token']
	request.session['refresh_token'] = token_info['refresh_token']
	request.session['expires_at'] = token_info['expires_at']

	# if the user has no display name
	if request.session['username'] == None:
		try:
			y = Username.objects.get(email=ok)
			request.session['username'] = y.user
			return HttpResponseRedirect('/login')
		except:
			return HttpResponseRedirect('/needusername')
	else:
		return HttpResponseRedirect('/login')

# homepage for the user, showing statistics and options	
@require_login
def home(request):
	access_token = request.session['access_token']

	sp = spotipy.Spotify(access_token)
	
	# info on user details
	userinfo = Username.objects.get(user=request.session['username'])

	# get info for topartists, short_term = 1 month
	topartists = sp.current_user_top_artists(time_range='short_term', limit=50)
		
	# get info for top tracks	
	toptracks = sp.current_user_top_tracks(time_range='short_term', limit=50)
	
	# get music people recommended you form DB
	received = Recommend.objects.filter(recdado__user=request.session['username'])

	# get info on recs received
	receivedrecs = []
	durations = []
	for item in received:
		if item.tipo == 'track':
			r = sp.track(item.spotid)
			duration = durationf(r['duration_ms'])
			receivedrecs.append(r)
			durations.append(duration)

		# need to separate types because of spotipy method. also, need to add duration for template loop
		if item.tipo == 'album':
			r = sp.album(item.spotid)
			receivedrecs.append(r)
			duration = ''
			durations.append(duration)
	receivedt = zip(received, receivedrecs, durations)

	# do the same for the recs the user has given
	recdados = Recommend.objects.filter(recmander__user=request.session['username'])
	musicrecdados = []
	durations = []
	seen = []
	repeated = []
	seentop = []
	for item in recdados:
		if item.tipo == 'track':
			r = sp.track(item.spotid)
			duration = durationf(r['duration_ms'])
			musicrecdados.append(r)
			durations.append(duration)

		# need to separate types because of spotipy method. also, need to add duration for template loop
		if item.tipo == 'album':
			r = sp.album(item.spotid)
			musicrecdados.append(r)
			duration = ''
			durations.append(duration)
	

	# check the recmanded user history to see if he played i
	

		# only check history if user allows	it
		try: #the recommendation might not have a recdado yet!
			if item.recdado.historyperm == True:
				if is_token_expired(item.recdado.texpiresat):
					x = sp_oauth.refresh_access_token(item.recdado.rtoken)
					spsp = spotipy.Spotify(x['access_token'])
					history = spsp.current_user_recently_played()				
					for item in recdados:
						if item in repeated:
							break		
						else:
							for x in range(50):
								if history['items'][x]['track']['uri'] not in seen:
									seen.append(history['items'][x]['track']['uri'])
							repeated.append(item)

					# check if in top tracks of month too
					toptracks2 = spsp.current_user_top_tracks(time_range='short_term', limit=50)
					for idx, item in enumerate(toptracks2):
						seentop.append(toptracks2['items'][idx]['uri'])
		except:
			pass
			

	for item in recdados:
		if item.spotid in seen:
			item.prova = True
			item.save()
		if item.spotid in seentop:
			item.prova = True
			item.top = True
			item.save()


	recdadost = zip(recdados, musicrecdados, durations)

	return render(request, 'network/home.html', {'userinfo' : userinfo,  \
	 'topartists' : topartists, 'toptracks' : toptracks, \
	 'receivedt' : receivedt, 'recdadost' : recdadost, 'seen' : seen
	 })
	


# where the user can recommend stuff to others
@require_login
def recommend(request):
	# info on user details
	userinfo = Username.objects.get(user=request.session['username'])
	# get info
	recs = {}
	access_token = request.session['access_token']
	sp = spotipy.Spotify(access_token)

	try:
		user = Username.objects.get(user=request.session['username'])
		recs_sent = user.recommend_set.all()
		recs_received = Recommend.objects.get(recdado=request.session['username'])
		recs[received] = recs_received
		recs[sent] = recs_sent
	except:
		pass
	return render(request, 'network/recommend.html', {'sesusername' : request.session["username"],\
		'recs' : recs, 'userinfo': userinfo })
	

# search for music to rec to integrate in rec.html
@require_login
def search(request):

	# get the query written inside the typeahead form
	q = request.GET.get("q")
	if not q:
		raise RuntimeError("that's not a valid query")

	# use wildcards to improve search query
	
	access_token = request.session['access_token']
	sp = spotipy.Spotify(access_token)
	tracks = []
	artists = []	
	final =[]

	# different loops capped at 10 to send over ajax, can't do it otherwise w/ typeahead
	results = sp.search(helpsearch(q))
	for x in range(5):
		try:
			track = results["tracks"]["items"][x]["name"]
		except:
			break
		result = {}
		result['track']= track
		artists = results['tracks']["items"][x]["artists"][0]['name']
		result['artists']= artists
		album = results['tracks']["items"][x]['album']['name']
		result['album'] = album
		image = results["tracks"]["items"][x]['album']['images'][2]['url']
		result['image']=image
		uri = results['tracks']['items'][x]['uri']
		result['uri']=uri
		embedurl = results['tracks']["items"][x]['external_urls']['spotify']
		result['embedurl'] = embedurl
		duration = results['tracks']['items'][x]['duration_ms']
		result['duration'] = durationf(duration)
		tipo = results['tracks']["items"][x]['type']
		result['tipo'] = tipo
		final.append(result)

	results = sp.search(helpsearch(q), type='album')
	for x in range(5):
		try:
			albums = results["albums"]["items"][x]["name"]
		except:
			break
		result = {}
		result['album']=albums
		artists = results["albums"]["items"][x]["artists"][0]['name']
		result['artists']=artists
		image = results["albums"]["items"][x]['images'][2]['url']
		result['image'] = image
		uri = results['albums']["items"][x]['uri']
		result['uri'] = uri
		embedurl = results['albums']["items"][x]['external_urls']['spotify']
		result['embedurl'] = embedurl
		tipo = results['albums']["items"][x]['type']
		result['tipo'] = tipo
		final.append(result)
	
	

	# need to return in json, safe so i can pass lists
	return JsonResponse(final, safe = False)

# helper function to get duration of tracks from ms in min:s
def durationf(f):
	def truncate(f):
		return math.floor(f * 10 ** 0) / 10 ** 0
	o = str(round((f * 0.001) % 60))
	if len(o) == 1:
		o = '0' + o
	l = str(truncate(((f * 0.001) / 60)))
	lo = l[:-2] + ':' + o
	return lo

# function to generate URLs for suggestions
def generate_url(size=8, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

# path to fetch user names w AJAX for the suggest form
@require_login
def getuserstorec(request):
	if request.method == 'POST':
		access_token = request.session['access_token']
		sp = spotipy.Spotify(access_token)
		final =[]

	# I also need to pass 'friends' of the recmander so I can put the names on the form
	
	try: # it might be empty
		pkid = Username.objects.get(user=request.session['username'])
		results = Recommend.objects.all().filter(recdado=pkid.id)

		# I need to add the recmander's name to pass, but only one!
		for i in results:
			result = {'names': ''}
			if i.recmander.user not in final:
				result['names'] = i.recmander.user 
				result['img'] = i.recmander.image
				if result not in final:
					final.append(result)
	except:
		pass

	try: 
	# I need to fetch the ID since it's a foreignkey
		results = Recommend.objects.all().filter(recmander=pkid.id)
		for i in results:
			result = {'names': ''}
			try:
				if i.recdado.user not in final and i.recdado.user != '':
					result['names'] = i.recdado.user 
					result['img'] = i.recdado.image
					if result not in final:
						final.append(result)
			except:
				pass
	except:
		pass

	return JsonResponse(final, safe=False)


# path to receive data from AJAX and return URL and stuiff
@require_login
def listento(request):
	# use the data from AJAX on the recommend script, get from form
	if request.method == 'POST':
		rec = {}

		# had to use the name parameter in the inputs and not id... lol
		rec['recmander'] = request.session['username']
		rec['recdado'] = request.POST.get('recdado')
		rec['tipo'] = request.POST.get('tipo')
		rec['msg'] = request.POST.get('msg')
		rec['spotifyid'] = request.POST.get('spotifyuri')
		rec['genurl'] = generate_url()
		while True:
			try:
				p = Recommend.objects.get(genurl=rec['rurl'])
				rec['genurl'] = generate_url()
			except:
				break
		p = Username.objects.get(user=request.session['username'])
		try:
			e = Username.objects.get(user=rec['recdado'])
		except:
			pass
		try:
			l = Recommend(recmander=p, recdado=e,\
			spotid=rec['spotifyid'], genurl=rec['genurl'], tipo=rec['tipo'],\
			msg=rec['msg'])
		except:
			l = Recommend(recmander=p,\
			spotid=rec['spotifyid'], genurl=rec['genurl'], tipo=rec['tipo'],\
			msg=rec['msg'])

		l.save()
		
		return JsonResponse(rec, safe=False)

	else:
		return render(request, 'network/home.html')

# view to submit answers and where to see the recs
@require_login
def listentothis(request, genurl):

	# info on user details
	userinfo = Username.objects.get(user=request.session['username'])

	if request.method == "POST":
		answer = request.POST.get('msg')
		u = Answer(answer=answer)
		u.save()

		dbid = request.POST.get('dbid')

		
		rec = Recommend.objects.get(id=dbid)
					

		# If there's an answer already, go overwrite it and delete
		try:
			deleteold = Answer.objects.get(answer=rec.answer)
			deleteold.delete()

		except:
			pass

		rec.answer = u
		rec.save()
		action = "answer"
		messages.success(request, 'Your answer has been sent!')
		return JsonResponse(action, safe=False)

	# get the object from the rec table
	# get a simple rec made for you
	try:
		rec = get_object_or_404(Recommend, genurl=genurl, recdado=userinfo)

	# if the recdado user is blank
	except:

		# check if there's only one
		try:
			rec = get_object_or_404(Recommend, genurl=genurl, recdado=None)

		# might be >1 or none
		except:

			# still try it if there's 1 but with a recdado not this user
			try:
				rec = get_object_or_404(Recommend, genurl=genurl)

			# if there's still >1, use filter instead
			except:
				rec = Recommend.objects.filter(genurl=genurl)
				try:
					rec = rec[0]
				except: 
					pass

				# I just want to copy the info on one of these from rec1
			

	# search the item to retrieve info to show
	access_token = request.session['access_token']
	sp = spotipy.Spotify(access_token)
	try:
		musicinfo = sp.album(rec.spotid)
		embedurl = musicinfo['external_urls']['spotify']
	except:
		musicinfo = sp.track(rec.spotid)
		embedurl = musicinfo["external_urls"]["spotify"]
	
	# I want to embed it to play
	a = embedurl.split(".com/")
	embedurl = a[0] + ".com/embed/" + a[1]

	# get saved playlists so he can save into one
	results = sp.current_user_playlists(limit=50)
	
	final = []
	try:
		for x in range(50):
			playlists = {}
			# I can only modify playlists owned by the user
			u = results['items'][x]['owner']['display_name']
			p = sp.current_user()
			if u != p['display_name']:
				continue
			y = results['items'][x]['name']
			playlists['names'] = y
			o = results['items'][x]['uri']
			playlists['uri'] = o
			u = results['items'][x]['id']
			playlists['id'] = u
			
			final.append(playlists)
	except:
		pass
	# add the user who's logged in == person who got recmanded
	item = musicinfo["artists"][0]["name"] + " - " + musicinfo["name"]

	
	
	if (userinfo) == (rec.recmander):
		messages.info(request, 'This request wants done by you.')
		action = "same"
		return render(request, 'network/gotrecd.html', {'rec':rec, 'musicinfo' : musicinfo,\
	 'embedurl' : embedurl, 'genurl':genurl, 'final' : final, 'userinfo' : userinfo, 'action': action})
	
	else:
		# If the rec was from other user
		if rec.recmander != userinfo and rec.recdado != None and rec.recdado != userinfo:
			u = Recommend(recmander=rec.recmander, recdado = userinfo, spotid=rec.spotid, genurl=genurl,\
				tipo=rec.tipo, msg=rec.msg, visto=True)
			u.save()

		# if the rec was made with no recdado, save w/ the current user 
		elif rec.recmander != userinfo and rec.recdado == None:
			rec.recdado = userinfo
			rec.visto = True
			rec.save()
		elif rec.recmander != userinfo and rec.recdado == userinfo:
			rec.visto = True
			rec.save()
	
	return render(request, 'network/gotrecd.html', {'rec':rec, 'musicinfo' : musicinfo,\
	 'embedurl' : embedurl, 'genurl':genurl, 'final' : final, 'userinfo' : userinfo})


# view to add to playlists and save tracks/albums
@require_login
def addmusic(request):
	if request.method == "POST":

		# need to get the user's ID to add tracks
		access_token = request.session['access_token']
		sp = spotipy.Spotify(access_token)

		# Check if it's to add a playlist
		try:
			playlist = request.POST.get("playlist")
	
			# spotipy needs the ID so I split it from the URI
			spotid = request.POST.get("spotid")
			trackid=spotid.split(":")
			trackid=trackid[2]
			song = [trackid]

			# need user info to add to playlists
			access_token = request.session['access_token']
			user = sp.current_user()
			user = user['id']			
			ye = sp.user_playlist_add_tracks(user, playlist, song, position=None)
			action = 'Track was added to playlist'
			messages.info(request, action)

		
		except:

			# may be a track
			try:
				spotid = request.POST.get("spotid")
				trackid=spotid.split(":")
				trackid=trackid[2]
				song = [trackid]
				savetrack = sp.current_user_saved_tracks_add(tracks = song)
				action = 'Track was saved to library'
				messages.info(request, action)

			# may be an album
			except:
				spotid = request.POST.get("spotid")
				trackid=spotid.split(":")
				trackid=trackid[2]
				song = [trackid]
				savealbum = sp.current_user_saved_albums_add(albums = song)
				action = 'Album was saved to library'
				messages.info(request, action)

			
		return JsonResponse(action, safe=False)
		
@require_login
def likemusic(request):
	if request.method == "POST":
		genurl = request.POST.get("liked")
		p = Recommend.objects.get(genurl=genurl)
		p.liked = True
		p.save()
		action = "We'll pat them in the back for that one"
		messages.info(request, action )
		
	return JsonResponse(action, safe=False)

# click on answer at table to check the item + answer
@require_login
def answer(request):
	if request.method == "POST":
		recdados = request.POST.get("recdados")
		recdados = Recommend.objects.get(pk=recdados)
		embedurl = request.POST.get("answermusic")
		
	
	# I want to embed it to play
		a = embedurl.split(".com/")
		embedurl = a[0] + ".com/embed/" + a[1]

		return render(request, 'network/answer.html', {'embedurl' : embedurl, 'recdados' : recdados,})

# change permission on history
@require_login
def changeperm(request):
	y = Username.objects.get(user=request.session['username'])

	if y.historyperm == True:
		y.historyperm = False
		y.save()
	else:
		y.historyperm = True
		y.save()

	return JsonResponse("done", safe=False)



	


