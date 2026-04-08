-- CFX Server Event Pattern
-- Register a network event handler on the server side.
-- Always capture source immediately and validate input.

RegisterNetEvent('myResource:serverEvent', function(data)
    local source = source -- capture before any yield

    -- Validate the source is a real player
    if not source or source <= 0 then return end

    -- Validate data types
    if type(data) ~= 'table' then return end

    -- Your server logic here
    print(('Player %d triggered event with data'):format(source))
end)
