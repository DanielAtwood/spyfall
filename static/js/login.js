$(document).ready(function() {
  const socket = io.connect(location.href + 'login')
  var id = null
  var username = null

  socket.on('getPlayerInfo', function(player) {
    id = player[0]
    username = player[1]
  })

  $('form').submit(function(e) {
    var input = $('input').val()
    if (username != input) {
      socket.emit('changeUsername', [id, input])
    }
    location.href='/join'
  })
})
