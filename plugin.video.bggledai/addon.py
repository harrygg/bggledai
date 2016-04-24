# -*- coding: utf-8 -*-
import sys, os, base64, xbmcgui, re
from xbmcswift2 import Plugin
from urlparse import urlparse, urljoin
from resources.lib.grequest import GRequest
from resources.lib.mode import *

reload(sys)
sys.setdefaultencoding('utf8')
plugin = Plugin('plugin.video.bggledai')
req = GRequest(plugin)
url = base64.b64decode('aHR0cDovL2JnLWdsZWRhaS50di8=')

@plugin.cached_route('/', None, None, 240)
def index():
	items = []
	
	try:
		req.Get(url)
		el = req.soup.find(ul, id='menu-gledaitv')
		lis = el.findAll(li)
		del lis[0] # Remove first link
		
		for l in lis:
			items.append({
				label: l.a.get_text(),
				path: plugin.url_for(Mode.show_channels, id=get_path(l.a[href]))
			})
			
	except Exception, er:
		plugin.log.error(er)
	return items

@plugin.cached_route('/category/<id>/', None, None, 240)
def show_channels(id):
	items = []
	
	try:
		req.Get(urljoin(url, id))
		divs = req.soup.findAll(div, class_='gallerybox')
		
		for d in divs:
			heading = d.find(h2)
			link = get_path(heading.a[href])
			try: img = d.a.img[src]
			except: img = ''
			items.append({
				label : heading.a.get_text(), 
				path : plugin.url_for(Mode.play_stream, id=link),
				icon : img,
				is_playable : True
			})	
	except Exception, er:
		plugin.log.error(er)
	return items
				
@plugin.route('/channel/<id>')
def play_stream(id):
	try:
		main_url = urljoin(url, id)
		req.Get(main_url)
		iframe_url = req.soup.find(iframe, src=re.compile('.+freshvideos.+'))[src]
	
		req.Get(iframe_url, main_url)		
		if not req.UserLogged() and not req.Login(iframe_url):
			plugin.notify(msg=plugin.name, title='Грешка при логването', delay=10000)
			return False
		
		pl_url = get_playlist_url(iframe_url)
		plugin.set_resolved_url(pl_url)

	except Exception, er:
		plugin.log.error(er)

def get_playlist_url(url):
	try:
		matches = re.compile('playlist: +[\'"]+(.+?)[\'"]+').findall(req.response)
		u = urlparse(url)
		pl_url = '%s://%s/%s' % (u.scheme, u.netloc, matches[0])
		req.Get(pl_url)
		matches = re.compile('jwplayer:file>(.+?)<').findall(req.response)
		return matches[0] + '|User-Agent=' + req.user_agent_desktop
	except Exception, er:
		plugin.log.error(er)
		return ''

def get_path(url):
	parsed_url = urlparse(url)
	return parsed_url.path[1:]

if __name__ == '__main__':
	plugin.run()