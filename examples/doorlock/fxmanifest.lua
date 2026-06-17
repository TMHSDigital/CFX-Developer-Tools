fx_version 'cerulean'
games { 'gta5' }

name 'doorlock'
author 'TMHSDigital'
description 'Server-authoritative door locking via replicated StateBags (ESX/QBCore notify bridge, standalone fallback)'
version '1.0.0'

lua54 true

shared_script 'config.lua'

client_script 'client/main.lua'
server_script 'server/main.lua'
