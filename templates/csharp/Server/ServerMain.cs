using System;
using CitizenFX.Core;

public class ServerMain : BaseScript
{
    public ServerMain()
    {
        EventHandlers["myResource:serverEvent"] += new Action<dynamic>(OnServerEvent);
    }

    private void OnServerEvent([FromSource] Player player, dynamic data)
    {
        Debug.WriteLine($"Server received event from player: {player.Name}");
    }
}
