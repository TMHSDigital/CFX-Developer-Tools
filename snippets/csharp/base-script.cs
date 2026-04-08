// CFX Base Script Pattern (C#)
// All FiveM/RedM C# scripts extend BaseScript from CitizenFX.Core.
// Register event handlers in the constructor and use async Tick for loops.

using System;
using System.Threading.Tasks;
using CitizenFX.Core;
using static CitizenFX.Core.Native.API;

public class MyScript : BaseScript
{
    public MyScript()
    {
        EventHandlers["myResource:clientEvent"] += new Action<dynamic>(OnClientEvent);
        Tick += OnTick;
    }

    private void OnClientEvent(dynamic data)
    {
        Debug.WriteLine($"Received event with data: {data}");
    }

    private async Task OnTick()
    {
        await Delay(1000); // Yield every second - NEVER skip Delay in Tick

        // Your recurring logic here
    }
}
