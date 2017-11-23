$(document).ready(function() {
  const socket = io.connect('192.168.140.26:5000/login')
  var id = null
  var username = null

  socket.on('getPlayerInfo', function(player) {
    id = player[0]
    username = player[1]
  })

  $('form').submit(function(e) {
    console.log(id)
    console.log(username)
    var input = $('input').val()
    if (username == null) {
      socket.emit('addPlayer', input)
    } else if (input != username) {
      socket.emit('changeUsername', [id, input])
    }

    window.location.href='/join'
  })
})
