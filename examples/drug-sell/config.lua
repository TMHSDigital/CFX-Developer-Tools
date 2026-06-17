Config = {}

-- 'auto' resolves ESX or QBCore at runtime. Force with 'esx' / 'qb' / 'standalone'.
Config.Framework = 'auto'

-- Key to offer a sale to the nearest valid ped. 38 = E
Config.SellKey = 38

-- Max distance (meters) a ped can be from the player to sell to.
Config.SellDistance = 2.5

-- Seconds the player must wait between sale attempts.
Config.Cooldown = 6

-- Selling is blocked while in a vehicle when true.
Config.RequireOnFoot = true

-- Per-sale outcome chances (must sum to <= 1.0; remainder = ped ignores you).
Config.Chances = {
    accept   = 0.55, -- buys the drug
    decline  = 0.30, -- walks off, no sale
    callCops = 0.15, -- refuses and alerts police
}

-- Police alert: dispatched as a server event you can hook into your CAD/dispatch.
Config.PoliceAlertEvent = 'drug-sell:server:policeAlert'

-- Define your custom drugs here. `item` must match the inventory item name.
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
