import pprint
import os
import random
import re
import eventlet
import subprocess
import json
from flask import Flask, render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from string import ascii_lowercase

if 'ON_HEROKU_SERVER' not in os.environ:
    config_vars = json.loads(subprocess.check_output(
        'heroku config -a spyfallonline --json', shell=True).decode())
    for key, value in config_vars.items():
        os.environ[key] = value

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['MONGO_URI'] = os.environ['MONGODB_URI']

io = SocketIO(app, manage_session=False)
mongo = PyMongo(app)
Session(app)


def re_col(collection):
    return mongo.db[collection]


def start_game(id, players, short_code):
    re_col('games').update_one({'_id': id}, {'$set': {'state': 1}})
    location = [*re_col('locations').aggregate([{'$sample': {'size': 1}}])][0]
    spy_id = random.choice([*players])
    players[spy_id]['role'] = 'Spy'
    assigned = {spy_id: players.pop(spy_id)}

    for index in [*players]:
        player = players.pop(index)
        player['role'] = location['roles'].pop(
            random.randrange(len(location['roles'])))
        assigned[index] = player

    players.update(assigned)
    emit('load_HTML', render_template('game_state_1.html'), room=short_code)
    emit('start_game', (players, location['name']), room=short_code)

    eventlet.spawn_after(60 * 8, end_game, *[id, short_code])


def end_game(id, short_code):
    re_col('players').update_many({'game_id': id}, {'$unset': {'ready': ''}})
    re_col('games').update_one({'_id': id}, {'$set': {'state': 0}})
    emit('load_HTML', render_template('game_state_0.html',
                                      short_code=short_code), room=short_code)
    emit_players(id, short_code)


def leave_game():
    if 'id' in session:
        re_col('players').update_one(
            {'_id': session['id']},
            {'$unset': {'game_id': '', 'ready': ''}},
            upsert=True)
    if 'game_id' in session:
        emit_players(session['game_id'], session['room'])
        del session['game_id']
    if 'room' in session:
        leave_room(session['room'])
        del session['room']


def emit_players(id, short_code):
    cursor = re_col('players').find({'game_id': id})
    for document in cursor: 
        pprint.pprint(document)
    players = {}
    start_ready = True if cursor.count() >= 3 else False
    for player in cursor:
        player_ready = True if 'ready' in player else False
        if player_ready is False:
            start_ready = False
        players[str(player['_id'])] = {
            'username': player['username'], 'ready': player_ready}

    if start_ready:
        start_game(id, players, short_code)
    else:
        if players:
            emit('players', players, room=short_code)
        else:
            re_col('games').delete_one({
                '_id': id
            })


@io.on('connect')
def connect():
    leave_game()
    username = session['username'] if 'username' in session else None
    emit('load_HTML', render_template('set_user.html', username=username))


@io.on('disconnect')
def disconnect():
    print('Disconnected %s %s' % (session['username'], session['id']))
    leave_game()


@io.on('set_user')
def new_user_socket(username):
    leave_game()
    if 'id' in session:
        player_id = session['id']
        re_col('players').update_one(
            {'_id': session['id']},
            {'$set': {'username': username}},
            upsert=True)
    else:
        player_id = re_col('players').insert_one(
            {'username': username}).inserted_id
        session['id'] = player_id

    session['username'] = username

    emit('player_id', str(player_id))
    emit('load_HTML', render_template('join_game.html'))


@io.on('load_join_game')
def load_join_game():
    leave_game()
    emit('load_HTML', render_template('join_game.html'))


@io.on('load_create_game')
def load_create_game():
    leave_game()
    short_code = ''.join(random.sample(ascii_lowercase, 4))
    emit('load_HTML', render_template('create_game.html',
                                      short_code=short_code))


@io.on('join_game')
def join_game(short_code):
    leave_game()
    game = re_col('games').find_one({'short_code': short_code})
    if not game:
        emit('join_error', 'Game does not exist')
    elif game['state'] != 0:
        emit('join_error', 'Game already started')
    else:
        re_col('players').update_one(
            {'_id': session['id']},
            {'$set': {'game_id': game['_id']}},
            upsert=True)
        join_room(short_code)
        session['game_id'] = game['_id']
        session['room'] = short_code
        emit('load_HTML', render_template(
            'game_state_0.html', short_code=short_code))
        emit_players(game['_id'], short_code)


@io.on('ready')
def ready():
    re_col('players').update_one(
        {'_id': session['id']},
        {'$set': {'ready': True}},
        upsert=True)
    emit_players(session['game_id'], session['room'])


@io.on('unready')
def unready():
    re_col('players').update_one(
        {'_id': session['id']},
        {'$unset': {'ready': ''}},
        upsert=True)
    emit_players(session['game_id'], session['room'])


@io.on('create_game')
def create_game(short_code):
    leave_game()
    if re_col('games').find_one({'short_code': short_code}):
        emit('create_error', 'Short code already in use')
    elif re.findall('[^A-Za-z0-9]+', short_code):
        emit('create_error', 'Short code must be alphanumeric')
    else:
        re_col('games').insert_one({'short_code': short_code, 'state': 0})
        join_game(short_code)


@app.route('/')
def start():
    return render_template('start.html')
