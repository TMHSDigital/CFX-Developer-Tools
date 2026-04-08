RSGCore = exports['rsg-core']:GetCoreObject()

local Config = Config or {}

RegisterNetEvent('myResource:serverEvent', function(data)
    local source = source
    local Player = RSGCore.Functions.GetPlayer(source)

    if not Player then return end

    -- Server logic here
end)
