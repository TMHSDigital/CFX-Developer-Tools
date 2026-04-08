local VORPcore = exports.vorp_core:GetCore()

local Config = Config or {}

RegisterNetEvent('myResource:serverEvent', function(data)
    local source = source
    local user = VORPcore.getUser(source)

    if not user then return end

    local character = user.getUsedCharacter

    -- Server logic here
end)
