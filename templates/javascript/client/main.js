// FiveM's JS runtime has no built-in Delay; define it once per file.
const Delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

setTick(async () => {
    await Delay(1000);

    const playerPed = PlayerPedId();
    const playerCoords = GetEntityCoords(playerPed, false);

    // Main client loop
});
