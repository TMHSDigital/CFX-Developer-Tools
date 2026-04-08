RSGCore = exports['rsg-core']:GetCoreObject()

local Config = Config or {}

CreateThread(function()
    while true do
        Wait(1000)

        local PlayerData = RSGCore.Functions.GetPlayerData()

        -- Main client loop
    end
end)
