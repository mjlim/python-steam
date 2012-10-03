from steam import Game, User, cached_games_and_users
from steam.api import ISteamUser
from steam.util import cachedreturn

if __name__ == "__main__":
	import sys

	with cached_games_and_users():
		current_users = set()

		for n in sys.argv[1:]:
			u = User.from_username(n)
			g = u.get_most_played()
			print u, '--', g
			current_users.add(u)
		print ''

		mutual_friends = [ User(i) for i in set.intersection( *(u.get_friends() for u in current_users) ) ]
		if mutual_friends:
			print 'Mutual friends: ', ', '.join(str(u) for u in mutual_friends), '\n'

		candidates = set.intersection( *(u.get_appids() for u in current_users) )
		candidates = filter(Game.is_multiplayer, (Game(a) for a in candidates))

		@cachedreturn(0)
		def interesting_playtime(g):
			return g.get_user_hours(*current_users)

		for g in sorted(candidates, key = interesting_playtime):
			other_players = filter( lambda u: u.has_game(g), mutual_friends )
			print g,
			print '-- {} hours'.format(interesting_playtime(g)),
			if other_players: print '--', ', '.join(str(u) for u in other_players),
			print ''
