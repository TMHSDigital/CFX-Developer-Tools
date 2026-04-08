using System;
using System.Threading.Tasks;
using CitizenFX.Core;
using static CitizenFX.Core.Native.API;

public class ClientMain : BaseScript
{
    public ClientMain()
    {
        EventHandlers["myResource:clientEvent"] += new Action<dynamic>(OnClientEvent);
        Tick += OnTick;
    }

    private void OnClientEvent(dynamic data)
    {
        Debug.WriteLine($"Client received: {data}");
    }

    private async Task OnTick()
    {
        await Delay(1000);

        int playerPed = PlayerPedId();
        var coords = GetEntityCoords(playerPed, false);

        // Main client loop
    }
}
