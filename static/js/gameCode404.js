const socket = io.connect(location.href.slice(0, location.href.search('play')) + 'join')

function newGame() {
  socket.emit('newGame')
}

socket.on('newGame', function(gameCode) {
  window.location.href='/play/'+gameCode
})
