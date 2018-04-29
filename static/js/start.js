const socket = io.connect(location.href)
var id = ''
var timer_id

function set_user() {
  socket.emit('set_user', $('.username_input').val())
}
function join_game() {
  socket.emit('join_game', $('.short_code_input').val())
}
function create_game() {
  var short_code = $('.create_game_shortcode').val()
  if (short_code.length < 4) {
    $('.create_error').text('Short code must be atleast 4 characters')
  } else if (short_code.match('[^A-Za-z0-9]')) {
    $('.create_error').text('Short code must be alphanumeric')
  } else {
    socket.emit('create_game', short_code)
  }
}

function toggle_ready(button) {
  if (button.text() == 'Ready') {
    button.text('Unready')
    socket.emit('ready')
  }
  else {
    button.text('Ready')
    socket.emit('unready')
  }
}

socket.on('player_id', (set_id) => {
  id = set_id
})

socket.on('load_HTML', (html) => {
  clearTimeout(timer_id)
  $('.content').html(html)
  $('input').focus()

  $('.username_submit').click(() => {
    set_user()
  })

  $('.username_input').keypress((e) => {
    if (e.key == 'Enter') {
      set_user()
    }
  })

  $('.load_join_game').click(() => {
    socket.emit('load_join_game')
  })

  $('.load_create_game').click(() => {
    socket.emit('load_create_game')
  })

  $('.join_game').click(() => {
    join_game()
  })

  $('.short_code_input').keydown((e) => {
    $('.join_error').text('')
    if (e.key == 'Enter' && $('.short_code_input').val()) { join_game() }
  })

  $('.create_game').click(() => {
    create_game()
  })
  $('.create_game_shortcode').keydown((e) => {
    $('.create_error').text('')
    if (e.key == 'Enter') { create_game() }
  })

  $('.ready_button').click(() => {
    toggle_ready($('.ready_button'))
})
})

socket.on('join_error', (error) => {
  $('.join_error').text(error)
})

socket.on('create_error', (error) => {
  $('.create_error').text(error)
})

socket.on('players', (players) => {
  console.log(players)
  var table = []
  for (var index in players) {
    var player = players[index]
    var cells = ['<td class="username">' + player['username'] + '</td>']
    if (player['ready']) { cells.push('<td class="ready"><i class="material-icons">check</i></td>') }
    var row = '<tr id="' + id + '">' + cells + '</tr>'
    table.push(row)
  }
  $('.players tbody').empty().append(table)
})

socket.on('start_game', (players, location) => {
  role = players[id]['role']
  if (role == 'Spy') {
    $('.location').text('You are the Spy')
    $('.role').remove()
  } else {
    $('.location').text(location)
    $('.role').text(role)
  }
  var table = []
  for (var index in players) {
    if (index != id) {
      var player = players[index]
      var cell = '<td class="username">' + player['username'] + '</td>'
      table.push('<tr>' + cell + '</tr>')
    }
    $('.players tbody').empty().append(table)
  }
  var start = new Date()
  var endTime = new Date(new Date().setMinutes(start.getMinutes() + 8))

  function updateClock() {
    now = new Date()
    var time = endTime.getTime() - now.getTime()
    var minutes = Math.floor((time / 1000 / 60) % 60)
    var seconds = ('0' + Math.floor((time / 1000) % 60)).slice(-2)
    $('.time').text(minutes + ':' + seconds)
    if (minutes == 0 && seconds == 0) { clearTimeout(timer_id) }
    timer_id = setTimeout(updateClock, 1000)
  }
  updateClock()
})
