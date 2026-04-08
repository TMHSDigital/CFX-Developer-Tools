local QBX = exports['qbx_core']

local Config = Config or {}

RegisterNetEvent('myResource:serverEvent', function(data)
    local source = source
    local player = QBX:GetPlayer(source)

    if not player then return end

    -- Server logic here
end)
