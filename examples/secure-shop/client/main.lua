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

-- Set by the proximity thread below. The keybind only does anything when true,
-- but note: this is a CLIENT-side gate for UX. The server is what actually
-- protects the purchase - it never trusts that we were really near the shop.
local nearShop = false

local function attemptBuy()
    if not nearShop then
        notify('You are not near the shop.', 'error')
        return
    end

    -- Demo (no NUI): buy 1x the FIRST configured item. We send ONLY an item id
    -- and a quantity. We deliberately do NOT send a price - the server owns
    -- prices and looks them up by id. This is the whole point of the example.
    local first = Config.Items[1]
    if not first then return end

    TriggerServerEvent('secure-shop:server:buy', first.id, 1)
end

-- A command + key mapping replaces a per-frame IsControlJustReleased poll,
-- so the keybind itself idles at 0.00ms and players can rebind the key.
RegisterCommand('secureshop', function()
    attemptBuy()
end, false)
RegisterKeyMapping('secureshop', 'Buy from the secure shop', 'keyboard', Config.OpenKey)

CreateThread(function()
    resolveFramework()
end)

-- Low-frequency proximity thread. It Waits 1000ms when far away and 500ms when
-- close, so it costs almost nothing. It only flips `nearShop` and shows a hint;
-- it never sends anything trusted to the server.
CreateThread(function()
    local hintShown = false
    while true do
        local wait = 1000
        local ped = PlayerPedId()
        local dist = #(GetEntityCoords(ped) - Config.ShopCoords)

        if dist <= Config.UseDistance then
            wait = 500
            nearShop = true
            if not hintShown then
                notify(('Press [%s] to buy %s.'):format(Config.OpenKey, Config.Items[1].label), 'primary')
                hintShown = true
            end
        else
            nearShop = false
            hintShown = false
        end

        Wait(wait)
    end
end)

-- The server is authoritative: it decided whether the purchase succeeded, what
-- it cost, and granted the item. We only translate its verdict into a notify.
--   ok     - boolean success flag
--   reason - 'ok' | 'cooldown' | 'bad_item' | 'bad_qty' | 'no_funds' | 'grant_failed'
--   label  - item label (when known)
--   total  - server-computed price (when known)
RegisterNetEvent('secure-shop:client:buyResult', function(ok, reason, label, total)
    if ok then
        notify(('Bought %s for $%d.'):format(label or 'item', total or 0), 'success')
        return
    end

    if reason == 'cooldown' then
        notify('Slow down a moment.', 'error')
    elseif reason == 'no_funds' then
        notify(('You cannot afford %s ($%d).'):format(label or 'that', total or 0), 'error')
    elseif reason == 'grant_failed' then
        notify('Could not deliver the item - you were refunded.', 'error')
    elseif reason == 'bad_item' then
        notify('That item is not for sale.', 'error')
    elseif reason == 'bad_qty' then
        notify('Invalid quantity.', 'error')
    else
        notify('Purchase failed.', 'error')
    end
end)
