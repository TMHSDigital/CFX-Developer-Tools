-- CFX Export Function Pattern
-- Expose a function that other resources can call.
-- Other resources use: exports['your-resource']:GetSomething(param)

exports('GetSomething', function(param)
    -- param: whatever the caller passes in
    -- Return a value back to the caller

    local result = doSomeCalculation(param)
    return result
end)

-- Consuming an export from another resource:
-- local value = exports['other-resource']:GetSomething('test')
