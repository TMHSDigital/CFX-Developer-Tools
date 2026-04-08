ESX = exports['es_extended']:getSharedObject()

local Config = Config or {}

RegisterNetEvent('myResource:serverEvent', function(data)
    local source = source
    local xPlayer = ESX.GetPlayerFromId(source)

    if not xPlayer then return end

    -- Server logic here
end)
