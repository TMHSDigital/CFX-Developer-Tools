-- Lua 5.4 variable attributes: <const> and <close>

-- <const>: prevents reassignment (compile-time check)
local MAX_SLOTS <const> = 40
local RESOURCE_NAME <const> = GetCurrentResourceName()

-- MAX_SLOTS = 50  --> ERROR: attempt to assign to const variable

-- <close>: calls __close metamethod when variable goes out of scope
local function readJsonFile(path)
    local file <close> = io.open(path, 'r')
    if not file then return nil end
    local content = file:read('*a')
    -- file:close() is called automatically here
    return content
end

-- <close> with custom cleanup (e.g., temporary entities)
local function withTemporaryBlip(coords, fn)
    local blip <close> = setmetatable(
        { handle = AddBlipForCoord(coords.x, coords.y, coords.z) },
        { __close = function(self) RemoveBlip(self.handle) end }
    )
    fn(blip.handle)
    -- blip is removed automatically when this function returns
end
