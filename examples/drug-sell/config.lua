Config = {}

-- 'auto' resolves ESX or QBCore at runtime. Force with 'esx' / 'qb' / 'standalone'.
Config.Framework = 'auto'

-- Default key for the sale keybind. Players can rebind it in
-- Settings > Key Bindings > FiveM (RegisterKeyMapping below).
Config.DefaultKey = 'E'

-- Max distance (meters) a ped can be from the player to sell to.
Config.SellDistance = 2.5

-- Seconds the player must wait between sale attempts. Enforced on the SERVER;
-- the client cooldown is only a UX nicety and is not trusted.
Config.Cooldown = 6

-- Selling is blocked while in a vehicle when true.
Config.RequireOnFoot = true

-- Per-sale outcome chances. The remainder (1.0 - accept - decline) is the
-- "calls the cops" chance. The outcome is rolled SERVER-side, not on the client.
Config.Chances = {
    accept  = 0.55, -- buys the drug
    decline = 0.30, -- walks off, no sale
    -- callCops = 0.15 (implied remainder)
}

-- Police alert is dispatched as a SERVER event so your CAD/dispatch resource
-- can hook it: AddEventHandler('drug-sell:server:policeAlert', function(src, coords) ... end)
Config.PoliceAlertEvent = 'drug-sell:server:policeAlert'

-- Standalone has no inventory backend. When true, standalone treats the player
-- as always holding stock so the example is testable. Leave false in production.
Config.StandaloneInfiniteStock = true

-- Define your custom drugs here. `item` must match the inventory item name.
-- The server sells the FIRST drug in this list that the player actually holds.
Config.Drugs = {
    {
        label    = 'Weed Baggie',
        item     = 'weed_baggie',
        minPrice = 40,
        maxPrice = 80,
        amount   = 1,        -- units removed per successful sale
    },
    {
        label    = 'Cocaine',
        item     = 'cocaine_bag',
        minPrice = 120,
        maxPrice = 220,
        amount   = 1,
    },
    {
        label    = 'Meth',
        item     = 'meth_pouch',
        minPrice = 90,
        maxPrice = 160,
        amount   = 1,
    },
}

-- Where cash lands on a sale: 'cash' (money) or 'bank'.
Config.PayAccount = 'cash'
