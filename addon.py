# -*- coding: utf-8 -*-
import sys, os, base64
from xbmcswift2 import Plugin
from urlparse import urlparse

reload(sys)
sys.setdefaultencoding('utf8')
plugin = Plugin('plugin.video.bggledai')

#append_pydev_remote_debugger
REMOTE_DBG = False
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
	return u.path
	
def request(path = ''):
	res = ''
	try:
		url = 'aHR0cDovL2JnLWdsZWRhaS50di8='
		url = url if path == '' else : url + path
		r = requests.get(base64.b64decode(url))
	except Exception, er:
		plugin.log.error(str(er))
	return res

def request_html(path):
	html = request(path):
	return BeautifulSoup(html.decode('utf-8', 'ignore'), 'html5lib')

@plugin.route('/')
def index():
	items = []
	try:
		soup = request_html('')
		ul = soup.find('ul', id='menu-gledaitv')
		lis = ul.find_all('li')
		for li in lis:
			items.append({
				'label': li.a.get_text(),
				'path': plugin.url_for('show_channels', url=get_path(li.a['href'])
				})				
	except Exception, er:
		plugin.log.error(str(er))
	return items

@plugin.route('/channel/<id>/')
def show_channels(id):
	items = []
	try:
		soup = request_html(id)
		divs = soup.find_all('div', class_='gallerybox')
		for div in divs:
			h2 = div.find('h2')
			title = h2.a.get_text()
			url = get_path(h2.a['href'])
			img = div.find('img')['href']

			items.append({
				'label' : title, 
				'path' : plugin.url_for('play_stream', id=url),
				'icon' : img,
				'is_playable' : True
			})	
	except Exception, er:
		plugin.log.error(str(er))
	return items

@plugin.route('/stream/<id>')
def play_stream(id):
	try:
		soup = request_html(id)
		iframes = soup.find_all('iframe')
		for iframe in iframes:
			if 'freshvideos' in iframe['href']:
				r = requests.get(iframe['href'], headers={'referer': 'http://bg-gledai.tv/'})
				matches = re.compile('playlist: +[\'"]+(.+?)[\'"]+').findall(r.text)
				if len(matches) > 0:
					r = requests.get(matches[0], headers={'referer': iframe['href']})
					matches = re.compile('jwplayer:file>(.+?)<').findall(r.text)
					plugin.setResolvedUrl(matches[0])				
	except Exception, er:
		plugin.log.error(str(er))

if __name__ == '__main__':
	plugin.run()

 
