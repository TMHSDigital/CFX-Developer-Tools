-- Compile-time hashing with backticks
-- Replaces GetHashKey() calls with zero-cost compile-time constants

-- BAD: runtime hash on every call
local model_bad = GetHashKey("adder")

-- GOOD: resolved at compile time, zero runtime cost
local model = `adder`

-- Works anywhere a hash is expected
RequestModel(`adder`)
while not HasModelLoaded(`adder`) do
    Wait(10)
end
local vehicle = CreateVehicle(`adder`, pos.x, pos.y, pos.z, heading, true, false)

-- Weapon hashes
GiveWeaponToPed(ped, `WEAPON_PISTOL`, 250, false, true)

-- Animation dictionaries still use strings (backticks are for hashes only)
RequestAnimDict("anim@heists@ornate_bank@grab_cash")
