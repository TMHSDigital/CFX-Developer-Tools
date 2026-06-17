fx_version 'cerulean'
games { 'gta5' }

name 'playtime-tracker'
author 'TMHSDigital'
description 'Tracks per-player playtime in MySQL via oxmysql (prepared statements, migration, identifier lookup; ESX/QBCore bridge, standalone fallback)'
version '1.0.0'

lua54 true

-- oxmysql provides the database exports used in server/main.lua. It reads the
-- connection string from the server convar `mysql_connection_string`, so no
-- credentials live in this resource.
dependency 'oxmysql'

shared_script 'config.lua'

server_script 'server/main.lua'
