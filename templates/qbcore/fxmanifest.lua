fx_version 'cerulean'
games { 'gta5' } -- QBCore is FiveM-only; add 'rdr3' if porting to RedM

author 'YourName'
description 'QBCore resource'
version '1.0.0'

dependency 'qb-core'

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
