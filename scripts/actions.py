debugMode = False

shipPlayingX = 0
shipPlayingY = 0
shipPlayingXOffset = 0
shipsPlayedThisTurn = 0

explorerPileX = 0
explorerPileY = 0

neutralMarker = ("Owned By Table", "fabd2965-929e-4ee9-b69c-e278e3cd4098")
actionMarker = ("Action Spent", "2cccc5d7-76e9-4c98-a37b-31d95ef20f3b")
synergyMarker = ("Synergy Action Spent", "c16f45b5-475c-4372-acb8-42da0a189bcc")

explorerModel = '9abd52a8-7310-4527-9234-c2de2ce4c5cc'

CARD_HEIGHT = 120

def onTableLoad():
  global debugMode
  debugMode = len(players) == 1

def resetGame():
  whisper('Inverted? {}'.format(me.hasInvertedTable()))
  global shipPlayingX, shipPlayingY, shipPlayingXOffset
  global explorerPileX, explorerPileY
  shipPlayingX = -300
  shipPlayingXOffset = 100
  shipPlayingY = 150
  explorerPileX = -300
  explorerPileY = 0
  if me.hasInvertedTable():
    shipPlayingX *= -1
    shipPlayingY = -(shipPlayingY + CARD_HEIGHT)
    shipPlayingXOffset *= -1

    explorerPileX *= -1
    explorerPileY = -CARD_HEIGHT

def isLocationInCard(x, y, card):
  cardx, cardy = card.position
  return x >= cardx and x <= cardx + card.width() and y >= cardy and y <= cardy + card.height()

def cardAtLocation(x, y):
  for c in table:
    if isLocationInCard(x, y, c): return c

  return None

def endTurn(group, x = 0, y = 0):
  mute()
  if not me.isActivePlayer:
    whisper('It is not your turn')
    return

  global shipsPlayedThisTurn
  shipsPlayedThisTurn = 0
  notify('{} ends turn with Trade: {} Combat: {}'.format(me, me.counters['Trade'].value, me.counters['Combat'].value));
  me.counters['Trade'].value = 0
  me.counters['Combat'].value = 0

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

  if len(players) < 2:
    return

  activePlayer = players[1]
  activePlayer.setActivePlayer()

  for c in table:
    if c.markers[neutralMarker] > 0:
      cardx, cardy = c.position
      if activePlayer.hasInvertedTable():
        cardy = -c.height()
      else:
        cardy = 0
      c.moveToTable(-cardx, cardy)
      c.setController(activePlayer)
  shared.Deck.setController(activePlayer)
  shared.Scrap.setController(activePlayer)

def setup(group, x = 0, y = 0):
  mute()

  # Validation
  startingCards = shared.piles['Starting Cards']
  if len(startingCards) != 20:
    notify('Not enough cards in the starting cards pile')
    return
  if len(shared.piles['Explorers']) != 10:
    notify('Deck doesnt have enough Explorers')
    return
  global debugMode
  if (not debugMode) and len(players) != 2:
    notify('not enough players')
    return

  shared.Deck.setController(me)
  shared.Scrap.setController(me)
  shared.piles['Explorers'].setController(me)
  startingCards.setController(me)

  # deal out trade row
  whisper('Setting out Trade Row')
  shared.Deck.shuffle()
  x = -100
  y = 0
  xincr = 100
  if me.hasInvertedTable():
    x = -x
    y = -CARD_HEIGHT
    xincr = -xincr
  for i in xrange(5):
    replaceTradeCard(x, y)
    x += xincr

  # set out explorers
  whisper('Setting out Explorer pile')
  for c in shared.piles['Explorers']:
    c.moveToTable(explorerPileX, explorerPileY)
    c.markers[neutralMarker] = 1

  # deal out starting cards
  whisper('Dealing out starting decks')
  while len(startingCards) > 0:
    for player in players:
      for c in startingCards.top(1): c.moveTo(player.Deck)

  startingPlayer = me

  whisper('Dealing starting hands')
  for player in players:
    if player == startingPlayer:
      cardCount = 3 
    else:
      cardCount = 5;
    remoteCall(player, 'remoteDrawStartingHand', [cardCount])
  update()

  notify('{} plays first'.format(startingPlayer))
  startingPlayer.setActivePlayer()

