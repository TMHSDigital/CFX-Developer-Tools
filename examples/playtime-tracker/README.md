# playtime-tracker

A minimal, server-authoritative FiveM example that tracks how long each player
has spent on the server and persists it in MySQL through
[oxmysql](https://github.com/overextended/oxmysql).

It is the worked example for the repo's `database-integration` skill.

## What it demonstrates

- **oxmysql prepared / parameterised statements.** Every query passes its values
  as the array argument (`{ identifier, total }`) with `?` placeholders. Values
  are never concatenated into the SQL string, which prevents injection and lets
  the database reuse the query plan.
- **A migration.** `sql/playtime.sql` creates the `player_playtime` table with
  `CREATE TABLE IF NOT EXISTS`, so re-importing is safe.
- **Stable identifier lookup.** A small framework bridge resolves a durable
  per-player key: the ESX `identifier`, the QBCore `citizenid`, or the Rockstar
  `license` on standalone. That identifier is the table's primary key.
- **UPSERT accumulation.** Time is flushed periodically and on disconnect with
  `INSERT ... ON DUPLICATE KEY UPDATE`, so a returning player's total keeps
  growing rather than resetting.

## Files

| File | Purpose |
|------|---------|
| `fxmanifest.lua` | Resource manifest; declares the `oxmysql` dependency. |
| `config.lua` | `Config.Framework` and `Config.SaveIntervalMinutes`. |
| `sql/playtime.sql` | Migration that creates `player_playtime`. |
| `server/main.lua` | Identifier resolution, session tracking, queries, `/playtime`. |

## Install

1. **Import the schema.** Run `sql/playtime.sql` against your game database
   (your DB tool of choice, or paste it into a MySQL client connected to the
   same database oxmysql uses).
2. **Set the connection convar.** oxmysql reads the connection string from the
   server convar `mysql_connection_string`. Add it to your `server.cfg`, for
   example:

   ```cfg
   set mysql_connection_string "mysql://user:password@127.0.0.1:3306/fivem?charset=utf8mb4"
   ```

   The string lives in server config, not in this resource - there are no
   hardcoded credentials in the Lua.
3. **Ensure the dependency and this resource** (oxmysql must start first):

   ```cfg
   ensure oxmysql
   ensure playtime-tracker
   ```

## Usage

Players run `/playtime` in chat to see their lifetime total formatted as
`Hh Mm`. The value is computed and reported server-side, so it cannot be
spoofed by a modded client.

## The prepared-statement pattern

oxmysql exposes parameterised exports. The rule is: put `?` where each value
goes, and pass the values as the array argument.

```lua
-- Read a single value (scalar) with a parameter.
exports.oxmysql:scalar_async(
    'SELECT seconds FROM player_playtime WHERE identifier = ?',
    { identifier },
    function(existing) --[[ ... ]] end
)

-- Insert-or-update with parameters. Values are NEVER concatenated into the SQL.
exports.oxmysql:execute(
    'INSERT INTO player_playtime (identifier, seconds) VALUES (?, ?) '
    .. 'ON DUPLICATE KEY UPDATE seconds = VALUES(seconds), last_seen = CURRENT_TIMESTAMP',
    { identifier, total }
)
```

Building SQL by joining user-controlled strings is the one thing to avoid; the
array argument keeps the query safe and cacheable.
