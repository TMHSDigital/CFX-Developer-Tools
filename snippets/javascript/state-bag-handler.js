// CFX State Bag Change Handler (JavaScript)
// React to state changes on any entity or player bag.

AddStateBagChangeHandler('myResource:fuel', null, (bagName, key, value, _reserved, replicated) => {
    const entity = GetEntityFromStateBagName(bagName);
    if (entity === 0) return;

    if (replicated) {
        // change came from network; validate if needed
    }

    // react to the new value
});
