fx_version 'cerulean'
games { 'gta5' } -- ox_core is FiveM-only; add 'rdr3' if porting to RedM

author 'YourName'
description 'ox_core resource'
version '1.0.0'

-- `require '@ox_core.lib.init'` in the scripts is provided by ox_lib, so
-- ox_lib must be loaded first.
dependencies {
    'ox_lib',
    'ox_core'
}

shared_scripts {
    '@ox_lib/init.lua',
    'config.lua'
}

client_scripts {
    'client/*.lua'
}

server_scripts {
    '@oxmysql/lib/MySQL.lua',
    'server/*.lua'
}
