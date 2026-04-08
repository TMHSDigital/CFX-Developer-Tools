local isOpen = false

RegisterNetEvent('myResource:openUI', function()
    if isOpen then return end
    isOpen = true
    SetNuiFocus(true, true)
    SendNUIMessage({ action = 'open' })
end)

RegisterNUICallback('close', function(_, cb)
    isOpen = false
    SetNuiFocus(false, false)
    cb('ok')
end)

RegisterNUICallback('getData', function(data, cb)
    -- handle requests from the UI
    -- data contains whatever the UI sent
    cb({ success = true, items = {} })
end)

RegisterNUICallback('submitAction', function(data, cb)
    -- forward to server if needed
    TriggerServerEvent('myResource:action', data)
    cb('ok')
end)

RegisterCommand('myui', function()
    if isOpen then
        isOpen = false
        SetNuiFocus(false, false)
        SendNUIMessage({ action = 'close' })
    else
        isOpen = true
        SetNuiFocus(true, true)
        SendNUIMessage({ action = 'open' })
    end
end, false)
