fx_version 'cerulean'
games { 'gta5' } -- Qbox is FiveM-only

author 'YourName'
description 'Qbox resource'
version '1.0.0'

dependency 'qbx_core'

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
