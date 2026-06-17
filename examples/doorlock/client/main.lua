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

-- Returns the nearest configured door within its own distance, or nil. The
-- server re-checks range too; this is just so we send the right id.
local function getNearestDoor()
    local coords = GetEntityCoords(PlayerPedId())
    local nearest, nearestDist = nil, nil
    for _, door in ipairs(Config.Doors) do
        local dist = #(coords - door.coords)
        if dist <= door.distance and (not nearestDist or dist < nearestDist) then
            nearest = door
            nearestDist = dist
        end
    end
    return nearest
end

-- A command + key mapping replaces a per-frame poll, so this resource idles at
-- 0.00ms and players can rebind the key in the FiveM key bindings menu.
RegisterCommand('toggledoor', function()
    local door = getNearestDoor()
    if not door then
        notify('No door within reach.', 'error')
        return
    end
    -- The server is authoritative: it validates range and flips GlobalState.
    TriggerServerEvent('doorlock:server:toggle', door.id)
end, false)
RegisterKeyMapping('toggledoor', 'Toggle the nearest door lock', 'keyboard', Config.ToggleKey)

-- React to the replicated lock state. AddStateBagChangeHandler fires on EVERY
-- client whenever the server writes GlobalState['doorlock:'..id], including the
-- initial seed and for late joiners, so the physical door and notification stay
-- in sync without any polling.
for _, door in ipairs(Config.Doors) do
    AddStateBagChangeHandler('doorlock:' .. door.id, 'global', function(_, _, value)
        local locked = value == true

        -- Drive a physical door only if one is registered with the door system.
        if door.doorHash then
            DoorSystemSetDoorState(door.doorHash, locked and 1 or 0, false, false)
        end

        notify(('%s is now %s.'):format(door.label, locked and 'locked' or 'unlocked'),
            locked and 'error' or 'success')
    end)
end

CreateThread(function()
    resolveFramework()
end)
