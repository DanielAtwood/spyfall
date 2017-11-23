from flask import Flask, render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit, Namespace, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
import func, os

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = 'secret!'
io = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://kv26ma2q4bmgeihx:zjjdf7zdzly84ng1@p2d0untihotgr5f6.cbetxkdyhwsb.us-east-1.rds.amazonaws.com/hjht9eula9cn9lvy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Games(db.Model):
    __tablename__ = 'games'
    code = db.Column('code', db.Unicode, primary_key = True, unique = True)
    state = db.Column('state', db.Integer, default = 0)
    type = db.Column('type', db.Integer, default = 0)

class Players(db.Model):
    __tablename__ = 'players'
    id = db.Column('id', db.Integer, primary_key = True)
    username = db.Column('username', db.Unicode)
    gameCode = db.Column('gameCode', db.Integer)

def countPlayers():
    return func.countPlayers(Games.query.all(), Players.query.all())

@app.before_request
def make_session_permanent():
    session.permanent = True

@io.on('connect', namespace='/login')
def loginConnection():
    if 'ID' in session:
        player = Players.query.filter_by(id = session['ID']).limit(1).first()
        emit('getPlayerInfo', [player.id, player.username])

@io.on('addPlayer', namespace='/login')
def addPlayer(username):
    player = Players(username=username)
    db.session.add(player)
    db.session.flush()
    session['ID'] = player.id
    db.session.commit()
    print('Added Player')

@io.on('changeUsername', namespace='/login')
def changeUsername(playerInput):
    player = Players.query.filter_by(id = playerInput[0]).limit(1).first()
    player.username = playerInput[1]
    print(playerInput, player.id)
    db.session.commit()

@io.on('connect', namespace='/join')
def joinConnection():
    if 'ID' in session:
        player = Players.query.filter_by(id = session['ID']).limit(1).first()
        if player.gameCode:
            updatePlayers(player.gameCode)
            player.gameCode = None
            db.session.commit()
    updateGames()

@io.on('updateGames', namespace='/join')
def updateGames():
    emit('updateGames', countPlayers(), json=True, broadcast=True, namespace='/join')

@io.on('newGame', namespace='/join')
def newGame():
    gameCode = func.new()
    db.session.add(Games(code = gameCode))
    db.session.commit()
    emit('newGame', gameCode, namespace='/join')

@io.on('joinRoom', namespace='/play')
def joinRoom(gameCode):
    player = Players.query.filter_by(id = session['ID']).limit(1).first()
    player.gameCode = gameCode
    db.session.commit()
    join_room(gameCode)
    updatePlayers(gameCode)
    emit('playerID', session['ID'], namespace='/play')

@io.on('disconnect', namespace='/play')
def playDisconnect():
    if 'ID' in session:
        player = Players.query.filter_by(id = session['ID']).limit(1).first()
        gameCode = player.gameCode
        player.gameCode = None
        db.session.commit()
    updatePlayers(gameCode)

@io.on('updatePlayers', namespace='/play')
def updatePlayers(gameCode):
    players = Players.query.filter_by(gameCode = gameCode).all()
    game = Games.query.filter_by(code = gameCode).limit(1).first()
    if not players and game.state == 1:
        game.state = 0
        db.session.commit()
    else:
        list = []
        for player in players: list.append('<li>%s</li>' % player.username)
        emit('updatePlayers', list, broadcast = True, room = gameCode, namespace = '/play')
    updateGames()

@io.on('startGame', namespace='/play')
def startGame(gameCode):
    assignPlayers = {}
    players = Players.query.filter_by(gameCode = gameCode).all()
    for player in players: assignPlayers[player.id] = None
    game = Games.query.filter_by(code = gameCode).limit(1).first()
    game.state = 1
    db.session.commit()
    emit('startGame', func.assign(assignPlayers), json = True, room = gameCode)
    updateGames()

@app.route('/')
def login():
    if 'ID' in session:
        return render_template('login.html', username = Players.query.filter_by(id = session['ID']).limit(1).first().username)
    return render_template('login.html')

@app.route('/join', strict_slashes=False)
def join():
    return render_template('join.html', games = countPlayers())

@app.route('/play/<gameCode>')
def play(gameCode):
    game = Games.query.filter_by(code = gameCode).limit(1).first()
    if not game: return render_template('gameCode404.html', gameCode = gameCode)
    players = Players.query.filter_by(gameCode = gameCode).all()
    return render_template('play.html', gameCode = gameCode, players = players)

@app.route('/play', strict_slashes=False)
def noGameCode():
    return redirect(url_for('join'))

if __name__ == '__main__':
    io.run(app, debug = False, host = '0.0.0.0', port = int(os.environ.get('PORT', '8000')))
