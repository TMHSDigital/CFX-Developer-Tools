-- CFX Thread Loop Pattern
-- Use this for periodic checks. Adjust Wait() time based on your needs.
-- NEVER use Wait(0) unless you need per-frame execution (drawing, input).

CreateThread(function()
    while true do
        Wait(1000) -- Check every 1 second (adjust as needed)

        local playerPed = PlayerPedId()
        local playerCoords = GetEntityCoords(playerPed)

        -- Your logic here

    end
end)
