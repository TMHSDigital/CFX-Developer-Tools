// CFX Entity State Bag Pattern (JavaScript)
// Attach persistent data to a networked entity (requires OneSync).

// Server: set state on entity
const vehicle = GetVehiclePedIsIn(GetPlayerPed(source), false);
Entity(vehicle).state.set('myResource:fuel', 100.0, true);

// Client: read state from entity
const vehicle = GetVehiclePedIsIn(PlayerPedId(), false);
const fuel = Entity(vehicle).state['myResource:fuel'];
