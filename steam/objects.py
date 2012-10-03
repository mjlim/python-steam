from api import ISteamUser, ISteamApps
from scrape import Store, Community
from util import MetaUniques, _strip_unicode, deprecated



class Game(object):
	__metaclass__ = MetaUniques
	def __init__(self, appid, name = None, user = None, hours = 0.0):
		self.appid = int(appid)
		self.playtime = {}
		self.name = name or ISteamApps.x_GetAppName(self.appid)
		# hack to get rid of non-ascii chars:
		self.name = _strip_unicode(self.name)
		self._update(appid, name, user, hours)

	def _update(self, appid, name = None, user = None, hours = 0.0):
		if user is not None:
			self.playtime[int(user.steamid)] = float(hours)

	def __repr__(self):
		return '<{}[{}]: "{}">'.format(self.__class__.__name__, self.appid, self.name)

	def __str__(self):
		return self.name

	def get_owners(self):
		return self.playtime.keys()

	def get_user_hours(self, *users):
		try:
			return sum(self.playtime[int(u.steamid)] for u in users)
		except KeyError:
			return 0.0

	def get_total_hours(self):
		return sum(self.playtime.itervalues())

	def get_features(self):
		try:
			return self.features
		except AttributeError:
			print 'DEBUG: querying game features for', self.appid, ':', self.name
			self.features = Store.game_features(self.appid)
			return self.features

	def is_multiplayer(self):
		return 'Multi-player' in self.get_features()



class User(object):
	__metaclass__ = MetaUniques

	@classmethod
	def from_username(cls, username):
		return cls(int(ISteamUser.ResolveVanityURL(username)))

	@deprecated('User.from_steamid is redundant, constructor uses steamid directly.')
	@classmethod
	def from_steamid(cls, steamid):
		return cls(int(steamid))

	def __init__(self, steamid):
		self.steamid = steamid
		self.name = ISteamUser.x_ResolveSteamID(steamid)
		self.alias = ISteamUser.x_GetPlayerAlias(steamid)
		self.games = {}
		self.playtime = {}
		self._update(steamid)

	def _update(self, steamid):
		for entry in Community.user_games_list(self.steamid):
			appid = int(entry['appID'])
			try:
				hours = float(entry['hoursOnRecord'].replace(',', ''))
			except KeyError:
				hours = 0.0
			self.games[appid] = Game(appid, entry['name'], self, hours)
			self.playtime[appid] = hours

	def __repr__(self):
		return '<{}[{}]: "{}">'.format(self.__class__.__name__, self.steamid, self.name or self.alias)

	def __str__(self):
		if self.name:
			return self.name
		if self.alias:
			return '"{}"'.format(self.alias)
		return '[{}]'.format(self.steamid)

	def get_playtime(self, g):
		if type(g) is Game: g = int(g.appid)
		try:
			return self.playtime[g]
		except KeyError:
			return 0.0

	def has_game(self, g):
		if type(g) is Game: g = int(g.appid)
		return g in self.games

	def get_most_played(self):
		try:
			return Game(max(self.playtime, key = self.playtime.get))
		except ValueError:
			return None # originally had Game[440] here for TF2

	def get_appids(self):
		return set( int(appid) for appid in self.games.iterkeys() )

	def get_friends(self):
		try:
			return self.friends
		except AttributeError:
			self.friends = ISteamUser.GetFriendList(self.steamid)
			return self.friends
