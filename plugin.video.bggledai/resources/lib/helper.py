# -*- coding: utf-8 -*-
import urllib2, urllib, re, cookielib, os.path, hashlib, time, gzip, base64
from bs4 import BeautifulSoup

class GRequest:
	url = ''
	user_agent_pc = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
	user_agent_desktop = 'TVBG-Chrome-Win32-7849cnsiorhf938hxniyugr96gxuiy4hx938gw483xw9888h7xmh389xm87mh'
	referer = ''
	response = ''
	cookie_file = ''
	cj = cookielib.LWPCookieJar()
	user_logged = False
	
	def __init__(self, plugin):
		self.plugin = plugin
		cookieprocessor = urllib2.HTTPCookieProcessor(self.cj)
		opener = urllib2.build_opener(GPHTTPRedirectHandler, cookieprocessor)
		urllib2.install_opener(opener)
		self.cookie_file = os.path.join(plugin.storage_path, 'coolies')
			
	def Get(self, url, referer=None, ua=None):
		self.ulr = url
		if os.path.isfile(self.cookie_file):
			try: self.cj.load(self.cookie_file)
			except: pass
		

		try:
			req = urllib2.Request(url)
			if ua == None:
				ua = self.user_agent_pc
			req.add_header('User-agent', ua)
			if referer == None:
				referer = url
			req.add_header('Referer', referer)
			
			self.plugin.log.info("GRequest class | url=" + url)
			#try:
			res = urllib2.urlopen(req)
			self.response = res.read()
			res.close()
			self.cj.save(self.cookie_file, ignore_discard=True)
			self.soup = BeautifulSoup(self.response.decode('utf-8', 'ignore'), 'html5lib')
			
			return True
		
		except Exception, er:
			self.plugin.log.error(str(er))
			return False

					
	def Post(self, url, post_data, referer=None):
		self.ulr = url
		if os.path.isfile(self.cookie_file):
			try: self.cj.load(self.cookie_file)
			except: pass
		
		post_data = urllib.urlencode(post_data)
		req = urllib2.Request(url, post_data)
		req.add_header('Referer', referer)
		req.add_header('User-agent', self.user_agent_pc)
		self.plugin.log.info("GRequest class | url=" + url)
		try:
			res = urllib2.urlopen(req)
			self.response = res.read()
			res.close()
			self.cj.save(self.cookie_file, ignore_discard=True)
			return True
		except Exception, er:
			self.plugin.log.info(str(er))
			self.response = ""
			return False

	def UserLogged(self):
		matches = re.compile('title>Login<').findall(self.response)
		return False if len(matches) > 0 else True


	def Login(self, url):
		username = self.plugin.get_setting('username')
		password = self.plugin.get_setting('password')
		if username == '' or password == '':
			return False
		data = { 'user_name':username, 'user_password':password, 'user_rememberme':'1', 'login':'Вход', 'login':'Continue'}
		self.Post(url, data, url)
		return True if self.UserLogged() else False
	
	def DeleteCookie(self):
		try:
			os.remove(self.cookie_file)
		except: 
			self.plugin.log.error(er)
			pass
			
class GPHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
		def http_error_302(self, req, fp, code, msg, headers):
				return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
		http_error_301 = http_error_303 = http_error_307 = http_error_302
				
class Mode:
	show_channels = 'show_channels'
	show_streams = 'show_streams'
	play_stream = 'play_stream'

ul = 'ul'
li = 'li'
div = 'div'
h2 = 'h2'
iframe = 'iframe'
href = 'href'
src = 'src'
label = 'label'
path = 'path'
icon = 'icon'
is_playable = 'is_playable'
all = 'all'