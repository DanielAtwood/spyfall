const socket = io.connect('192.168.140.26:5000')

function newGame() {
  socket.emit('newGame')
}

socket.on('newGame', function(gameCode) {
  window.location.href='/play/'+gameCode
})
