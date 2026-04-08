-- ACE (Access Control Entry) permission checks

-- Check if a player has a specific ACE permission (server only)
if IsPlayerAceAllowed(source, 'myResource.admin') then
    -- player has admin permission
end

-- Register a command that requires an ACE permission
RegisterCommand('admintp', function(source, args)
    -- Only runs if player has 'myResource.teleport' ACE
end, true) -- true = restricted to players with command.admintp ACE

-- server.cfg ACE configuration:
--   add_ace group.admin myResource allow
--   add_ace group.admin command.admintp allow
--   add_principal identifier.license:abc123 group.admin
