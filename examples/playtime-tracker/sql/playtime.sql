-- playtime-tracker migration.
-- Import once before starting the resource:
--   - via oxmysql/your DB tool, run this file against your game database, or
--   - paste it into a MySQL client connected to the same database that
--     `mysql_connection_string` points at.
--
-- `identifier` is the stable per-player key (ESX identifier, QBCore citizenid,
-- or the player's Rockstar license on standalone). `seconds` is the running
-- lifetime total. `last_seen` is updated on every flush so you can spot
-- inactive players.

CREATE TABLE IF NOT EXISTS `player_playtime` (
    `identifier` VARCHAR(64) NOT NULL PRIMARY KEY,
    `seconds`    INT NOT NULL DEFAULT 0,
    `last_seen`  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
