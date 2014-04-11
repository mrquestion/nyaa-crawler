# -*- coding: utf-8 -*-

import sqlite3 as sqlite

from .Tools import Tools

class DatabaseManager:
	CREATE_SQL = "\
		Create table If not exists TORRENT(\
			index_torrent integer,\
			torrent_hash text,\
			torrent_file text,\
			torrent_time text\
		)\
	"
	ADD_SQL = "\
		Insert into TORRENT(\
			index_torrent,\
			torrent_hash,\
			torrent_file,\
			torrent_time\
		)\
		Select\
			ifnull(max(index_torrent), 0)+1,\
			?,\
			?,\
			datetime('now', 'localtime')\
		From\
			TORRENT\
	"
	FIND_SQL = "\
		Select\
			index_torrent\
		From\
			TORRENT\
		Where\
			torrent_hash = ?\
	"
	COUNT_SQL = "Select count(index_torrent) From TORRENT"

	def __init__(self, filename="{}.db".format(Tools.timestamp())):
		if not filename.endswith(".db"):
			filename = "{}.db".format(filename)

		self.filename = filename

		db = sqlite.connect(self.filename)
		db.execute(self.CREATE_SQL)
		db.commit()
		db.close()

	def add(self, filename):
		db = sqlite.connect(self.filename)
		filehash = Tools.md5(filename)
		result = db.execute(self.ADD_SQL, (filehash, filename))
		db.commit()
		db.close()
		return result.rowcount

	def find(self, filename):
		db = sqlite.connect(self.filename)
		filehash = Tools.md5(filename)
		rs = db.execute(self.FIND_SQL, (filehash, ))
		data = rs.fetchone()
		db.close()
		return data

	def count(self):
		db = sqlite.connect(self.filename)
		rs = db.execute(self.COUNT_SQL)
		data = rs.fetchone()
		count = data[0]
		db.close()
		return count