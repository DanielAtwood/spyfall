var socket = io.connect('192.168.140.26:5000/join')

socket.on('updateGames', function(games) {
  content = ''
  if (games) {
    for(var game in games){
      content += '<tr><td><a href="/play/'+game+'">'+game+'</a></td><td>'+games[game]+'/8</td></tr>'
    }
    $('.games').html(content)
  } else {
    $('.games').html('<tr><td class="noGames">No games, make one!</td></tr>')
  }
})
socket.on('newGame', function(gameCode) {
  window.location.href='/play/'+gameCode
})

function newGame() {
  socket.emit('newGame')
}

function privateGame() {
  window.location.href='/play/' + $('.privateGame').val()
  return false
}
