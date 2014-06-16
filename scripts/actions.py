def resetGame():
  notify('Game reset.  me: {}'.format(me))

def endTurn(player):
  mute()

  for c in table:
    if c.controller != me():
      continue
    if c.properties['type'] == 'Ship':
      c.moveTo(me.Discard)

  for c in me.hand():
    c.moveTo(me.Discard)

  for i in xrange(5):
    drawCard(me.hand)

  if len(players) > 1:
    players[1].setActivePlayer()

def setup(group, x = 0, y = 0):
  mute()

  # Validation
  starting_cards = shared.piles['Starting Cards']
  if len(starting_cards) != 20:
    notify('Not enough cards in the starting cards pile')
    return
  if len(shared.Explorers) != 10:
    notify('Deck doesnt have enough Explorers')
    return
  if len(players) != 2:
    notify('not enough players')
    # return

  # TODO deal out trade row
  shared.Deck.shuffle()
  # TODO set out explorers

  # deal out starting cards
  while len(starting_cards) > 0:
    for player in players:
      for c in starting_cards.top(1): c.moveTo(player.Deck)

  startingPlayer = me

  for player in players:
    player.Deck.shuffle()
    if player == startingPlayer:
      cardCount = 3 
    else:
      cardCount = 5;
    for c in player.Deck.top(cardCount): c.moveTo(player.hand)
  notify('Dealt 3 cards to {} and 5 cards to everyone else'.format(startingPlayer.name))
  startingPlayer.setActivePlayer()


def drawCard(group, count=None):
  mute()
  if len(me.Deck) == 0:
    if (len(me.Discard) == 0):
      notify('{} is out of cards'.format(me))
      return
    for c in me.Discard:
      c.moveTo(me.Deck)
    me.Deck.shuffle()
    notify('{} shuffles their discard into their deck'.format(me))
  me.Deck[0].moveTo(me.hand)
  notify('{} draws a card'.format(me))

def discard(card, x = 0, y = 0):
  mute()
  card.moveTo(me.Discard);
  notify('{} moves {} to their discard'.format(me, card))

def scrap(card, x = 0, y = 0):
  mute()
  card.moveTo(shared.Scrap)
  notify("{} scraps {}".format(me, card))
