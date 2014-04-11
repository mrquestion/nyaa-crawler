# -*- coding: utf-8 -*-

import sys

from nyaa import Nyaa

def main(argc, args):
	nyaa = Nyaa()
	words = nyaa.getwords()
	if nyaa.check():
		count = nyaa.words(words, ismp=True)
		#count = nyaa.words(words)

if __name__ == "__main__":
	main(len(sys.argv), sys.argv)