import random
from config import setup

players = {
    'Kassie': None,
    'Daniel': None,
    'Aron': None,
    'Brandon': None,
    'Nicole': None
}

def assign(players):
    location = random.choice(setup.keys())
    roles = random.sample(setup[location], len(players) - 1)
    assigned = {}
    for index in range(len(players) - 1):
        player = random.choice(players.keys())
        role = random.choice(roles)
        assigned[player] = role
        roles.remove(role)
        del players[player]
    players[players.keys()[0]] = 'Spy'
    players.update(assigned)

assign(players)
