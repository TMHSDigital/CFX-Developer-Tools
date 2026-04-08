fx_version 'cerulean'
games { 'gta5', 'rdr3' } -- Remove 'rdr3' for FiveM-only, or 'gta5' for RedM-only

author 'YourName'
description 'Standalone resource'
version '1.0.0'

shared_scripts {
    'config.lua'
}

client_scripts {
    'client/*.lua'
}

server_scripts {
    'server/*.lua'
}
