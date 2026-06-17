// NUI message routing. The client sends two action types:
//   { action: 'display', show: true|false }  -> toggle visibility
//   { action: 'speed', value: <int>, unit }  -> update the readout
const speedo = document.getElementById('speedo');
const valueEl = document.getElementById('value');
const unitEl = document.getElementById('unit');

const UNIT_LABELS = {
    mph: 'mph',
    kmh: 'km/h',
};

window.addEventListener('message', function (event) {
    const data = event.data;
    if (!data || !data.action) {
        return;
    }

    if (data.action === 'display') {
        speedo.classList.toggle('hidden', !data.show);
    } else if (data.action === 'speed') {
        valueEl.textContent = data.value;
        unitEl.textContent = UNIT_LABELS[data.unit] || data.unit;
    }
});
