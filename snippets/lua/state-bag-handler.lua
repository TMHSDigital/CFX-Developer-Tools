-- CFX State Bag Change Handler
-- React to state changes on any entity or player bag.

AddStateBagChangeHandler('myResource:fuel', nil, function(bagName, key, value, _reserved, replicated)
    local entity = GetEntityFromStateBagName(bagName)
    if entity == 0 then return end

    if replicated then
        -- change came from network; validate if needed
    end

    -- react to the new value
end)
