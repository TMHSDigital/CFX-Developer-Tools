fx_version 'cerulean'
games { 'gta5', 'rdr3' } -- Remove 'rdr3' for FiveM-only, or 'gta5' for RedM-only

author 'YourName'
description 'NUI resource with Vite + Svelte 5'
version '1.0.0'

client_scripts {
    'client/*.lua'
}

ui_page 'web/dist/index.html'

files {
    'web/dist/**'
}
