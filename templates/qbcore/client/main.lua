QBCore = exports['qb-core']:GetCoreObject()

local Config = Config or {}

CreateThread(function()
    while true do
        Wait(1000)

        local PlayerData = QBCore.Functions.GetPlayerData()

        -- Main client loop
    end
end)
