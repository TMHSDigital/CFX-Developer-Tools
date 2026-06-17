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

local function findDrug(item)
    for _, drug in ipairs(Config.Drugs) do
        if drug.item == item then
            return drug
        end
    end
    return nil
end

-- Returns true if the player held >= amount and the item was removed.
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
        -- Standalone: trust nothing, but no inventory backend exists. Treat as held.
        return true
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

RegisterNetEvent('drug-sell:server:sell', function(item)
    local src = source
    if not src or src <= 0 then return end

    local drug = findDrug(item)
    if not drug then return end

    if not removeItem(src, drug.item, drug.amount) then
        TriggerClientEvent('drug-sell:client:saleResult', src, false, drug.label, 0)
        return
    end

    local price = math.random(drug.minPrice, drug.maxPrice) * drug.amount
    addMoney(src, price)
    TriggerClientEvent('drug-sell:client:saleResult', src, true, drug.label, price)
end)

RegisterNetEvent(Config.PoliceAlertEvent, function(coords)
    local src = source
    if not src or src <= 0 then return end
    if type(coords) ~= 'table' or not coords.x then return end
    -- Hook your dispatch/CAD here. Example: notify on-duty police.
    print(('[drug-sell] Police alert from %d at %.1f, %.1f, %.1f'):format(src, coords.x, coords.y, coords.z))
end)
