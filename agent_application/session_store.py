import threading


class SessionStore:

    def __init__(self):
        self.sessions = {}
        self.locks = {}

    def get(self, session_id: str) -> list:
        return self.sessions.get(session_id, [])

    def save(self, session_id: str, messages: list):
        self.sessions[session_id] = messages

    def get_lock(self, session_id: str):
        if session_id not in self.locks:
            self.locks[session_id] = threading.Lock()

        return self.locks[session_id]