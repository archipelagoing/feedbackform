from collections import OrderedDict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException


class LoginLimiter:
    """Bounded single-process limiter. Hosting behind proxies needs separate configuration."""

    def __init__(self, attempts=20, window=60):
        self.attempts, self.window = attempts, window
        self.peers = OrderedDict()
        self.lock = Lock()

    def check(self, peer: str):
        now = monotonic()
        with self.lock:
            events = self.peers.pop(peer, deque())
            while events and events[0] <= now - self.window:
                events.popleft()
            self.peers[peer] = events
            if len(self.peers) > 1024:
                self.peers.popitem(last=False)
            if len(events) >= self.attempts:
                raise HTTPException(
                    429,
                    "Too many sign-in attempts. Try again in a minute.",
                    headers={"Retry-After": str(self.window)},
                )
            events.append(now)
