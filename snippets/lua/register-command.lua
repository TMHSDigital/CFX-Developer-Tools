-- CFX Register Command Pattern
-- Creates a chat command. Set the third argument to true for admin-only (ACE restricted).

RegisterCommand('mycommand', function(source, args, rawCommand)
    -- source: player server ID (0 on server console)
    -- args: table of space-separated arguments
    -- rawCommand: the full string typed

    if source > 0 then
        -- Called by a player
        TriggerClientEvent('myResource:doSomething', source, args[1])
    else
        -- Called from server console
        print('Command executed from console')
    end
end, false) -- false = not restricted, true = requires ACE permission
