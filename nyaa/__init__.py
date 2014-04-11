# -*- coding: utf-8 -*-

import os
import time
import json
import requests
import subprocess as sp
import multiprocessing as mp
from bs4 import BeautifulSoup as bs

from .Tools import Tools
from .Log import Log as L
from .DatabaseManager import DatabaseManager

class Nyaa:
	BASEDIR = "torrents"
	NAME = "nyaa"
	WORDFILE = "nyaa-words.json"
	URL = "http://www.nyaa.se/?page=rss&term={}"

	def __init__(self, basedir=BASEDIR, savedir=None, dm=None):
		mp.freeze_support()

		if not os.path.exists(basedir):
			os.mkdir(basedir)

		if not savedir:
			self.time = Tools.timestamp()
			savedir = os.sep.join((basedir, self.time))
			if not os.path.exists(savedir):
				os.makedirs(savedir, exist_ok=True)
		self.savedir = savedir
		
		if dm: self.dm = dm
		else: self.dm = DatabaseManager(self.NAME)

		l = self.l = L(filename="Torrent.log", filepath=savedir)

		l.og(Tools.getlogo("nyaa.se Torrent Crawler"), sep=os.linesep)

	def getwords(self, filename=WORDFILE):
		l = self.l

		if not filename.endswith(".json"):
			filename = '.'.join(filename, "json")

		l.og("[Word] Load from '{}'...".format(filename))
		if os.path.exists(filename):
			ro = open(filename, "r")
			try:
				words = json.loads(ro.read())
				if type(words) is list:
					l.og("\t{} word{} loaded.".format(len(words), 's' if len(words) > 1 else ''), os.linesep)
					return words
			except Exception as e:
				l.og("Error: json.loads()")
				l.og("\t{}".format(e))
		else: l.og("\t'{}' file not exists.".format(filename))

	def words(self, words, ismp=False):
		l = self.l

		if type(words) is list:
			t = time.time()
			total = 0
			if ismp:
				pools = mp.Pool(processes=mp.cpu_count())
				map = pools.map(self.mpword, words)
				total = sum(count for count in map if type(count) is int)
			else:
				for word in words:
					count = self.word(word)
					l.og(word, count)
					total = total + count if type(count) is int else 0
			l.og()

			l.og("[Result]")
			l.og("\tTotal:", total)
			l.og("\tElapsed:", time.time()-t)
			l.og()

			l.og("[Total Result]")
			l.og("\t{} word{} done.".format(len(words), 's' if len(words) > 1 else ''))
			l.og("\tTotal data in '{}':".format(self.dm.filename), self.dm.count())

			return total
		else: l.og("\tWords is not list")
	
	def mpword(self, word):
		return self.word(word, ismp=True)

	def word(self, word, ismp=False):
		l = self.l

		if ismp: l.og("[Search #{}] {}".format(mp.current_process().name.replace("PoolWorker-", ''), word))
		else: l.og("[Search]", word)

		list = self.search(word)

		count = 0
		if ismp and False:
			# TODO
			pass
		else:
			for x in list:
				if not self.dm.find(x["file"]):
					if self.download(x["url"], x["file"]): count = count + 1

		return count

	def check(self):
		l = self.l

		l.og("[Check] Connection check...", linesep=False)
		url = self.URL.format("test")
		response = requests.get(url)
		self.checked = response.ok
		l.og(self.checked)
		l.og()

		if not response.ok:
			l.og("Error: requests.get()")
			l.og("\t{} {}".format(response.status_code, response.reason))

		return self.checked

	def search(self, word):
		l = self.l

		word = str(word)
		word = word.replace(' ', '+')
		url = self.URL.format(word)
		response = requests.get(url)
		self.checked = response.ok
		if response.ok:
			dom = bs(response.content)
			items = dom.findAll("item")

			list = []
			for item in items:
				link = item.link.text
				filename = "{}.torrent".format(Tools.normalize(item.title.string))
				list.append({ "url": link, "file": filename })
			return list
		else: l.og("Error: Connection is unstable.")

	def download(self, url, filename):
		l = self.l

		if not os.path.exists(self.savedir):
			os.makedirs(self.savedir, exist_ok=True)
		filepath = os.sep.join((self.savedir, filename))

		l.og("\t[Download]", filename)

		response = requests.get(url)
		if response.ok:
			try:
				rbo = open(filepath, "wb")
				rbo.write(response.content)
				rbo.close()

				self.dm.add(filename)

				return True
			except Exception as e:
				l.og("Error: Failed to save file.")
				l.og("\t{}".format(e))
		else: l.og("Error: Connection is unstable.")
		'''
		p = sp.Popen("wget.exe \"{}\" -O \"{}\" -q".format(url, filepath))
		p.wait()
		if p.returncode == 0:
			self.dm.add(filename)
			return True
			'''