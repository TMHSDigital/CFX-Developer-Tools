local Ox = require '@ox_core.lib.init'

local Config = Config or {}

RegisterNetEvent('myResource:serverEvent', function(data)
    local source = source
    local player = Ox.GetPlayer(source)

    if not player then return end

    -- Server logic here
end)
