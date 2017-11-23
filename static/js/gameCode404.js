const socket = io.connect('http://' + document.domain + ':' + location.port)

function newGame() {
  socket.emit('newGame')
}

socket.on('newGame', function(gameCode) {
  window.location.href='/play/'+gameCode
})
