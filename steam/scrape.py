from util import _get_soup, _get_soup_cached, _get_xml, cachedreturn, deprecated
import json

import os
import time

class Store:
	URL = 'http://store.steampowered.com/app/'

	@classmethod
	@cachedreturn(1)
	def game_name(cls, appid):
		soup = _get_soup_cached( '{}/{}/'.format(cls.URL, appid) )
		for row in soup('div', {'class' : 'apphub_AppName'}):
			return row.text
		return 'Half-Life 3'

	# the generator isn't cachedreturn, but the frozenset below it is.
	@classmethod
	def _game_features(cls, appid):
		soup = _get_soup_cached( '{}/{}/'.format(cls.URL, appid) )
		for row in soup('div', {'class' : 'game_area_details_specs'}):
			for child in row('div', {'class': 'name'}):
				yield child.text

	@classmethod
	@cachedreturn(1)
	def game_features(cls, appid):
		return frozenset(cls._game_features(appid))

class CommunityHTML:
	URL = 'http://steamcommunity.com/id/'

	@deprecated('XML-based Community class is preferred.')
	@classmethod
	def user_games_list(cls, username):
		soup = _get_soup( '{}/{}/games?tab=all'.format(cls.URL, username) )
		for js in soup('script'):
			if js.text[:14] == 'var rgGames = ':
				encoded = js.text.splitlines()[0][14:-1]
				return json.loads(encoded)
		return []


class Community:
	URL = 'http://steamcommunity.com'

	@classmethod
	def _xml_call(cls, path, steamid, **kwargs):
		arguments = '&'.join('{}={}'.format(k,v) for k,v in kwargs.iteritems())
		url = '{}/profiles/{}/{}?xml=1&{}'.format(cls.URL, steamid, path, arguments)
		return _get_xml(url)

	@classmethod
	def user_games_list(cls, steamid):
		try:
			result = cls._xml_call('games', steamid, tab='all')['gamesList']['games']['game']
			if type(result) is not list:
				return [result]
			return result
		except (KeyError, TypeError):
			# (private profile, no games owned) respectively
			return []

	@classmethod
	def user_friends_list(cls, steamid):
		try:
			result = cls._xml_call('friends', steamid)['friendsList']['friends']['friend']
			if type(result) is not list:
				return set( [int(result)] )
			return set( int(r) for r in result )
		except (KeyError, TypeError):
			return set()

	@classmethod
	@cachedreturn(1)
	def user_alias(cls, steamid):
		url = '{}/profiles/{}/?xml=1'.format(cls.URL, steamid)
		return _get_xml_cached(url)['profile']['steamID']

	@classmethod
	@cachedreturn(1)
	def user_name_from_id(cls, steamid):
		url = '{}/profiles/{}/?xml=1'.format(cls.URL, steamid)
		return _get_xml_cached(url)['profile']['customURL'] or ''

	@classmethod
	@cachedreturn(1)
	def user_id_from_name(cls, username):
		url = '{}/id/{}/?xml=1'.format(cls.URL, username)
		return int(_get_xml_cached(url)['profile']['steamID64'])
