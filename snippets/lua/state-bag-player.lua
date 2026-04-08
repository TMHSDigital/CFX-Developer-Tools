-- CFX Player State Bag Pattern
-- Sync persistent player data using State Bags (requires OneSync).

-- Server: set player state (replicated to all clients)
Player(source).state:set('myResource:job', 'police', true)

-- Client: read own state
local myJob = LocalPlayer.state['myResource:job']

-- Client: read another player's state
local otherJob = Player(serverId).state['myResource:job']
