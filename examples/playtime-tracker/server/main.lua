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

-- Resolve a STABLE identifier for a player. This is the database primary key,
-- so it must survive reconnects and never change for the same person.
--   - ESX: xPlayer.identifier (already a license/fivem-derived id).
--   - QB:  the citizenid bound to the active character.
--   - standalone: the Rockstar license, which is stable across sessions.
-- Returns nil if the player is not loaded yet (e.g. mid-spawn), in which case
-- callers skip the DB work for that tick.
local function getIdentifier(src)
    if Framework == 'esx' then
        local xPlayer = FW.GetPlayerFromId(src)
        return xPlayer and xPlayer.identifier or nil
    elseif Framework == 'qb' then
        local Player = FW.Functions.GetPlayer(src)
        return Player and Player.PlayerData.citizenid or nil
    else
        -- 'license:xxxxxxxx...'. nil only if the player has already dropped.
        return GetPlayerIdentifierByType(src, 'license')
    end
end

-- In-memory session state keyed by player server id (src).
--   identifier = the resolved DB key for this player
--   baseSeconds = total seconds already persisted in the DB at load time
--   startTimer  = GetGameTimer() value when this session segment started
-- Cleaned up on playerDropped so the table cannot grow without bound.
local sessions = {}

-- Seconds elapsed in the current (unsaved) session segment. GetGameTimer
-- returns milliseconds since resource start; we never trust the client clock.
local function sessionSeconds(session)
    if not session then return 0 end
    return math.floor((GetGameTimer() - session.startTimer) / 1000)
end

-- Persist a player's accumulated time. Uses a PARAMETERISED upsert: the values
-- are passed as the array argument and never concatenated into the SQL string,
-- so the query is immune to injection and is plan-cached by the server.
-- After a successful save we fold the elapsed time into baseSeconds and reset
-- the segment timer, so the next save only writes the new delta.
local function savePlaytime(src)
    local session = sessions[src]
    if not session or not session.identifier then return end

    local elapsed = sessionSeconds(session)
    if elapsed <= 0 then return end

    local total = session.baseSeconds + elapsed
    exports.oxmysql:execute(
        'INSERT INTO player_playtime (identifier, seconds) VALUES (?, ?) '
        .. 'ON DUPLICATE KEY UPDATE seconds = VALUES(seconds), last_seen = CURRENT_TIMESTAMP',
        { session.identifier, total }
    )

    session.baseSeconds = total
    session.startTimer = GetGameTimer()
end

-- Format a raw seconds count as "Hh Mm" (e.g. "3h 07m").
local function formatPlaytime(seconds)
    local hours = math.floor(seconds / 3600)
    local minutes = math.floor((seconds % 3600) / 60)
    return ('%dh %02dm'):format(hours, minutes)
end

-- Begin tracking once the player's character is loaded. We read any existing
-- total with a parameterised scalar query (single column, single row) so a
-- returning player's lifetime keeps accumulating instead of resetting.
local function startSession(src)
    local identifier = getIdentifier(src)
    if not identifier then return end

    exports.oxmysql:scalar_async(
        'SELECT seconds FROM player_playtime WHERE identifier = ?',
        { identifier },
        function(existing)
            sessions[src] = {
                identifier  = identifier,
                baseSeconds = existing or 0,
                startTimer  = GetGameTimer(),
            }
        end
    )
end

-- Framework load hooks. Each fires once the player has a usable identifier.
if Framework == 'esx' then
    RegisterNetEvent('esx:playerLoaded', function(playerId)
        startSession(playerId)
    end)
elseif Framework == 'qb' then
    RegisterNetEvent('QBCore:Server:PlayerLoaded', function(Player)
        startSession(Player.PlayerData.source)
    end)
else
    -- Standalone: no character system, so begin as soon as the player spawns.
    AddEventHandler('playerSpawned', function()
        startSession(source)
    end)
end

-- Periodic flush. Saving on an interval bounds how much playtime is lost if the
-- server stops without a clean drop. Each pass writes only loaded sessions.
CreateThread(function()
    local intervalMs = math.max(1, Config.SaveIntervalMinutes) * 60 * 1000
    while true do
        Wait(intervalMs)
        for src in pairs(sessions) do
            savePlaytime(src)
        end
    end
end)

-- Final flush on disconnect, then drop the session so memory does not leak.
AddEventHandler('playerDropped', function()
    local src = source
    savePlaytime(src)
    sessions[src] = nil
end)

-- /playtime - report the caller's lifetime total (persisted base + current
-- unsaved segment) formatted as "Hh Mm". Server-side so the number is trusted.
RegisterCommand('playtime', function(src)
    if src <= 0 then return end -- ignore the server console
    local session = sessions[src]
    if not session then
        TriggerClientEvent('chat:addMessage', src, {
            args = { '[playtime]', 'Playtime is still loading, try again in a moment.' },
        })
        return
    end

    local total = session.baseSeconds + sessionSeconds(session)
    TriggerClientEvent('chat:addMessage', src, {
        args = { '[playtime]', ('Total playtime: %s'):format(formatPlaytime(total)) },
    })
end, false)
