fx_version 'cerulean'
games { 'gta5', 'rdr3' } -- Remove 'rdr3' for FiveM-only, or 'gta5' for RedM-only

author 'YourName'
description 'C# resource'
version '1.0.0'

-- Build with `dotnet build Client` and `dotnet build Server`; each project
-- writes its .net.dll into dist/.
client_scripts {
    'dist/MyResource.Client.net.dll'
}

server_scripts {
    'dist/MyResource.Server.net.dll'
}
