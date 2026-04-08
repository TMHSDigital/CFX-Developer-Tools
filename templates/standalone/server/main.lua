local Config = Config or {}

AddEventHandler('onResourceStart', function(resourceName)
    if GetCurrentResourceName() ~= resourceName then return end
    print(resourceName .. ' started')
end)
