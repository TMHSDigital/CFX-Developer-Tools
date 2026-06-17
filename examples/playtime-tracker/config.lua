Config = {}

-- 'auto' resolves ESX or QBCore at runtime. Force with 'esx' / 'qb' / 'standalone'.
-- The framework is only used to resolve a stable per-player identifier; all
-- database access is server-side and framework-agnostic.
Config.Framework = 'auto'

-- How often (in minutes) accumulated session time is flushed to the database.
-- A periodic flush means a server crash loses at most this many minutes of
-- playtime instead of the whole session, which only saves on player drop.
Config.SaveIntervalMinutes = 5
