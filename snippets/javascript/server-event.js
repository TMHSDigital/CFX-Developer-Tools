// CFX Server Event Pattern (JavaScript)
// Listen for a network event from a client. Always validate source.

onNet('myResource:serverEvent', (data) => {
    const src = global.source;

    // Validate the source is a real player
    if (!src || src <= 0) return;

    // Validate data
    if (typeof data !== 'object') return;

    // Your server logic here
    console.log(`Player ${src} triggered event`);
});
