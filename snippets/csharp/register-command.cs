// CFX Register Command Pattern (C#)
// Register a chat command. Use the restricted parameter for admin-only commands.

using System;
using System.Collections.Generic;
using CitizenFX.Core;
using static CitizenFX.Core.Native.API;

public class CommandScript : BaseScript
{
    public CommandScript()
    {
        RegisterCommand("mycommand", new Action<int, List<object>, string>((source, args, rawCommand) =>
        {
            if (source > 0)
            {
                // Called by a player. args is empty when the command has no arguments.
                var first = args.Count > 0 ? args[0]?.ToString() : "(none)";
                Debug.WriteLine($"Player {source} used /mycommand with first arg: {first}");
            }
            else
            {
                // Called from server console
                Debug.WriteLine("Command executed from console");
            }
        }), false); // false = not restricted
    }
}
