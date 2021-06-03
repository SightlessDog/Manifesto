# -*- coding: utf-8 -*-
from __future__ import print_function
from Stitcher.stitcherclass import StitcherClass
import imutils

class stitch:
	def __init__(self):
		self.stitcher = StitcherClass()
		self.total = 0


	def update(self, right, left):
		# resize the frames
		left = imutils.resize(left, width=400)
		right = imutils.resize(right, width=400)
		# stitch the frames together to form the panorama
		# IMPORTANT: you might have to change this line of code
		# depending on how your cameras are oriented; frames
		# should be supplied in left-to-right order
		result = self.stitcher.stitch([left, right])
		# no homograpy could be computed
		if result is None:
			print("[INFO] homography could not be computed")
			return None
		self.total += 1
		return result
