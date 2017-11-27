$(document).ready(function() {
  const socket = io.connect(location.href.slice(0, location.href.search('play') + 4))
  const gameCode = location.href.slice(1-5)
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
    content += '<p class="time"></p><button class="endGame">End Game</button>'
    $('.dynamicContainer').html(content)
    var start = new Date()
    var endTime = new Date(new Date().setMinutes(start.getMinutes()+8))
    updateClock()
    function updateClock() {
      now = new Date()
      var time = endTime.getTime()-now.getTime()
      var minutes = Math.floor( (time/1000/60) % 60 )
      var seconds = ('0'+ Math.floor( (time/1000) % 60 )).slice(-2)
      $('.time').html(minutes+':'+seconds)
      if (minutes == 0 && seconds == 0){
        window.location.reload()
      }
      setTimeout(updateClock, 1000)
    }
    $('.endGame').click(function() {
      socket.emit('endGame', gameCode)
    })
    socket.on('endGame', function() {
      window.location.reload()
    })
  })

})
