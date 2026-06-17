local Framework, FW = nil, nil

local function resolveFramework()
    local choice = Config.Framework
    if choice == 'esx' or (choice == 'auto' and GetResourceState('es_extended') == 'started') then
        Framework = 'esx'
        FW = exports['es_extended']:getSharedObject()
    elseif choice == 'qb' or (choice == 'auto' and GetResourceState('qb-core') == 'started') then
        Framework = 'qb'
        FW = exports['qb-core']:GetCoreObject()
    else
        Framework = 'standalone'
    end
end
resolveFramework()

-- Build an id -> item lookup once. The price comes from HERE, never the client.
local ItemsById = {}
for _, it in ipairs(Config.Items) do
    ItemsById[it.id] = it
end

-- How much money the player has in the configured account. 0 if unknown.
local function getMoney(src)
    if Framework == 'esx' then
        local xPlayer = FW.GetPlayerFromId(src)
        if not xPlayer then return 0 end
        if Config.PayAccount == 'bank' then
            local acc = xPlayer.getAccount('bank')
            return acc and acc.money or 0
        end
        return xPlayer.getMoney()
    elseif Framework == 'qb' then
        local Player = FW.Functions.GetPlayer(src)
        if not Player then return 0 end
        return Player.Functions.GetMoney(Config.PayAccount == 'bank' and 'bank' or 'cash') or 0
    else
        -- Standalone has no money backend. Test-only behaviour.
        return Config.StandaloneAlwaysAfford and math.huge or 0
    end
end

-- Returns true if `amount` was actually removed from the player.
local function removeMoney(src, amount)
    if Framework == 'esx' then
        local xPlayer = FW.GetPlayerFromId(src)
        if not xPlayer then return false end
        if Config.PayAccount == 'bank' then
            local acc = xPlayer.getAccount('bank')
            if not acc or acc.money < amount then return false end
            xPlayer.removeAccountMoney('bank', amount)
            return true
        end
        if xPlayer.getMoney() < amount then return false end
        xPlayer.removeMoney(amount)
        return true
    elseif Framework == 'qb' then
        local Player = FW.Functions.GetPlayer(src)
        if not Player then return false end
        return Player.Functions.RemoveMoney(Config.PayAccount == 'bank' and 'bank' or 'cash', amount, 'secure-shop-purchase')
    else
        return Config.StandaloneAlwaysAfford == true
    end
end

-- Grant `amount` of `item`. Returns true on success.
local function giveItem(src, item, amount)
    if Framework == 'esx' then
        local xPlayer = FW.GetPlayerFromId(src)
        if not xPlayer then return false end
        xPlayer.addInventoryItem(item, amount)
        return true
    elseif Framework == 'qb' then
        local Player = FW.Functions.GetPlayer(src)
        if not Player then return false end
        return Player.Functions.AddItem(item, amount) and true or false
    else
        -- Standalone has no inventory backend; nothing to grant.
        return true
    end
end

-- Server-enforced per-player cooldown. A modded client can fire the buy event
-- as fast as it likes, so the rate limit lives HERE, not on the client.
local lastBuy = {}

--[[ ============================================================================
  SECURITY: WHY EVERY FIELD IS RE-VALIDATED SERVER-SIDE
  ----------------------------------------------------------------------------
  A network event from a client is ATTACKER-CONTROLLED. A cheater can call
  TriggerServerEvent('secure-shop:server:buy', anything, anything) with any
  types and values they want. So this handler trusts NOTHING from the wire:

    1. src > 0          - the event must come from a real connected player.
    2. itemId is string - reject numbers, tables, nil, booleans.
    3. itemId exists    - must be a real id in OUR catalogue (ItemsById).
    4. qty is a number  - reject strings, tables, nil.
    5. qty == qty       - reject NaN (NaN is the only value not equal to itself).
    6. qty finite       - reject inf / -inf (math.huge passes #4 and #5).
    7. qty is integer   - reject 1.5 etc via math.floor comparison.
    8. 1 <= qty <= Max  - reject negative, zero, and absurdly large amounts.

  PRICE IS NEVER ACCEPTED FROM THE CLIENT. We compute total = price * qty using
  the price from OUR config. If we trusted a client-sent price, a cheater would
  simply send price = 0 (or negative) and take items for free, or even gain
  money. Funds are checked and deducted, and the item granted, all server-side.
============================================================================ ]]
RegisterNetEvent('secure-shop:server:buy', function(itemId, qty)
    local src = source

    -- 1. Real player.
    if not src or src <= 0 then return end

    -- Server-side anti-spam. Stamped before heavy work so floods are cheap.
    local now = GetGameTimer()
    if now - (lastBuy[src] or 0) < Config.Cooldown * 1000 then
        TriggerClientEvent('secure-shop:client:buyResult', src, false, 'cooldown')
        return
    end

    -- 2 + 3. itemId must be a string that names a real catalogue entry.
    if type(itemId) ~= 'string' then
        TriggerClientEvent('secure-shop:client:buyResult', src, false, 'bad_item')
        return
    end
    local item = ItemsById[itemId]
    if not item then
        TriggerClientEvent('secure-shop:client:buyResult', src, false, 'bad_item')
        return
    end

    -- 4 - 8. qty must be a finite, positive integer within bounds.
    if type(qty) ~= 'number'
        or qty ~= qty                       -- NaN
        or qty == math.huge or qty == -math.huge
        or math.floor(qty) ~= qty           -- non-integer
        or qty < 1 or qty > Config.MaxQuantity then
        TriggerClientEvent('secure-shop:client:buyResult', src, false, 'bad_qty')
        return
    end

    -- Price comes from OUR config, never the wire.
    local total = item.price * qty

    -- Funds check before taking anything.
    if getMoney(src) < total then
        TriggerClientEvent('secure-shop:client:buyResult', src, false, 'no_funds', item.label, total)
        return
    end

    -- Stamp the cooldown only once a genuine, valid attempt is happening.
    lastBuy[src] = now

    -- Deduct first; only grant the item if the money actually left the account.
    if not removeMoney(src, total) then
        TriggerClientEvent('secure-shop:client:buyResult', src, false, 'no_funds', item.label, total)
        return
    end

    if not giveItem(src, item.item, qty) then
        -- Refund so the player is never charged for an item they did not get.
        if Framework == 'esx' then
            local xPlayer = FW.GetPlayerFromId(src)
            if xPlayer then
                if Config.PayAccount == 'bank' then
                    xPlayer.addAccountMoney('bank', total)
                else
                    xPlayer.addMoney(total)
                end
            end
        elseif Framework == 'qb' then
            local Player = FW.Functions.GetPlayer(src)
            if Player then
                Player.Functions.AddMoney(Config.PayAccount == 'bank' and 'bank' or 'cash', total, 'secure-shop-refund')
            end
        end
        TriggerClientEvent('secure-shop:client:buyResult', src, false, 'grant_failed', item.label, total)
        return
    end

    TriggerClientEvent('secure-shop:client:buyResult', src, true, 'ok', item.label, total)
end)

-- Stop the cooldown table from growing without bound.
AddEventHandler('playerDropped', function()
    lastBuy[source] = nil
end)
