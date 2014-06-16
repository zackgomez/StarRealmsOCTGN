debugMode = False
cardsPlayedThisTurn = 0

neutralMarker = ("Owned By Table", "fabd2965-929e-4ee9-b69c-e278e3cd4098")
actionMarker = ("Action Spent", "2cccc5d7-76e9-4c98-a37b-31d95ef20f3b")
synergyMarker = ("Synergy Action Spent", "c16f45b5-475c-4372-acb8-42da0a189bcc")

def onTableLoad():
  global debugMode
  debugMode = len(players) == 1

def resetGame():
  notify('Game reset.  me: {}'.format(me))

def endTurn(group, x = 0, y = 0):
  mute()

  for c in table:
    if c.controller != me:
      continue
    if c.markers[neutralMarker] > 0:
      continue

    c.markers[actionMarker] = 0;
    c.markers[synergyMarker] = 0;
    if c.properties['type'] == 'Ship':
      c.moveTo(me.Discard)

  for c in me.hand:
    c.moveTo(me.Discard)

  for i in xrange(5):
    drawCard(me.hand)

  if len(players) > 1:
    players[1].setActivePlayer()

  cardsPlayedThisTurn = 0

def setup(group, x = 0, y = 0):
  mute()

  # Validation
  starting_cards = shared.piles['Starting Cards']
  if len(starting_cards) != 20:
    notify('Not enough cards in the starting cards pile')
    return
  if len(shared.piles['Explorers']) != 10:
    notify('Deck doesnt have enough Explorers')
    return
  global debugMode
  if (not debugMode) and len(players) != 2:
    notify('not enough players')
    return

  # TODO deal out trade row
  shared.Deck.shuffle()
  x = -100
  for c in shared.Deck.top(5):
    c.moveToTable(x, 0)
    c.markers[neutralMarker] = 1
    notify('Dealing {} to Trade Row'.format(c))
    x += 100

  # set out explorers
  for c in shared.piles['Explorers']:
    c.moveToTable(-300, 0)
    c.markers[neutralMarker] = 1

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

def playCard(card, x = 0, y = 0):
  mute()
  global cardsPlayedThisTurn
  if not me.isActivePlayer:
    whisper('It is not your turn')
    return
  card.moveToTable(-300 + cardsPlayedThisTurn * 100, 150)
  cardsPlayedThisTurn += 1
  notify('{} plays {}'.format(me, card))

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
  if card.markers[neutralMarker]:
    return
  card.moveTo(me.Discard);
  notify('{} moves {} to their discard'.format(me, card))

def scrap(card, x = 0, y = 0):
  mute()
  if card.markers[neutralMarker]:
    return
  card.moveTo(shared.Scrap)
  notify("{} scraps {}".format(me, card))

def doubleClick(card, x = 0, y = 0):
  mute()
  notify('{} double clicks {}'.format(me, card))

def defaultAction(card, x = 0, y = 0):
  mute()
  if card.markers[neutralMarker]:
    return
  if card.markers[actionMarker] > 0:
    return
  actionText = card.properties['Action']
  if len(actionText) > 0:
    card.markers[actionMarker] = 1
    notify("{} takes action on {}: {}".format(me, card, actionText))

def synergyAction(card, x = 0, y = 0):
  mute()
  if card.markers[neutralMarker]:
    return
  if card.markers[synergyMarker] > 0:
    return
  actionText = card.properties['SynergyAction']
  if len(actionText) > 0:
    card.markers[synergyMarker] = 1
    notify("{} takes synergy action on {}: {}".format(me, card, actionText))

def scrapAction(card, x = 0, y = 0):
  mute()
  if card.markers[neutralMarker]:
    return
  actionText = card.properties['ScrapAction']
  if len(actionText) > 0:
    notify("{} takes scrap action on {}: {}".format(me, card, actionText))
    scrap(card, x, y)
