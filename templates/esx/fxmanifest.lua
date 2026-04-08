fx_version 'cerulean'
games { 'gta5' }

author 'YourName'
description 'ESX resource'
version '1.0.0'

dependency 'es_extended'

shared_scripts {
    'config.lua'
}

client_scripts {
    'client/*.lua'
}

server_scripts {
    '@oxmysql/lib/MySQL.lua',
    'server/*.lua'
}
