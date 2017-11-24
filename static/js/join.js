const socket = io.connect(location.href)

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

function newGame() {
  socket.emit('newGame')
}

socket.on('newGame', function(gameCode) {
  window.location.href='/play/'+gameCode
})

function privateGame() {
  window.location.href='/play/' + $('.privateGame').val()
  return false
}
