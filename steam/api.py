from util import _get_json, _get_json_cached, _get_xml, cachedreturn

API_KEY = '579B676998C7434DAE1C28F2A3DCB67F'

# methods starting with x_ aren't actual API call names.

class _API:
	URL = 'http://localhost:8000'
	@classmethod
	def _api_call(cls, path, **kwargs):
		arguments = '&'.join('{}={}'.format(k,v) for k,v in kwargs.iteritems())
		url = '{}/{}?key={}&{}'.format(cls.URL, path, API_KEY, arguments)
		return _get_json(url)

class ISteamUser(_API):
	URL = 'http://api.steampowered.com/ISteamUser'

	@classmethod
	def GetPlayerSummaries(cls, *steamids):
		result = cls._api_call('GetPlayerSummaries/v0002', steamids=','.join(str(x) for x in steamids))
		return result['response']['players']

	@classmethod
	@cachedreturn(1)
	def x_GetPlayerSummary(cls, steamid):
		# sugar for the 1-case.
		return cls.GetPlayerSummaries(steamid)[0]

	@classmethod
	@cachedreturn(1)
	def x_ResolveSteamID(cls, steamid):
		return cls.x_GetPlayerSummary(steamid)['profileurl'].replace('/', ' ').split()[-1]

	@classmethod
	@cachedreturn(1)
	def x_GetPlayerAlias(cls, steamid):
		return cls.x_GetPlayerSummary(steamid)['personaname']

	@classmethod
	@cachedreturn(1)
	def ResolveVanityURL(cls, username):
		response = cls._api_call('ResolveVanityURL/v0001', vanityurl=username)['response']
		try:
			if int(response['success']):
				return int(response['steamid'])
		except KeyError:
			pass
		return None

	@classmethod
	def GetFriendList(cls, steamid):
		result = cls._api_call('GetFriendList/v1', relationship='friend', steamid=str(steamid))
		return set( int(d['steamid']) for d in result['friendslist']['friends'] )

class ISteamApps(_API):
	URL = 'http://api.steampowered.com/ISteamApps'

	@classmethod
	@cachedreturn(0)
	def GetAppList(cls):
		return dict( (int(g['appid']), g['name']) for g in cls._api_call('GetAppList/v2')['applist']['apps'] )

	@classmethod
	@cachedreturn(1)
	def x_GetAppName(cls, appid):
		return cls.GetAppList()[int(appid)]
