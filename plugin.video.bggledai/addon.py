# -*- coding: utf-8 -*-
import sys, base64, re
from xbmcswift2 import Plugin
from urlparse import urlparse, urljoin
from resources.lib.helper import *

reload(sys)
sys.setdefaultencoding('utf8')
plugin = Plugin('BG Gledai', 'plugin.video.bggledai')
req = GRequest(plugin)
url = base64.b64decode('aHR0cDovL2JnLWdsZWRhaS50di8=')

	
@plugin.cached_route('/')
def index():
	items = []
	try:
	
		req.Get(url)
		el = req.soup.find(ul, id='menu-gledaitv')
		lis = el.findAll(li)
		del lis[0] # Remove first link, add show all
		
		items.append({label: 'Всички', path: plugin.url_for(Mode.show_channels, id=all)})
		
		for l in lis:
			items.append({
				label: l.a.get_text(),
				path: plugin.url_for(Mode.show_channels, id=get_path(l.a[href]))
			})
	
	except Exception, er:
		plugin.log.error(er)
	return items

@plugin.cached_route('/category/<id>/')
def show_channels(id):
	items = []
	if id == all:
		return get_all_channels()
		
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
		plugin.log.info('iframe_url: ' + iframe_url)
		req.Get(iframe_url, main_url)		
		if not req.UserLogged() and not req.Login(iframe_url):
			plugin.notify(msg=plugin.name, title='Грешка при логването', delay=10000)
			return False
		
		pl_url = get_playlist_url(iframe_url)
		plugin.log.info('Resolved m3u url: %s' % pl_url)
		pl_url += '|Referer=%s' % base64.b64decode('aHR0cDovL3R2YmcudHYvd2luMzIvZmxhc2hwbGF5ZXIvandwbGF5ZXIuZmxhc2guc3dm')
		plugin.set_resolved_url(pl_url)

	except Exception, er:
		plugin.log.error(er)

def get_playlist_url(url):
	try:
		matches = re.compile('playlist: +[\'"]+(.+?)[\'"]+').findall(req.response)
		if len(matches) == 0:
			plugin.log.error('Playlist source url not found!')
			plugin.log.error(req.response)
		pl_url = matches[0]
		if 'http' not in pl_url:
			u = urlparse(url)
			pl_url = '%s://%s/%s' % (u.scheme, u.netloc, matches[0])
		req.Get(matches[0], pl_url)
		matches = re.compile('jwplayer:file>(.+?)<').findall(req.response)
		if len(matches) == 0:
			plugin.log.error('m3u url not found')
			plugin.log.error(req.response)		
		return matches[0]
	except Exception, er:
		plugin.log.error(er)
		return ''

def get_path(url):
	parsed_url = urlparse(url)
	return parsed_url.path[1:]

@plugin.cached(1440)
def get_all_channels():
	items = []
	try:
		from resources.lib.channels import channels
		for i in range (0, len(channels)):
			items.append({
				label : channels[i][0], 
				path : plugin.url_for(Mode.play_stream, id=channels[i][1]),
				icon : urljoin(url, channels[i][2]),
				is_playable : True
			})
	except Exception, er:
		plugin.log.error(er)
	return items

def delete_cache():
	req.DeleteCookie()
	plugin.clear_function_cache()

if __name__ == '__main__':
	plugin.run()