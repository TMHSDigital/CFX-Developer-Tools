// CFX Register Command Pattern (C#)
// Register a chat command. Use the restricted parameter for admin-only commands.

using System;
using CitizenFX.Core;
using static CitizenFX.Core.Native.API;

public class CommandScript : BaseScript
{
    public CommandScript()
    {
        RegisterCommand("mycommand", new Action<int, dynamic, string>((source, args, rawCommand) =>
        {
            if (source > 0)
            {
                // Called by a player
                Debug.WriteLine($"Player {source} used /mycommand with args: {args[0]}");
            }
            else
            {
                // Called from server console
                Debug.WriteLine("Command executed from console");
            }
        }), false); // false = not restricted
    }
}
