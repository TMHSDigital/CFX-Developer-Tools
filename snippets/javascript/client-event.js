// CFX Client Event Pattern (JavaScript)
// Listen for a network event triggered by the server.

onNet('myResource:clientEvent', (data) => {
    // data: whatever the server sent
    console.log('Received data:', data);

    // Your client-side logic here
});
