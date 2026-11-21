using System;
using CitizenFX.Core;

public class ServerMain : BaseScript
{
    public ServerMain()
    {
        // The delegate's parameters must match the handler: the [FromSource]
        // player first, then the event arguments sent by the client.
        EventHandlers["myResource:serverEvent"] += new Action<Player, object>(OnServerEvent);
    }

    private void OnServerEvent([FromSource] Player player, object data)
    {
        Debug.WriteLine($"Server received event from player: {player.Name}");
    }
}
