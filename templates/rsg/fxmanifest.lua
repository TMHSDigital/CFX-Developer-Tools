fx_version 'cerulean'
games { 'rdr3' }

author 'YourName'
description 'RSG resource'
version '1.0.0'

dependency 'rsg-core'

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
