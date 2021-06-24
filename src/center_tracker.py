# -*- coding: utf-8 -*-
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


class center_tracker():
    def __init__(self, max_disappeared):
        # A counter used to assign unique ids to each object
        self.nextObjectID = 0
        # A dictionary that has the object id as a key and the center coords as a value
        self.objects = OrderedDict()
        # Maintains number of consecutive frames (value) a particular object ID (key) has been marked as “lost”for
        self.disappeared = OrderedDict()
        # the maximum number of frames that an object is allowed to be marked as lost
        self.maxDisappeared = max_disappeared

    def register(self, center):
        self.objects[self.nextObjectID] = center
        self.disappeared[self.nextObjectID] = 0
        print("printing the objects", self.objects)
        print("printing the disappeared objects", self.disappeared)
        if self.nextObjectID < 9:
            self.nextObjectID += 1

    def unregister(self, objectID):
        # to deregister an object ID we delete the object ID
        del self.objects[objectID]
        del self.disappeared[objectID]
        if self.nextObjectID < 9:
            self.nextObjectID -= 1
        if self.nextObjectID <= 0:
            self.nextObjectID = 0
        print("printing the objects", self.objects)
        print("printing the disappeared objects", self.disappeared)

    def update(self, rects):
        if len(rects) == 0:
            # loop over any existing tracked objects and mark them as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # delete the object if we exceeded the maximum allowed
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.unregister(objectID)

            return self.objects
        # initialize an array for the centers
        input_centers = np.zeros((len(rects), 2), dtype=int)

        # loop over the rectangles
        for (i, (start_x, start_y, end_x, end_y)) in enumerate(rects):
            # calculate the center coords
            c_x = int((start_x + end_x) / 2)
            c_y = int((start_y + end_y) / 2)

            input_centers[i] = (c_x, c_y)

        # If there are no objects not being tracked we register the centers
        if len(self.objects) == 0:
            for i in range(0, len(input_centers)):
                self.register(input_centers[i])
        else:
            # If there are objects being tracked, we grab them
            object_ids = list(self.objects.keys())
            object_centers = list(self.objects.values())
            # we calculate the distance in order to update the coords
            D = dist.cdist(np.array(object_centers), input_centers)
            # we find the smallest value in each row
            rows = D.min(axis=1).argsort()
            # the same for cols
            cols = D.argmin(axis=1)[rows]
            # in order to determine if we need to update, register or unregister we need to keep track of the
            # rows and cols that we have examined
            used_rows = set()
            used_cols = set()
            # we loop over the comb of the (row, col) index tuples
            for (row, col) in zip(rows, cols):
                # if we alredy examined one them ignore it
                if row in used_rows or col in used_cols:
                    continue
                # Otherwise grab the object, update its coords and reset the counter
                object_id = object_ids[row]
                self.objects[object_id] = input_centers[col]
                self.disappeared[object_id] = 0
                # put that used row and col
                used_rows.add(row)
                used_cols.add(col)

            # get the unexamined rows and cols
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)
            # we check here if the input provided has less points than the original one
            if D.shape[0] >= D.shape[1]:
                for row in unused_rows:
                    object_id = object_ids[row]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.maxDisappeared:
                        self.unregister(object_id)
            else:
                for col in unused_cols:
                    self.register(input_centers[col])
        return self.objects
