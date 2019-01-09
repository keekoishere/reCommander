# uns imports
from spotipy import oauth2
import spotipy
import webbrowser
import requests
import spotipy.util as util
from json.decoder import JSONDecodeError

# get tracks saved (max from get_current_album)
access_token = token_info['access_token']
sp = spotipy.Spotify(access_token)
results = sp.current_user_saved_albums(50)
y = []
for x in results["items"]:
			for i in x["album"]["tracks"]["items"]:
				y.append(i["name"])

# logging in with:
sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope, cache_path=cache_path)
auth_url = sp_oauth.get_authorize_url()
acess_token = ""
token_info = sp_oauth.get_cached_token()

# where people get redirected after clicking the login button
def login(request):
	token_info = sp_oauth.get_cached_token()
	if token_info:
		return redirect('/home')
	else:
		auth_url = sp_oauth.get_authorize_url()
		return redirect(auth_url)

# after all the login I still need this callback for the midpart
def callback(request):
	code = request.GET.get('code')
	token_info = sp_oauth.get_access_token(code)
	return HttpResponseRedirect('/login')

# function to check if logged in
def requirelogin():
	token_info = sp_oauth.get_cached_token()
	access_token = token_info['access_token']
	sp = spotipy.Spotify(access_token)
	if not sp:
		return render(request, 'spotify/index.html')
	else:
		return sp
		
# a function that redirects user to a login page if he's not logged in, probably home
def requirelogin():

	# check if there's a token in session, this also refreshes the token if there is one
	try:
		if request.session['username']:
			access_token = request.session['access_token']
			sp = spotipy.Spotify(access_token)
			return sp		
	except:
		return render(request, 'spotify/index.html')




	def search(request):
	q = request.GET.get("q")
	if not q:
		raise RuntimeError("that's not a valid query")

	access_token = request.session['access_token']
	sp = spotipy.Spotify(access_token)
	result = sp.search(q)

	return JsonResponse(result)

	q = "radio"
	access_token = request.session['access_token']
	sp = spotipy.Spotify(access_token)
	result = sp.search(q)

	return render(request, 'spotify/search.html', {'result' : result})
	# from search get artist from typ track
	{{ result.tracks.items.0.artists.0.name }}




	results = sp.search(q, type='artist')
	for x in range(10):
		artists = results["artists"]["items"][x]["name"]
		result = {}
		result['artists']=artists
		final.append(result)

# se precisar de meter o resultado no ecra da recomendaçao tbm
		  if (suggestion.track == undefined){
    document.getElementById("suggest").innerHTML = "<h2>" + suggestion.artists + " (" 
    + suggestion.album + ' )' + "<img src=" + suggestion.image + ">" + "</h2>";
  }
  else {
    document.getElementById("suggest").innerHTML = "<h2>" + suggestion.artists + " - " 
    + suggestion.track + "<img src=" + suggestion.image + ">" + "</h2>";
  }



  u = Username(user=r['display_name'], country=r['country'], image='https://cdn.vox-cdn.com/thumbor/ITErCh1_JR7_GwWdMVmM9WRFwu4=/0x0:1200x675/1200x0/filters:focal(0x0:1200x675):no_upscale()/cdn.vox-cdn.com/uploads/chorus_asset/file/10838143/monkas.png', \
				URL=r['external_urls']['spotify'], followers=r['followers']['total'], \
				email=r['email'], rtoken=request.session['refresh_token'],\
				atoken=request.session['access_token'], texpiresat=request.session['expires_at'])
				u.save()
				return HttpResponseRedirect('/home')

@require_login
def listentothis(request, genurl)
	rec = get_object_or_404(Username, user=)
	try:
		rec.
path('listentothis/<genurl>', views.listentothis, name='listentothis'),