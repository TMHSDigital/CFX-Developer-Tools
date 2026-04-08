-- CFX NUI Callback Pattern
-- Register a callback that the NUI (browser) can invoke via fetch POST.
-- Always call cb() to complete the request.

RegisterNUICallback('actionName', function(data, cb)
    -- data: JSON body from the NUI fetch request
    -- cb: callback function, must be called to resolve the fetch

    print('NUI sent: ' .. tostring(data.someField))

    -- Do your logic here

    cb('ok') -- or cb({ success = true, result = someValue })
end)

-- To open NUI and give it focus:
-- SendNUIMessage({ type = 'open', payload = {} })
-- SetNuiFocus(true, true)

-- To close NUI:
-- SendNUIMessage({ type = 'close' })
-- SetNuiFocus(false, false)
