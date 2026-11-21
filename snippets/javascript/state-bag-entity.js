// CFX Entity State Bag Pattern (JavaScript)
// Attach persistent data to a networked entity (requires OneSync).
// The two halves below belong in different files: the first in a server
// script, the second in a client script.

// --- server/main.js: set state on the player's current vehicle ---
onNet('myResource:refuel', () => {
    const serverVehicle = GetVehiclePedIsIn(GetPlayerPed(source), false);
    if (serverVehicle === 0) return;
    Entity(serverVehicle).state.set('myResource:fuel', 100.0, true);
});

// --- client/main.js: read state from the current vehicle ---
const clientVehicle = GetVehiclePedIsIn(PlayerPedId(), false);
const fuel = clientVehicle !== 0 ? Entity(clientVehicle).state['myResource:fuel'] : undefined;
