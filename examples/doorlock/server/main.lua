-- doorlock server: the authoritative owner of every door's lock state.
--
-- The lock state lives in GlobalState['doorlock:'..id]. GlobalState is a
-- replicated StateBag, so writing it here pushes the value to every client and
-- every late joiner automatically. Clients never write it; they only ask the
-- server to flip it via the 'doorlock:server:toggle' net event.

-- Build an id -> door lookup once so validation is O(1) and we never trust a
-- client-supplied id that is not in the config.
local doorById = {}
for _, door in ipairs(Config.Doors) do
    doorById[door.id] = door
end

-- Seed each door's GlobalState from config on resource start. Doing this from
-- the server guarantees the replicated value exists before any client reads it.
AddEventHandler('onResourceStart', function(resource)
    if resource ~= GetCurrentResourceName() then return end
    for _, door in ipairs(Config.Doors) do
        GlobalState['doorlock:' .. door.id] = door.locked and true or false
    end
end)

-- Server-enforced per-player cooldown. The client keybind can be spammed (or a
-- modded client can fire the event directly), so the rate limit lives here.
local lastToggle = {}
local TOGGLE_COOLDOWN_MS = 500

RegisterNetEvent('doorlock:server:toggle', function(id)
    local src = source
    if not src or src <= 0 then return end

    -- Input validation: the id must be a string and a configured door.
    if type(id) ~= 'string' then return end
    local door = doorById[id]
    if not door then return end

    -- Anti-spam: ignore toggles that arrive faster than the cooldown.
    local now = GetGameTimer()
    if now - (lastToggle[src] or 0) < TOGGLE_COOLDOWN_MS then return end

    -- Range check is done SERVER-side using the player's ped coords (OneSync),
    -- so a modded client cannot toggle a door from across the map.
    local ped = GetPlayerPed(src)
    if ped == 0 then return end
    local coords = GetEntityCoords(ped)
    if #(coords - door.coords) > door.distance then return end

    lastToggle[src] = now

    -- Flip the replicated boolean. Every client's StateBag change handler fires.
    local key = 'doorlock:' .. door.id
    local current = GlobalState[key]
    GlobalState[key] = not current
end)

-- Stop the cooldown table from growing without bound as players leave.
AddEventHandler('playerDropped', function()
    lastToggle[source] = nil
end)
