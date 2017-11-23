$(document).ready(function() {
  const socket = io.connect('https://' + document.domain)
  const gameCode = window.location.pathname.slice(1-5)
  var playerID = null

  socket.emit('joinRoom', gameCode)

  socket.on('playerID', function(ID) {
    playerID = ID
  })

  socket.on('updatePlayers', function(players) {
    $('.players').html(players)
  })

  $('.startGame').click(function() {
    socket.emit('startGame', gameCode)
  })

  socket.on('startGame', function(players, location) {
    var content
    if (players[playerID] == 'Spy') {
      content = '<h1>You are the spy</h1>'
    } else {
      content = '<h1>'+location+'</h1><h3>'+players[playerID]+'</h3>'
    }
    $('body').html(content)
  })
})
