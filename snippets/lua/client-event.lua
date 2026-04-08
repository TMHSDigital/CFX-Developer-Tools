-- CFX Client Event Pattern
-- Register a network event handler on the client side.
-- The event can be triggered from the server with TriggerClientEvent.

RegisterNetEvent('myResource:clientEvent', function(data)
    -- data: whatever the server sent
    -- Do NOT trust this data blindly on the client either;
    -- but critical validation belongs on the server.

    print('Received data: ' .. tostring(data))
end)
