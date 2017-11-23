import random, string
from config import setup

def new():
    gameCode = ''.join(random.sample(string.ascii_lowercase, 4))
    return gameCode

def assign(players):
    location = random.choice(list(setup))
    roles = random.sample(setup[location], len(players) - 1)
    assigned = {}
    for index in range(len(players)):
        if not roles: break
        player = random.choice(list(players))
        role = random.randint(0, len(roles) - 1)
        assigned[player] = roles[role]
        del roles[role]
        del players[player]
    players[list(players)[0]] = 'Spy'
    players.update(assigned)
    return players, location

def countPlayers(gamesList, players):
    if not gamesList: return None
    hidden = set()
    countedGames = {}
    for game in gamesList:
        if game.type == 1 or game.state == 1:
            hidden.add(game.code)
            continue
        countedGames[game.code] = 0

    for player in players:
        if player.gameCode in hidden: continue
        elif player.gameCode:
            countedGames[player.gameCode] += 1

    return countedGames
