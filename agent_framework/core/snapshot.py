# core/snapshot.py
import copy


class Snapshot:

    def __init__(self, data):
        self.data = copy.deepcopy(data)