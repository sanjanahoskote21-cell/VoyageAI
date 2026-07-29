# app/core/limiter.py

from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared Limiter instance — imported by main.py (to register it on the app)
# and by any router that wants to rate-limit specific endpoints.
limiter = Limiter(key_func=get_remote_address)