def remoteDrawStartingHand(numCards):
  mute()
  me.Deck.shuffle()
  for c in me.Deck.top(numCards): c.moveTo(me.hand)
  notify('{} drew {} cards for as their starting hand'.format(me, numCards))

def moveBaseToTable(base):
  sign = -1 if me.hasInvertedTable() else 1
  baseX = shipPlayingX
  baseY = shipPlayingY + sign * (base.height() + 1)
  xincr = sign * base.height() * 1.25

  while cardAtLocation(baseX, baseY) != None:
    baseX += xincr
  base.moveToTable(baseX, baseY)
  base.orientation = Rot90

def playCard(card, x = 0, y = 0):
  mute()
  global shipsPlayedThisTurn
  if not me.isActivePlayer:
    whisper('It is not your turn')
    return
  notify('{} plays {}'.format(me, card))
  if card.properties['Type'] == 'Base':
    moveBaseToTable(card)
  elif card.properties['Type'] == 'Ship':
    card.moveToTable(shipPlayingX + shipPlayingXOffset * shipsPlayedThisTurn, shipPlayingY)
    shipsPlayedThisTurn += 1
    defaultAction(card)
  else:
    whisper('Error: unknown card type {}'.format(card.properties['Type']))

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
  scrapImpl(card)

def doubleClick(card, x = 0, y = 0):
  mute()
  if card.markers[neutralMarker]:
    buyTradeCard(card, x, y)
  elif card.controller != me:
    whisper('that card belongs to another player')
    return
  elif card.markers[actionMarker] == 0 and len(card.properties['Action']) > 0:
    defaultAction(card, x, y)
  elif card.markers[actionMarker] == 1 and len(card.properties['SynergyAction']) > 0:
    synergyAction(card, x, y)
  else:
    return

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
    scrapImpl(card)

def replaceTradeCard(x, y):
  mute()
  if len(shared.Deck) == 0:
    notify('Deck is out of cards')
    return
  for c in shared.Deck.top(1):
    c.moveToTable(x, y)
    c.markers[neutralMarker] = 1
    update()
    notify('Added {} to trade row'.format(c))

def scrapTradeCard(card, x = 0, y = 0):
  mute()
  if card.markers[neutralMarker] != 1:
    whisper('That card is not a trade card.')
    return
  if card.model == explorerModel:
    whisper('Explorers are not in the trade row.')
    return

  notify("{} scraps trade card {}".format(me, card))
  cardX, cardY = card.position
  scrapImpl(card)
  replaceTradeCard(cardX, cardY)

def buyTradeCard(card, x = 0, y = 0):
  mute()
  if card.markers[neutralMarker] != 1:
    whisper('That card is not a trade card.')
    return

  cost = int(card.properties['Cost'])
  notify('{} purchased card {} for {}'.format(me, card, cost))
  me.counters['Trade'].value -= cost
  cardX, cardY = card.position
  card.moveTo(me.Discard)

  if card.model != explorerModel:
    replaceTradeCard(cardX, cardY)

def scrapImpl(card):
  removeMarkers(card)
  if card.model == explorerModel:
    card.moveToTable(explorerPileX, explorerPileY)
    card.markers[neutralMarker] = 1
    update()
    notify('{} returns {} to the supply'.format(me, card))
  else:
    card.moveTo(shared.Scrap)
    update()
    notify('{} scraps {}'.format(me, card))

def removeMarkers(card):
  card.markers[neutralMarker] = 0
  card.markers[actionMarker] = 0
  card.markers[synergyMarker] = 0
