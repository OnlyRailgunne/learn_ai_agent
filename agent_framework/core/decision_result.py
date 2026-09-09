#decision_result.py
class DecisionResult:

    def __init__(self):
        self.node = None
        self.changes = {}

        self.graph = None
        self.restore_snapshot = None

        self.terminate = False

        self.planning_origin = None

    def add_change(self, key, value):
        self.changes[key] = value
        return True

    def get_change(self, key):
        return self.changes[key]