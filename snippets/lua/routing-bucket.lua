-- Routing bucket (instance) management
-- Players in different buckets cannot see or interact with each other

-- Move player to an instanced bucket (server only)
local instanceBucket = source + 1000
SetPlayerRoutingBucket(source, instanceBucket)
SetRoutingBucketPopulationEnabled(instanceBucket, false)

-- Get player's current bucket
local bucket = GetPlayerRoutingBucket(source)

-- Return player to the default world
SetPlayerRoutingBucket(source, 0)

-- Move an entity to a specific bucket
SetEntityRoutingBucket(entity, instanceBucket)

-- Lock bucket so new entities stay inside it
SetRoutingBucketEntityLockdownMode(instanceBucket, 'strict')
