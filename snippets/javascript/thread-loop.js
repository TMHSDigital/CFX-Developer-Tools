// CFX Thread Loop Pattern (JavaScript)
// Use setTick for recurring logic. Always await Delay() to yield.
// NEVER use Delay(0) unless you need per-frame execution.

setTick(async () => {
    await Delay(1000); // Check every 1 second (adjust as needed)

    const playerPed = PlayerPedId();
    const playerCoords = GetEntityCoords(playerPed, false);

    // Your logic here
});
