fx_version 'cerulean'
games { 'gta5' }

author 'YourName'
description 'ox_core resource'
version '1.0.0'

dependency 'ox_core'

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
