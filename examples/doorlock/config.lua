Config = {}

-- 'auto' resolves ESX or QBCore at runtime for notifications only. The lock
-- logic itself is framework-agnostic. Force with 'esx' / 'qb' / 'standalone'.
Config.Framework = 'auto'

-- Key the player presses to toggle the nearest door. Players can rebind it in
-- Settings > Key Bindings > FiveM (RegisterKeyMapping in client/main.lua).
Config.ToggleKey = 'E'

-- Define your doors here. Each door's lock state is mirrored into GlobalState
-- under the key 'doorlock:'..id, so every client sees the same value.
--   id       - unique string, also forms the StateBag key 'doorlock:'..id
--   label    - shown in notifications
--   doorHash - a GTA door hash registered with the door system (AddDoorToSystem),
--              or nil if you only want logical locking (no physical door).
--   coords   - world position used for the proximity check (client + server)
--   distance - max meters from the door to toggle it
--   locked   - the initial lock state seeded into GlobalState on resource start
Config.Doors = {
    {
        id       = 'ld_front',
        label    = 'Front Door',
        doorHash = nil, -- set to a registered door hash to drive a physical door
        coords   = vec3(-809.83, 175.05, 76.74),
        distance = 2.0,
        locked   = true,
    },
    {
        id       = 'ld_back',
        label    = 'Back Door',
        doorHash = nil,
        coords   = vec3(-802.41, 170.12, 76.74),
        distance = 2.0,
        locked   = true,
    },
}
