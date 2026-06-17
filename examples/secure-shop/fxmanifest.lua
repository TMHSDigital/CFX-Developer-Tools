fx_version 'cerulean'
games { 'gta5' }

name 'secure-shop'
author 'TMHSDigital'
description 'Server-authoritative shop demonstrating input validation and the never-trust-the-client model (ESX/QBCore bridge, standalone fallback)'
version '1.0.0'

lua54 true

shared_script 'config.lua'

client_script 'client/main.lua'
server_script 'server/main.lua'
