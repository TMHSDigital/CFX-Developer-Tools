-- Conversion factors from GetEntitySpeed (meters per second) to a display unit.
local MPH = 2.236936
local KMH = 3.6

-- Tracks HUD visibility so we only send a 'display' message when it changes,
-- instead of every loop. NUI traffic is the expensive part, not the Lua.
local hudShown = false
-- Last integer speed we pushed to the NUI, so we only send 'speed' on a change.
local lastSpeed = -1
-- Time of the last 'speed' message, so a steady speed still refreshes at ~10Hz.
local lastSent = 0

-- Convert a raw m/s value to the configured display unit, rounded to an int.
local function toDisplaySpeed(metersPerSecond)
    local factor = (Config.Unit == 'kmh') and KMH or MPH
    return math.floor((metersPerSecond * factor) + 0.5)
end

-- Toggle the HUD, but only message the NUI when the state actually flips.
local function setHud(show)
    if show == hudShown then return end
    hudShown = show
    SendNUIMessage({ action = 'display', show = show })
    if not show then
        -- Reset so the next time we show the HUD it always sends a fresh value.
        lastSpeed = -1
    end
end

-- Single thread for the whole HUD. It paces itself: Wait(0) only while driving,
-- Wait(500) on foot. This keeps the resource near 0.00ms when out of a vehicle.
CreateThread(function()
    while true do
        local ped = PlayerPedId()
        local vehicle = GetVehiclePedIsIn(ped, false)

        if vehicle ~= 0 then
            setHud(true)

            local speed = toDisplaySpeed(GetEntitySpeed(vehicle))
            local now = GetGameTimer()

            -- Rate-limit: only push a 'speed' message when the displayed integer
            -- changes, or at most once every 100ms to keep the readout fresh.
            if speed ~= lastSpeed or (now - lastSent) >= 100 then
                lastSpeed = speed
                lastSent = now
                SendNUIMessage({ action = 'speed', value = speed, unit = Config.Unit })
            end

            Wait(0)
        else
            -- On foot: hide the HUD and idle. No SetNuiFocus is used anywhere
            -- because this is a passive overlay and never captures input.
            setHud(false)
            Wait(500)
        end
    end
end)
