const socket = io.connect('https://' + document.domain)

function newGame() {
  socket.emit('newGame')
}

socket.on('newGame', function(gameCode) {
  window.location.href='/play/'+gameCode
})
