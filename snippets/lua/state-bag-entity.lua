-- CFX Entity State Bag Pattern
-- Attach persistent data to a networked entity using State Bags (requires OneSync).
-- Server-set state replicates to all clients automatically.

-- Server: set state on entity
local vehicle = GetVehiclePedIsIn(GetPlayerPed(source), false)
Entity(vehicle).state:set('myResource:fuel', 100.0, true)

-- Client: read state from entity
local vehicle = GetVehiclePedIsIn(PlayerPedId(), false)
local fuel = Entity(vehicle).state['myResource:fuel']
