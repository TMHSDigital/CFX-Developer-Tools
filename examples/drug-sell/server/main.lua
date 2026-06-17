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

-- How many of `item` the player is holding. 0 if none / unknown.
local function getItemCount(src, item)
    if Framework == 'esx' then
        local xPlayer = FW.GetPlayerFromId(src)
        if not xPlayer then return 0 end
        local inv = xPlayer.getInventoryItem(item)
        return inv and inv.count or 0
    elseif Framework == 'qb' then
        local Player = FW.Functions.GetPlayer(src)
        if not Player then return 0 end
        local has = Player.Functions.GetItemByName(item)
        return has and has.amount or 0
    else
        -- Standalone has no inventory backend. Test-only behaviour.
        return Config.StandaloneInfiniteStock and math.huge or 0
    end
end

-- Returns true if `amount` of `item` was actually removed from the player.
local function removeItem(src, item, amount)
    if Framework == 'esx' then
        local xPlayer = FW.GetPlayerFromId(src)
        if not xPlayer then return false end
        local inv = xPlayer.getInventoryItem(item)
        if not inv or inv.count < amount then return false end
        xPlayer.removeInventoryItem(item, amount)
        return true
    elseif Framework == 'qb' then
        local Player = FW.Functions.GetPlayer(src)
        if not Player then return false end
        local has = Player.Functions.GetItemByName(item)
        if not has or has.amount < amount then return false end
        return Player.Functions.RemoveItem(item, amount)
    else
        return Config.StandaloneInfiniteStock == true
    end
end

local function addMoney(src, amount)
    if Framework == 'esx' then
        local xPlayer = FW.GetPlayerFromId(src)
        if not xPlayer then return end
        if Config.PayAccount == 'bank' then
            xPlayer.addAccountMoney('bank', amount)
        else
            xPlayer.addMoney(amount)
        end
    elseif Framework == 'qb' then
        local Player = FW.Functions.GetPlayer(src)
        if not Player then return end
        Player.Functions.AddMoney(Config.PayAccount == 'bank' and 'bank' or 'cash', amount)
    end
end

-- Server-enforced per-player cooldown. The client cooldown is not trusted: a
-- modded client can fire 'drug-sell:server:sell' as fast as it likes, so the
-- rate limit and the whole outcome live here.
local lastSale = {}

RegisterNetEvent('drug-sell:server:sell', function()
    local src = source
    if not src or src <= 0 then return end

    local now = GetGameTimer()
    if now - (lastSale[src] or 0) < Config.Cooldown * 1000 then
        TriggerClientEvent('drug-sell:client:saleResult', src, 'cooldown')
        return
    end

    -- Sell the first configured drug the player actually holds.
    local drug
    for _, d in ipairs(Config.Drugs) do
        if getItemCount(src, d.item) >= d.amount then
            drug = d
            break
        end
    end
    if not drug then
        TriggerClientEvent('drug-sell:client:saleResult', src, 'empty')
        return
    end

    -- Stamp the cooldown only once a genuine attempt is happening.
    lastSale[src] = now

    local accept = Config.Chances.accept or 0
    local decline = Config.Chances.decline or 0
    local roll = math.random()

    if roll <= accept then
        if not removeItem(src, drug.item, drug.amount) then
            TriggerClientEvent('drug-sell:client:saleResult', src, 'empty', drug.label)
            return
        end
        local price = math.random(drug.minPrice, drug.maxPrice) * drug.amount
        addMoney(src, price)
        TriggerClientEvent('drug-sell:client:saleResult', src, 'sold', drug.label, price)
    elseif roll <= accept + decline then
        TriggerClientEvent('drug-sell:client:saleResult', src, 'declined', drug.label)
    else
        TriggerClientEvent('drug-sell:client:saleResult', src, 'cops', drug.label)
        -- Coords are read server-side (OneSync) so the client cannot spoof them.
        local coords = GetEntityCoords(GetPlayerPed(src))
        TriggerEvent(Config.PoliceAlertEvent, src, { x = coords.x, y = coords.y, z = coords.z })
    end
end)

-- Example dispatch hook. Replace the body with your CAD/dispatch integration;
-- any other resource can also AddEventHandler(Config.PoliceAlertEvent, ...).
AddEventHandler(Config.PoliceAlertEvent, function(playerSrc, coords)
    print(('[drug-sell] Police alert: player %s at %.1f, %.1f, %.1f')
        :format(playerSrc, coords.x, coords.y, coords.z))
end)

-- Stop the cooldown table from growing without bound.
AddEventHandler('playerDropped', function()
    lastSale[source] = nil
end)
