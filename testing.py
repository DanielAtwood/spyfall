from pprint import pprint
from copy import deepcopy
import random

users = [
    {
        '_id': {
            '$oid': '5aaf029da861ec000699a98d'
        }, 'username': 'Daniel'
    },
    {
        '_id': {
            '$oid': '5aa9d3710db2336cfa1ce483'
        }, 'username': 'Daniel1'
    },
    {
        '_id': {
            '$oid': '5aaf00c70db233e7daaa8665'
        }, 'username': 'incog'
    },
    {
        '_id': {
            '$oid': '5ab3c8541f60ae00063ebd71'
        },
        'username': 'Mobile'
    }
]

location = {
    '_id': {
        '$oid': '5aa9c30a0db23368a4424df4'
    },
    'name': 'Airplane',
    'roles': [
        'Stewardess',
        'Mechanic',
        'First Class Passenger',
        'Economy Class Passenger',
        'Co-Pilot',
        'Captain',
        'Air Marshal'
    ]
}


def assign_roles(users, roles):
    us = deepcopy(users)
    rs = deepcopy(roles)

    spy = random.choice(us)
    spy['role'] = 'Spy'
    us.remove(spy)

    for u in us:
        role = random.choice(rs)
        u['role'] = role
        rs.remove(role)

    us.append(spy)

    return us


pprint(assign_roles(users, location['roles']))
