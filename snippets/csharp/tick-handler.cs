// CFX Tick Handler Pattern (C#)
// Use Tick handlers for recurring logic. Always await Delay() to yield.
// Never omit the Delay call or the game will freeze.

using System.Threading.Tasks;
using CitizenFX.Core;
using static CitizenFX.Core.Native.API;

public class TickScript : BaseScript
{
    public TickScript()
    {
        Tick += OnTick;
    }

    private async Task OnTick()
    {
        await Delay(1000); // Check every 1 second (adjust as needed)

        int playerPed = PlayerPedId();
        var coords = GetEntityCoords(playerPed, false);

        // Your recurring logic here
    }
}
