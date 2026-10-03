-- CFX Verified Payment Callback Pattern (server only)
-- Safely grant an item when an external payment provider (Tebex, a webhook
-- relay, any service that signs its callbacks) notifies your resource.
-- Needs oxmysql. Provider-neutral: adapt the header names and payload fields.
--
-- Checks performed, in order:
--   1. HMAC-SHA256 signature over "<timestamp>.<body>" (secret from a convar)
--   2. Timestamp freshness (rejects old, replayed requests)
--   3. Idempotency (a repeated event id can never grant twice)
--   4. Server-side catalog check (amount and item come from YOUR config, not the payload)
--
-- server.cfg (never hardcode the secret in a resource file):
--   set payment_callback_secret "long-random-string"
--
-- SQL:
--   CREATE TABLE IF NOT EXISTS payment_events (
--       event_id   VARCHAR(64) PRIMARY KEY,
--       identifier VARCHAR(64) NOT NULL,
--       item       VARCHAR(64) NOT NULL,
--       amount     INT NOT NULL,
--       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--   );

local SECRET <const> = GetConvar('payment_callback_secret', '')
local MAX_AGE <const> = 300 -- seconds a signed request stays valid
local MAX_BODY <const> = 4096

-- The catalog is the source of truth. Never trust a price or item from the payload.
local CATALOG <const> = {
    starter_pack = { item = 'bread', count = 10, amount = 500 }, -- amount in minor units
}

-- Replace with your framework call (QBCore, ESX, ox_inventory, ...)
local function GrantItem(identifier, item, count)
    print(('[payments] grant %dx %s to %s'):format(count, item, identifier))
    return true
end

-- Pure Lua 5.4 SHA-256 and HMAC (CFX exposes no native HMAC)
local K <const> = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
}

local function rrot(x, n) return ((x >> n) | (x << (32 - n))) & 0xffffffff end

local function sha256(msg)
    local h = { 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19 }
    local len = #msg
    msg = msg .. '\128' .. ('\0'):rep((55 - len) % 64) .. string.pack('>I8', len * 8)
    for chunk = 1, #msg, 64 do
        local w = { string.unpack('>I4I4I4I4I4I4I4I4I4I4I4I4I4I4I4I4', msg, chunk) }
        for i = 17, 64 do
            local s0 = rrot(w[i - 15], 7) ~ rrot(w[i - 15], 18) ~ (w[i - 15] >> 3)
            local s1 = rrot(w[i - 2], 17) ~ rrot(w[i - 2], 19) ~ (w[i - 2] >> 10)
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xffffffff
        end
        local a, b, c, d, e, f, g, hh = table.unpack(h)
        for i = 1, 64 do
            local t1 = (hh + (rrot(e, 6) ~ rrot(e, 11) ~ rrot(e, 25)) + ((e & f) ~ (~e & g)) + K[i] + w[i]) & 0xffffffff
            local t2 = ((rrot(a, 2) ~ rrot(a, 13) ~ rrot(a, 22)) + ((a & b) ~ (a & c) ~ (b & c))) & 0xffffffff
            hh, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xffffffff, c, b, a, (t1 + t2) & 0xffffffff
        end
        local v = { a, b, c, d, e, f, g, hh }
        for i = 1, 8 do h[i] = (h[i] + v[i]) & 0xffffffff end
    end
    return string.pack('>I4I4I4I4I4I4I4I4', table.unpack(h))
end

local function hmacSha256Hex(key, msg)
    if #key > 64 then key = sha256(key) end
    key = key .. ('\0'):rep(64 - #key)
    local ipad = key:gsub('.', function(c) return string.char(c:byte() ~ 0x36) end)
    local opad = key:gsub('.', function(c) return string.char(c:byte() ~ 0x5c) end)
    return (sha256(opad .. sha256(ipad .. msg)):gsub('.', function(c) return ('%02x'):format(c:byte()) end))
end

-- Compare without exiting early so timing does not leak how much matched
local function safeEquals(a, b)
    if #a ~= #b then return false end
    local diff = 0
    for i = 1, #a do diff = diff | (a:byte(i) ~ b:byte(i)) end
    return diff == 0
end

local function reply(res, code, text)
    res.writeHead(code, { ['Content-Type'] = 'text/plain' })
    res.send(text)
end

local function handleCallback(req, res, body)
    local timestamp = tonumber(req.headers['x-timestamp'])
    local signature = req.headers['x-signature']
    if not timestamp or not signature then return reply(res, 400, 'bad request') end

    -- 1 + 2: signature and freshness
    if math.abs(os.time() - timestamp) > MAX_AGE then return reply(res, 401, 'stale') end
    if not safeEquals(hmacSha256Hex(SECRET, ('%d.%s'):format(timestamp, body)), signature:lower()) then
        print('[payments] rejected: bad signature')
        return reply(res, 401, 'unauthorized')
    end

    -- Only parse the payload after it is authenticated
    local ok, data = pcall(json.decode, body)
    if not ok or type(data) ~= 'table' then return reply(res, 400, 'bad payload') end
    local eventId, identifier, product, amount =
        data.event_id, data.identifier, data.product, tonumber(data.amount)
    if type(eventId) ~= 'string' or #eventId == 0 or #eventId > 64 then return reply(res, 400, 'bad event') end
    if type(identifier) ~= 'string' or #identifier > 64 then return reply(res, 400, 'bad identifier') end

    -- 4: the catalog decides what is granted and what it must cost
    local entry = type(product) == 'string' and CATALOG[product]
    if not entry or amount ~= entry.amount then return reply(res, 422, 'amount mismatch') end

    -- 3: first writer wins; a replay inserts 0 rows and is acknowledged without granting
    local inserted = MySQL.update.await(
        'INSERT IGNORE INTO payment_events (event_id, identifier, item, amount) VALUES (?, ?, ?, ?)',
        { eventId, identifier, entry.item, entry.amount }
    )
    if inserted == 0 then return reply(res, 200, 'duplicate') end

    if not GrantItem(identifier, entry.item, entry.count) then
        -- Release the id so the provider's retry can succeed
        MySQL.update.await('DELETE FROM payment_events WHERE event_id = ?', { eventId })
        return reply(res, 500, 'grant failed')
    end

    print(('[payments] granted %s to %s (event %s)'):format(entry.item, identifier, eventId))
    reply(res, 200, 'ok')
end

if SECRET == '' then
    print('[payments] payment_callback_secret is not set, callback endpoint disabled')
else
    -- Reachable at http://<server>:30120/<resource-name>/ (POST only)
    SetHttpHandler(function(req, res)
        if req.method ~= 'POST' then return reply(res, 405, 'method not allowed') end
        req.setDataHandler(function(body)
            if #body > MAX_BODY then return reply(res, 413, 'too large') end
            handleCallback(req, res, body)
        end)
    end)
end
