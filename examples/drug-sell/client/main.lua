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

-- The ped we last offered to, so we can play the reaction on the server's verdict.
local pendingPed = nil
-- Local cooldown for snappy feedback only. The server enforces the real one.
local lastAttempt = 0

local function attemptSale()
    if Config.RequireOnFoot and IsPedInAnyVehicle(PlayerPedId(), false) then
        notify('Get out of the vehicle first.', 'error')
        return
    end

    local now = GetGameTimer()
    if now - lastAttempt < Config.Cooldown * 1000 then
        notify('You need to lay low for a moment.', 'error')
        return
    end

    local ped = getNearestPed()
    if not ped then
        notify('No one nearby to sell to.', 'error')
        return
    end

    lastAttempt = now
    pendingPed = ped
    TaskTurnPedToFaceEntity(ped, PlayerPedId(), 1500)
    -- The server picks the drug, rolls the outcome, and moves the money.
    TriggerServerEvent('drug-sell:server:sell')
end

-- A command + key mapping replaces a per-frame IsControlJustReleased poll,
-- so this resource idles at 0.00ms and players can rebind the key.
RegisterCommand('drugsell', function()
    attemptSale()
end, false)
RegisterKeyMapping('drugsell', 'Offer drugs to the nearest ped', 'keyboard', Config.DefaultKey)

CreateThread(function()
    resolveFramework()
end)

-- The server is authoritative: it decides sold / declined / cops and we only
-- play the matching reaction on the ped and notify the player.
RegisterNetEvent('drug-sell:client:saleResult', function(outcome, label, amount)
    local ped = pendingPed
    pendingPed = nil

    if outcome == 'sold' then
        notify(('Sold %s for $%d.'):format(label or 'drugs', amount or 0), 'success')
    elseif outcome == 'declined' then
        notify('They waved you off.', 'error')
        if ped and DoesEntityExist(ped) then
            TaskSmartFleePed(ped, PlayerPedId(), 60.0, -1, false, false)
            SetPedKeepTask(ped, true)
        end
    elseif outcome == 'cops' then
        notify('Wrong customer - they are calling the cops!', 'error')
        if ped and DoesEntityExist(ped) then
            TaskSmartFleePed(ped, PlayerPedId(), 100.0, -1, false, false)
            SetPedKeepTask(ped, true)
        end
    elseif outcome == 'cooldown' then
        notify('You need to lay low for a moment.', 'error')
    elseif outcome == 'empty' then
        notify(('You have no %s to sell.'):format(label or 'drugs'), 'error')
    end
end)
