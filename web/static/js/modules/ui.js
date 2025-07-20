// Globale Referenzen auf DOM-Elemente
const routinesContainer = document.getElementById('routines-container');
const scenesContainer = document.getElementById('scenes-container');
const statusContainer = document.getElementById('status-container');
const logContainer = document.getElementById('log-container');
const toastElement = document.getElementById('toast');
const clockElement = document.getElementById('clock');
const sunTimesContainer = document.getElementById('sun-times');
const modalScene = document.getElementById('modal-scene');
const modalRoutine = document.getElementById('modal-routine');

const icons = {
    morning: '🌅', day: '☀️', evening: '🌇', night: '🌕'
};
const sectionColors = {
    morning: 'bg-yellow-100', day: 'bg-sky-100', evening: 'bg-orange-100', night: 'bg-indigo-100'
};

export function showToast(message, isError = false) {
    if (!toastElement) return;
    toastElement.textContent = message;
    toastElement.className = `fixed bottom-5 right-5 text-white py-2 px-4 rounded-lg shadow-xl transition-opacity duration-300 ${isError ? 'bg-red-600' : 'bg-gray-900'}`;
    toastElement.classList.remove('hidden');
    setTimeout(() => toastElement.classList.add('hidden'), 4000);
}

export function updateClock() {
    if (clockElement) {
        clockElement.textContent = new Date().toLocaleTimeString('de-DE');
    }
}

export function renderRoutines(routines) {
    routinesContainer.innerHTML = '';
    if (!routines || routines.length === 0) {
        routinesContainer.innerHTML = `<p class="text-gray-500 text-center">Noch keine Routinen erstellt.</p>`;
        return;
    }
    routines.forEach((routine, index) => {
        const routineEl = document.createElement('div');
        routineEl.className = 'bg-white p-6 rounded-lg shadow-md border-2 border-gray-200';
        const sections = ['morning', 'day', 'evening', 'night'];

        const sectionsHtml = sections.map(name => {
            const section = routine[name];
            if (!section) return '';
            const waitTime = section.wait_time || { min: 0, sec: 0 };
            const waitTimeString = `${waitTime.min || 0}m ${waitTime.sec || 0}s`;

            return `
            <div class="py-2 px-3 ${sectionColors[name] || 'bg-gray-50'} rounded-md">
                <p class="font-semibold capitalize flex items-center">${icons[name] || ''} <span class="ml-2">${name}</span></p>
                <div class="text-sm text-gray-700 grid grid-cols-2 gap-x-4">
                    <span><strong class="font-medium">Normal-Szene:</strong> ${section.scene_name}</span>
                    <span><strong class="font-medium">Bewegungs-Szene:</strong> ${section.x_scene_name}</span>
                    <span><strong class="font-medium">Bewegung:</strong> ${section.motion_check ? `Ja (${waitTimeString})` : 'Nein'}</span>
                    <span><strong class="font-medium">Nicht stören:</strong> ${section.do_not_disturb ? 'Ja' : 'Nein'}</span>
                    <span><strong class="font-medium">Helligkeits-Check:</strong> ${section.bri_check ? 'Ja' : 'Nein'}</span>
                    ${section.bri_check ? `<span><strong class="font-medium">Max. Helligkeit:</strong> ${section.max_light_level}</span>` : ''}
                </div>
            </div>
        `}).join('');

        const dailyTime = routine.daily_time || { H1: 0, M1: 0, H2: 23, M2: 59 };
        const isEnabled = routine.enabled !== false;

        routineEl.innerHTML = `
        <div class="flex justify-between items-start mb-4">
            <div>
                <h3 class="text-2xl font-semibold">${routine.name}</h3>
                <div class="flex items-center text-gray-500 text-sm">
                    <p>Raum: ${routine.room_name}</p>
                    <span class="mx-2">|</span>
                    <p>Aktiv: ${String(dailyTime.H1).padStart(2, '0')}:${String(dailyTime.M1).padStart(2, '0')} - ${String(dailyTime.H2).padStart(2, '0')}:${String(dailyTime.M2).padStart(2, '0')}</p>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <label class="relative inline-flex items-center cursor-pointer" title="Routine an/aus">
                    <input type="checkbox" data-action="toggle-routine" data-index="${index}" class="sr-only peer" ${isEnabled ? 'checked' : ''}>
                    <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-2 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                <button type="button" data-action="edit-routine" data-index="${index}" class="text-blue-500 hover:text-blue-700 font-semibold">Bearbeiten</button>
                <button type="button" data-action="delete-routine" data-index="${index}" class="text-red-500 hover:text-red-700 font-semibold">Löschen</button>
            </div>
        </div>
        <div class="space-y-2">
            <h4 class="text-lg font-medium border-t pt-4 mt-4">Ablauf</h4>
            ${sectionsHtml}
        </div>
    `;
        routinesContainer.appendChild(routineEl);
    });
}

