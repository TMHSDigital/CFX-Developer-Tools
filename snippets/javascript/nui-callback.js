// CFX NUI Callback Pattern (JavaScript - Client Script Side)
// Register a NUI callback in a JS client script and send messages to the NUI browser.
// This is the CFX-client-side counterpart to the browser's window.addEventListener('message').

// Send a message from client script to NUI browser
// The NUI browser receives this via window.addEventListener('message', ...)
function openMenu(data) {
    SendNUIMessage({ type: 'open', payload: data });
    SetNuiFocus(true, true);
}

// Register a callback that the NUI browser can invoke via fetch POST
// Browser calls: fetch(`https://${GetParentResourceName()}/closeMenu`, { method: 'POST', body: JSON.stringify({}) })
RegisterNuiCallbackType('closeMenu');
on('__cfx_nui:closeMenu', (data, cb) => {
    SetNuiFocus(false, false);
    cb({ ok: true });
});

// Clean up on resource stop
on('onResourceStop', (resourceName) => {
    if (GetCurrentResourceName() !== resourceName) return;
    SetNuiFocus(false, false);
});
