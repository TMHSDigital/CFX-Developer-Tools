ESX = exports['es_extended']:getSharedObject()

local Config = Config or {}

CreateThread(function()
    while true do
        Wait(1000)

        local playerData = ESX.GetPlayerData()

        -- Main client loop
    end
end)
