# -*- coding: utf-8 -*-
from __future__ import print_function

import cv2
from Stitcher.stitcherclass import StitcherClass
import imutils

class stitch:
	def __init__(self):
		self.stitcher = StitcherClass()
		self.total = 0


	def update(self, right, left):
		# resize the frames
		left = imutils.resize(left, width=400, height=225)
		right = imutils.resize(right, width=400, height=225)
		# stitch the frames together to form the panorama
		# IMPORTANT: you might have to change this line of code
		# depending on how your cameras are oriented; frames
		# should be supplied in left-to-right order
		result = self.stitcher.stitch([right, left])
		# no homograpy could be computed
		if result is None:
			print("[INFO] homography could not be computed")
			return None
		self.total += 1
		# gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
		# gray = cv2.GaussianBlur(gray, (11, 11), 0)
		print("[INFO] homography computed, returning the result")
		return result
