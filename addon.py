# -*- coding: utf-8 -*-
import sys, os, base64, requests, re
from bs4 import BeautifulSoup
from xbmcswift2 import Plugin
from urlparse import urlparse

reload(sys)
sys.setdefaultencoding('utf8')
plugin = Plugin('plugin.video.bggledai')

#append_pydev_remote_debugger
REMOTE_DBG = True
if REMOTE_DBG:
	try:
		sys.path.append("C:\\Software\\Java\\eclipse-luna\\plugins\\org.python.pydev_4.4.0.201510052309\\pysrc")
		import pydevd
		xbmc.log("After import pydevd")
		#import pysrc.pydevd as pydevd # with the addon script.module.pydevd, only use `import pydevd`
		# stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
		pydevd.settrace('localhost', stdoutToServer=False, stderrToServer=False, suspend=False)
	except ImportError:
		xbmc.log("Error: You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
		sys.exit(1)
	except:
		xbmc.log("Unexpected error:", sys.exc_info()[0]) 
		sys.exit(1)
#end_append_pydev_remote_debugger	


def get_path(url):
	u = urlparse(url)
	return u.path[1:]
	
def request(path = ''):
	res = ''
	try:
		url = base64.b64decode('aHR0cDovL2JnLWdsZWRhaS50di8=')
		url = url if path == '' else url + path
		#plugin.log.info("url: " + url)
		r = requests.get(url)
		res = r.text
	except Exception, er:
		plugin.log.error(str(er))
	return res

def request_html(path):
	html = request(path)
	soup = BeautifulSoup(html.decode('utf-8', 'ignore'), 'html5lib')
	return soup

@plugin.route('/')
def index():
	items = []
	try:
		soup = request_html('')
		ul = soup.find('ul', id='menu-gledaitv')
		lis = ul.findAll('li')
		del lis[0] # Remove first link
		
		for li in lis:
			title = li.a.get_text()
			items.append({
				'label': title,
				'path': plugin.url_for('show_channels', id=get_path(li.a['href']))
			})
	except Exception, er:
		plugin.log.error("index() " + str(er))
	return items

@plugin.route('/category/<id>/')
def show_channels(id):
	items = []
	try:
		soup = request_html(id)
		divs = soup.findAll('div', class_='gallerybox')
		plugin.log.info("found divs: " + str(len(divs)))
		for div in divs:
			h2 = div.find('h2')
			title = h2.a.get_text()
			url = get_path(h2.a['href'])
			try: img = div.a.img['src']
			except: img = ''
			plugin.log.info("img.src: " + img)
			items.append({
				'label' : title, 
				'path' : plugin.url_for('play_stream', id=url),
				'icon' : img,
				'is_playable' : True
			})	
	except Exception, er:
		plugin.log.error("show_channels("+id+") " + str(er))
	return items

@plugin.route('/channels/<id>')
def play_stream(id):
	try:
		soup = request_html(id)
		iframe = soup.find('iframe', src=re.compile('.+freshvideos.+'))
		url = iframe['src']
		
		r = requests.get(url, headers={'referer': 'http://bg-gledai.tv/'})
		matches = re.compile('playlist: +[\'"]+(.+?)[\'"]+').findall(r.text)
		if len(matches) > 0:
			u = urlparse(url)
			pl_url = '%s://%s/%s' % (u.scheme, u.hostname, matches[0])
			r = requests.get(pl_url, headers={'referer': url})
			matches = re.compile('jwplayer:file>(.+?)<').findall(r.text)
			url = matches[0]# + '|User-Agent=stagefright/1.2'
			plugin.set_resolved_url(url)				
	except Exception, er:
		plugin.log.error("play_stream("+id+")" + str(er))

if __name__ == '__main__':
	plugin.run()

 