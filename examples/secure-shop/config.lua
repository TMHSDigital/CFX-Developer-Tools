Config = {}

-- 'auto' resolves ESX or QBCore at runtime. Force with 'esx' / 'qb' / 'standalone'.
Config.Framework = 'auto'

-- Default key for opening / using the shop. Players can rebind it in
-- Settings > Key Bindings > FiveM (RegisterKeyMapping in client/main.lua).
Config.OpenKey = 'E'

-- Where the shop counter is. The client only enables the prompt when near it,
-- but the server does NOT trust proximity from this example - a hardened build
-- would re-check the player's server-side coords against this point.
Config.ShopCoords = vec3(25.7, -1347.3, 29.49) -- 24/7 store, Innocence Blvd

-- Max distance (meters) the player can be from ShopCoords to use the shop.
Config.UseDistance = 2.5

-- The catalogue. THIS is the single source of truth for prices. The price lives
-- on the SERVER (this shared_script is loaded server-side too) and is looked up
-- by `id`. The client never sends a price - only an `id` and a `qty`.
--   id    - stable identifier the client sends to buy
--   label - human-readable name for notifications
--   price - cost PER UNIT, owned by the server
--   item  - inventory item name granted on a successful purchase
Config.Items = {
    { id = 'water',    label = 'Water',         price = 10,  item = 'water' },
    { id = 'sandwich', label = 'Sandwich',      price = 25,  item = 'sandwich' },
    { id = 'phone',    label = 'Burner Phone',  price = 150, item = 'phone' },
}

-- Hard ceiling on quantity per purchase. The server rejects anything above this,
-- so a modded client cannot ask to buy 999999 of something.
Config.MaxQuantity = 10

-- Seconds a player must wait between purchases. Enforced on the SERVER; any
-- client-side cooldown is only a UX nicety and is not trusted.
Config.Cooldown = 1

-- Where money is taken from / inventory is granted to.
--   PayAccount - 'cash' (money) or 'bank' for the deduction.
Config.PayAccount = 'cash'

-- Standalone has no money or inventory backend. When true, standalone treats
-- the player as always able to pay so the example is testable. Leave false in
-- production - standalone is for demos only.
Config.StandaloneAlwaysAfford = true
