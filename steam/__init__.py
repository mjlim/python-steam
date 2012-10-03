
from objects import *

# steam/
#   api.py
#   scrape.py
#   objects.py
#   util.py

from contextlib import contextmanager

@contextmanager
def _load_and_save(*args):
	for c in args: c._load()
	yield
	for c in reversed(args): c._save()

@contextmanager
def cached_games_and_users():
	with _load_and_save(Game, User):
		yield
