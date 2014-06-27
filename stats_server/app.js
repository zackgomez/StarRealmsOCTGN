var express = require('express');
var util = require('util')
var levelup = require('levelup')

var db = levelup('./star-realms-octgn-stats.leveldb')

var app = express();

var get_from_db_with_default = function (db, key, default_value, callback) {
  db.get(key, function(err, value) {
    if (err) {
      if (err.notFound) {
        callback(null, default_value);
        return;
      }
      callback(err, null);
    }
    callback(err, JSON.parse(value));
  });
};

var store_in_db = function (db, key, value) {
  db.put(key, JSON.stringify(value), function (err) {
    if (err) {
      console.log('error storing value:', err);
    }
    console.log('wrote', key, '===', value);
  });
};

app.get('/game_start', function(req, res) {
  var num_players = +req.query.num_players;
  if (!num_players) {
    res.send('error: no bad missing nonzero num_players param');
    return;
  }

  log_game({
    num_players: num_players,
  });
  res.send(util.format('success'));
});

var log_game = function (game) {
  util.log(util.format('logging game: %j', JSON.stringify(game)));
  var num_players = game.num_players;
  get_from_db_with_default(db, 'game_count_by_players', {}, function (err, game_count_by_players) {
    if (err) {
      console.log('error getting value from db:', err);
      return;
    }
    if (!game_count_by_players[num_players]) {
      game_count_by_players[num_players] = 0;
    }
    game_count_by_players[num_players] += 1;
    store_in_db(db, 'game_count_by_players', game_count_by_players);
  });
}

var server = app.listen(5000, function() {
  console.log('Listening on port %d', server.address().port);
});
