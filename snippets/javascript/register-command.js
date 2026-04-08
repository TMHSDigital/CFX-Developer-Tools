// CFX Register Command Pattern (JavaScript)
// Creates a chat command. Set the third argument to true for admin-only.

RegisterCommand('mycommand', (source, args, rawCommand) => {
    // source: player server ID (0 on server console)
    // args: array of space-separated arguments
    // rawCommand: the full string typed

    if (source > 0) {
        emitNet('myResource:doSomething', source, args[0]);
    } else {
        console.log('Command executed from console');
    }
}, false); // false = not restricted
