# -*- coding: utf-8 -*-
class PersonTrackable:
    def __init__(self, object_id, center):
        # Store the object_id of the person that we are tracking and initialize a list of centers
        self.object_id = object_id
        self.centers = [center]

        # Boolean indicating if we are tracking the object or not
        self.counted = False
