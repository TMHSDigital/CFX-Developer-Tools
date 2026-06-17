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

local function notify(msg, kind)
    if Framework == 'esx' then
        FW.ShowNotification(msg)
    elseif Framework == 'qb' then
        FW.Functions.Notify(msg, kind or 'primary')
    else
        BeginTextCommandThefeedPost('STRING')
        AddTextComponentSubstringPlayerName(msg)
        EndTextCommandThefeedPostTicker(false, true)
    end
end

-- Returns the nearest pedestrian (non-player, alive) within Config.SellDistance.
local function getNearestPed()
    local playerPed = PlayerPedId()
    local coords = GetEntityCoords(playerPed)
    local handle, ped = FindFirstPed()
    local success, nearest, nearestDist = true, nil, Config.SellDistance

    repeat
        if DoesEntityExist(ped)
            and not IsPedAPlayer(ped)
            and not IsPedDeadOrDying(ped, true)
            and not IsEntityDead(ped) then
            local dist = #(coords - GetEntityCoords(ped))
            if dist < nearestDist then
                nearest = ped
                nearestDist = dist
            end
        end
        success, ped = FindNextPed(handle)
    until not success

    EndFindPed(handle)
    return nearest
end

-- Pick a random drug the player can attempt to sell. The server re-validates inventory.
local function pickDrug()
    return Config.Drugs[math.random(1, #Config.Drugs)]
end

local lastSale = 0

local function attemptSale()
    if Config.RequireOnFoot and IsPedInAnyVehicle(PlayerPedId(), false) then
        return
    end

    local now = GetGameTimer()
    if now - lastSale < Config.Cooldown * 1000 then
        notify('You need to lay low for a moment.', 'error')
        return
    end

    local ped = getNearestPed()
    if not ped then
        notify('No one nearby to sell to.', 'error')
        return
    end

    lastSale = now

    local drug = pickDrug()
    local roll = math.random()
    local pedNet = PedToNet(ped)

    if roll <= Config.Chances.accept then
        notify(('Selling %s...'):format(drug.label), 'primary')
        TaskTurnPedToFaceEntity(ped, PlayerPedId(), 1500)
        Wait(1200)
        TriggerServerEvent('drug-sell:server:sell', drug.item)
    elseif roll <= Config.Chances.accept + Config.Chances.decline then
        notify('They waved you off.', 'error')
        TaskSmartFleePed(ped, PlayerPedId(), 60.0, -1, false, false)
        SetPedKeepTask(ped, true)
    else
        notify('Wrong customer. They are calling the cops!', 'error')
        TaskSmartFleePed(ped, PlayerPedId(), 100.0, -1, false, false)
        SetPedKeepTask(ped, true)
        local coords = GetEntityCoords(PlayerPedId())
        TriggerServerEvent(Config.PoliceAlertEvent, { x = coords.x, y = coords.y, z = coords.z })
    end
end

CreateThread(function()
    resolveFramework()
    while true do
        Wait(0)
        if IsControlJustReleased(0, Config.SellKey) then
            attemptSale()
        end
    end
end)

RegisterNetEvent('drug-sell:client:saleResult', function(ok, label, amount)
    if ok then
        notify(('Sold for $%d.'):format(amount), 'success')
    else
        notify(('You have no %s to sell.'):format(label or 'drugs'), 'error')
    end
end)
