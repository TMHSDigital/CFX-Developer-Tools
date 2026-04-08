-- CFX Config Template
-- Place all configurable values here. Never hardcode coordinates,
-- item names, job names, prices, or other tunable values in scripts.
-- This file is typically listed in shared_scripts so both client and server can access it.

Config = {}

Config.Debug = false

Config.Locations = {
    { coords = vector3(200.0, -800.0, 30.0), label = 'Location A' },
    { coords = vector3(400.0, -600.0, 28.0), label = 'Location B' },
}

Config.Blip = {
    sprite = 1,
    color = 2,
    scale = 0.8,
    label = 'My Resource',
}

Config.Permissions = {
    adminOnly = false,
    requiredJob = nil, -- set to a job name string to restrict
}