export function renderScenes(scenes) {
    scenesContainer.innerHTML = '';
    if (!scenes || Object.keys(scenes).length === 0) {
        scenesContainer.innerHTML = `<p class="text-gray-500 text-center">Noch keine Szenen erstellt.</p>`;
        return;
    }
    for (const [name, scene] of Object.entries(scenes)) {
        const sceneEl = document.createElement('div');
        sceneEl.className = 'bg-white p-4 rounded-lg shadow-md flex flex-col justify-between border-2 border-gray-200';

        let colorPreviewStyle = 'background-color: #f3f4f6;';
        if (scene.hue !== undefined && scene.sat !== undefined) {
            const hue = scene.hue / 65535 * 360;
            const sat = scene.sat / 254 * 100;
            colorPreviewStyle = `background-color: hsl(${hue}, ${sat}%, 50%);`;
        } else if (scene.ct !== undefined) {
            const tempPercent = (scene.ct - 153) / (500 - 153);
            const red = 255 * tempPercent;
            const blue = 255 * (1 - tempPercent);
            colorPreviewStyle = `background-color: rgb(${Math.round(red)}, ${Math.round(red * 0.8 + blue * 0.2)}, ${Math.round(blue)});`;
        }

        sceneEl.innerHTML = `
        <div>
            <div class="flex items-center mb-2">
                <div class="w-6 h-6 rounded-full mr-3 border border-gray-300" style="${colorPreviewStyle}"></div>
                <h4 class="text-xl font-semibold capitalize">${name.replace(/_/g, ' ')}</h4>
            </div>
            <div class="mt-2 text-sm text-gray-600 space-y-1">
                <p>Status: <span class="font-medium ${scene.status ? 'text-green-600' : 'text-red-600'}">${scene.status ? 'An' : 'Aus'}</span></p>
                <p>Helligkeit: <span class="font-medium">${scene.bri}</span></p>
                ${scene.hue !== undefined ? `<p>Farbton: <span class="font-medium">${scene.hue}</span></p>` : ''}
                ${scene.sat !== undefined ? `<p>Sättigung: <span class="font-medium">${scene.sat}</span></p>` : ''}
                ${scene.ct !== undefined ? `<p>Farbtemp.: <span class="font-medium">${scene.ct}</span></p>` : ''}
            </div>
        </div>
        <div class="mt-4 flex justify-end space-x-2">
            <button type="button" data-action="edit-scene" data-name="${name}" class="text-blue-500 hover:text-blue-700 text-sm font-semibold">Bearbeiten</button>
            <button type="button" data-action="delete-scene" data-name="${name}" class="text-red-500 hover:text-red-700 text-sm font-semibold">Löschen</button>
        </div>
    `;
        scenesContainer.appendChild(sceneEl);
    }
}

export function renderSunTimes(sunTimes) {
    if (sunTimes && sunTimes.sunrise) {
        const sunrise = new Date(sunTimes.sunrise).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
        const sunset = new Date(sunTimes.sunset).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
        sunTimesContainer.innerHTML = `
            <div>
                <span>Sonnenaufgang:</span>
                <span class="font-semibold">${sunrise}</span>
            </div>
            <div>
                <span>Sonnenuntergang:</span>
                <span class="font-semibold">${sunset}</span>
            </div>
        `;
    } else {
        sunTimesContainer.innerHTML = `
            <div>
                <span>Sonnenaufgang:</span>
                <span class="font-semibold">--:--</span>
            </div>
            <div>
                <span>Sonnenuntergang:</span>
                <span class="font-semibold">--:--</span>
            </div>
        `;
    }
}

export function renderStatus(statuses, config) {
    statusContainer.innerHTML = '';
    if (!statuses || statuses.length === 0) {
        statusContainer.innerHTML = `<p class="text-gray-500">Warte auf Status-Daten...</p>`;
        return;
    }
    statuses.forEach(status => {
        const motionColor = status.motion_status.includes('erkannt') ? 'text-green-500' : 'text-gray-500';
        const enabledColor = status.enabled ? 'text-green-500' : 'text-red-500';

        let currentSceneInfo = 'N/A';
        const routineConfig = config.routines.find(r => r.name === status.name);
        if (routineConfig && status.period && routineConfig[status.period]) {
            const periodConfig = routineConfig[status.period];
            currentSceneInfo = `Normal: <strong>${periodConfig.scene_name}</strong> / Bewegung: <strong>${periodConfig.x_scene_name}</strong>`;
        }

        const statusEl = document.createElement('div');
        statusEl.className = 'bg-white p-4 rounded-lg shadow border-2 border-gray-200';
        statusEl.innerHTML = `
        <h4 class="font-bold text-lg">${status.name}</h4>
        <div class="text-sm grid grid-cols-1 md:grid-cols-3 gap-2 mt-2">
            <span><strong>Routine-Status:</strong> <span class="${enabledColor}">${status.enabled ? 'Aktiviert' : 'Deaktiviert'}</span></span>
            <span><strong>Aktueller Zeitraum:</strong> <span class="flex items-center">${icons[status.period] || ''} <span class="ml-1">${status.period || 'Inaktiv'}</span></span></span>
            <span><strong>Letzte geschaltete Szene:</strong> ${status.last_scene || 'N/A'}</span>
            <span class="md:col-span-3"><strong>Konfigurierte Szene (für '${status.period}'):</strong> ${currentSceneInfo}</span>
            <span class="${motionColor}"><strong>Bewegung:</strong> ${status.motion_status || 'N/A'}</span>
            <span><strong>Helligkeit (Sensor):</strong> ${status.brightness !== 'N/A' ? status.brightness : 'Kein Sensor'}</span>
        </div>
    `;
        statusContainer.appendChild(statusEl);
    });
}

export function renderLog(logText) {
    logContainer.innerHTML = '';
    const lines = logText.split('\n');
    lines.forEach(line => {
        const span = document.createElement('span');
        if (line.includes('ERROR')) {
            span.className = 'text-red-400 block';
        } else if (line.includes('WARNING')) {
            span.className = 'text-yellow-400 block';
        } else if (line.includes('DEBUG')) {
            span.className = 'text-blue-400 block';
        } else {
            span.className = 'text-gray-300 block';
        }
        span.textContent = line || '\u00A0'; // Use non-breaking space for empty lines
        logContainer.appendChild(span);
    });
    logContainer.scrollTop = logContainer.scrollHeight;
}
