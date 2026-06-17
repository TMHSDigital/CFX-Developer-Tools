fx_version 'cerulean'
games { 'gta5' }

name 'speedometer-hud'
author 'TMHSDigital'
description 'A passive speedometer HUD demonstrating rate-limited SendNUIMessage and vanilla NUI (no build tooling).'
version '1.0.0'

lua54 true

shared_script 'config.lua'

client_script 'client/main.lua'

ui_page 'html/index.html'

files {
    'html/index.html',
    'html/style.css',
    'html/app.js',
}
