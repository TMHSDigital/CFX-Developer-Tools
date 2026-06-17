fx_version 'cerulean'
games { 'gta5' }

name 'drug-sell'
author 'TMHSDigital'
description 'Sell custom drugs to nearby pedestrians (ESX/QBCore bridge, standalone fallback)'
version '1.0.0'

lua54 true

shared_script 'config.lua'

client_script 'client/main.lua'
server_script 'server/main.lua'
