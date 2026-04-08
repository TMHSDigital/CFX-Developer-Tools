---
title: Database Integration
description: Guide database setup and queries for FiveM resources using oxmysql
globs: ["**/*.lua", "**/*.js", "**/*.sql"]
---

# Database Integration

Most FiveM RP servers use MySQL for persistent data. The standard library is **oxmysql**, which provides async MySQL queries from Lua and JavaScript resources.

## Setup

### 1. Install oxmysql

Download from https://github.com/overextended/oxmysql/releases and place in your server's `resources/` folder.

### 2. Configure the connection string

In `server.cfg`:
```
set mysql_connection_string "mysql://user:password@localhost/database_name?charset=utf8mb4"
ensure oxmysql
```

### 3. Add to fxmanifest.lua

```lua
server_scripts {
    '@oxmysql/lib/MySQL.lua',
    'server/*.lua'
}
```

The `@oxmysql/lib/MySQL.lua` import makes the `MySQL` global available in your server scripts.

## Query patterns (Lua)

### Select (fetch rows)

```lua
-- Async with callback
MySQL.query('SELECT * FROM players WHERE identifier = ?', {identifier}, function(result)
    -- result is an array of rows
end)

-- Async with promise (in a thread)
local result = MySQL.query.await('SELECT * FROM players WHERE identifier = ?', {identifier})
```

### Single row

```lua
local row = MySQL.single.await('SELECT * FROM players WHERE identifier = ? LIMIT 1', {identifier})
if row then
    print(row.name)
end
```

### Single value (scalar)

```lua
local money = MySQL.scalar.await('SELECT money FROM players WHERE identifier = ?', {identifier})
```

### Insert

```lua
local insertId = MySQL.insert.await('INSERT INTO players (identifier, name) VALUES (?, ?)', {
    identifier, playerName
})
```

### Update

```lua
local affectedRows = MySQL.update.await('UPDATE players SET money = ? WHERE identifier = ?', {
    newAmount, identifier
})
```

### Execute (general purpose)

```lua
MySQL.execute('DELETE FROM vehicles WHERE owner = ?', {identifier})
```

## Parameterized queries

**Always use parameterized queries.** Never concatenate user input into SQL strings.

```lua
-- Good: parameterized
MySQL.query.await('SELECT * FROM players WHERE name = ?', {playerName})

-- DANGEROUS: SQL injection vulnerability
MySQL.query.await('SELECT * FROM players WHERE name = "' .. playerName .. '"')
```

## mysql-async (legacy)

Older resources may use mysql-async instead of oxmysql. The API is similar but uses different function names:

```lua
-- mysql-async equivalents
MySQL.Async.fetchAll('SELECT * FROM players WHERE identifier = @id', {['@id'] = identifier}, function(result)
end)

MySQL.Async.execute('UPDATE players SET money = @money WHERE identifier = @id', {
    ['@money'] = newAmount,
    ['@id'] = identifier
})
```

oxmysql is backwards-compatible with mysql-async syntax, so migrating usually requires only changing the resource dependency.

## Common schema patterns

### Players table

```sql
CREATE TABLE IF NOT EXISTS `players` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `identifier` VARCHAR(60) NOT NULL UNIQUE,
    `name` VARCHAR(50) NOT NULL DEFAULT 'Unknown',
    `money` INT NOT NULL DEFAULT 0,
    `bank` INT NOT NULL DEFAULT 0,
    `job` VARCHAR(50) NOT NULL DEFAULT 'unemployed',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Vehicles table

```sql
CREATE TABLE IF NOT EXISTS `player_vehicles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `owner` VARCHAR(60) NOT NULL,
    `plate` VARCHAR(8) NOT NULL,
    `model` VARCHAR(50) NOT NULL,
    `stored` TINYINT(1) NOT NULL DEFAULT 1,
    `garage` VARCHAR(50) DEFAULT 'default',
    INDEX `idx_owner` (`owner`)
);
```

### Inventory table

```sql
CREATE TABLE IF NOT EXISTS `player_inventory` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `owner` VARCHAR(60) NOT NULL,
    `item` VARCHAR(50) NOT NULL,
    `count` INT NOT NULL DEFAULT 1,
    `metadata` JSON DEFAULT NULL,
    INDEX `idx_owner` (`owner`)
);
```

## Migration patterns

For schema changes, create numbered SQL migration files:

```
migrations/
  001_create_players.sql
  002_add_bank_column.sql
  003_create_vehicles.sql
```

Run them manually or build a simple migration runner that tracks which migrations have been applied.

## Tips

- Use indexes on columns you query frequently (identifiers, owner fields)
- Use transactions for operations that must be atomic (transferring money between players)
- Avoid `SELECT *` in production -- select only the columns you need
- Use `LIMIT` when you only need one row
- oxmysql handles connection pooling automatically -- you do not need to manage connections manually
- Test queries with sample data before deploying to a live server
