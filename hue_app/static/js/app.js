document.addEventListener('DOMContentLoaded', () => {
    // Globale Zustandsvariablen
    let config = {};
    let bridgeData = { groups: [], sensors: [] };
    let statusInterval;
    let colorPicker;

    // --- UI Konstanten ---
    const ICONS = { morning: '🌅', day: '☀️', evening: '🌄', night: '🌕' };
    const SECTION_COLORS = { morning: 'bg-yellow-100 dark:bg-yellow-900/50', day: 'bg-sky-100 dark:bg-sky-900/50', evening: 'bg-orange-100 dark:bg-orange-900/50', night: 'bg-indigo-100 dark:bg-indigo-900/50' };

    // --- Element-Referenzen ---
    const getEl = id => document.getElementById(id);
    const queryEl = selector => document.querySelector(selector);
    const queryAll = selector => document.querySelectorAll(selector);
    
    const elements = {
        clock: getEl('clock'),
        darkModeToggle: getEl('dark-mode-toggle'),
        settingsButton: getEl('settings-button'),
        saveAllButton: getEl('save-all-button'),
        toast: getEl('toast'),
        modalContainer: getEl('modal-container'),
    };

    // --- Initialisierung ---
    const init = async () => {
        setupEventListeners();
        updateClock();
        setInterval(updateClock, 1000);
        applyTheme(localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches));
        
        showToast('Lade Konfiguration...', false, true);
        try {
            const [configRes, groupsRes, sensorsRes] = await Promise.all([
                fetch('/api/config'),
                fetch('/api/bridge/groups'),
                fetch('/api/bridge/sensors')
            ]);
            if (!configRes.ok || !groupsRes.ok || !sensorsRes.ok) throw new Error("Netzwerkantwort war nicht ok.");
            
            config = await configRes.json();
            bridgeData = { groups: await groupsRes.json(), sensors: await sensorsRes.json() };
            
            const initialTab = queryEl('.tab-button');
            if(initialTab) switchTab(initialTab.dataset.tab);
        } catch (error) {
            console.error("Initialisierungsfehler:", error);
            showToast("Fehler beim Laden der Daten.", true);
        } finally {
            showToast('', false);
        }
    };

    // --- Event-Listener ---
    const setupEventListeners = () => {
        elements.darkModeToggle.addEventListener('click', toggleTheme);
        elements.settingsButton.addEventListener('click', openSettingsModal);
        elements.saveAllButton.addEventListener('click', saveAndRestart);
        queryAll('.tab-button').forEach(button => button.addEventListener('click', () => switchTab(button.dataset.tab)));
        document.body.addEventListener('click', handleDynamicClicks);
    };

    // --- UI Rendering & Hilfsfunktionen ---
    const render = tab => {
        const container = getEl(`tab-content-${tab}`);
        if (!container) return;
        const renderMap = { routines: getRoutinesHTML, scenes: getScenesHTML, status: getStatusHTML };
        container.innerHTML = renderMap[tab]();
        if (tab === 'status') {
            updateStatus();
            if (statusInterval) clearInterval(statusInterval);
            statusInterval = setInterval(updateStatus, 5000);
        }
    };
    
    const showToast = (message, isError = false, persistent = false) => {
        if (!message) return elements.toast.classList.add('hidden');
        elements.toast.textContent = message;
        elements.toast.className = `fixed bottom-5 right-5 text-white py-2 px-4 rounded-lg shadow-xl transition-opacity duration-300 ${isError ? 'bg-red-600' : 'bg-gray-900'}`;
        elements.toast.classList.remove('hidden');
        if (!persistent) setTimeout(() => elements.toast.classList.add('hidden'), 3000);
    };

    const updateClock = () => { if(elements.clock) elements.clock.textContent = new Date().toLocaleTimeString('de-DE'); };
    
    const applyTheme = isDark => {
        document.documentElement.classList.toggle('dark', isDark);
        elements.darkModeToggle.querySelector('.material-icons').textContent = isDark ? 'light_mode' : 'dark_mode';
    };

    const toggleTheme = () => {
        const isDark = !document.documentElement.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        applyTheme(isDark);
    };

    // --- HTML-Generatoren ---
    const getRoutinesHTML = () => {
        const routines = config.routines || [];
        const routinesHtml = routines.map((routine, index) => {
            const isEnabled = routine.enabled !== false;
            const dailyTime = routine.daily_time || { H1: 0, M1: 0, H2: 23, M2: 59 };
            const timeString = `${String(dailyTime.H1).padStart(2, '0')}:${String(dailyTime.M1).padStart(2, '0')} - ${String(dailyTime.H2).padStart(2, '0')}:${String(dailyTime.M2).padStart(2, '0')}`;
            
            const sectionsHtml = Object.entries(ICONS).map(([name, icon]) => {
                const section = routine[name];
                if (!section) return '';
                const waitTime = section.wait_time || { min: 0, sec: 0 };
                const waitTimeString = `${waitTime.min || 0}m ${waitTime.sec || 0}s`;
                return `
                    <div class="p-3 rounded-md ${SECTION_COLORS[name]}">
                        <p class="font-semibold capitalize flex items-center">${icon} <span class="ml-2">${name}</span></p>
                        <div class="text-sm text-gray-700 dark:text-gray-300 grid grid-cols-2 gap-x-4">
                            <span><strong class="font-medium">Normal:</strong> ${section.scene_name}</span>
                            <span><strong class="font-medium">Bewegung:</strong> ${section.x_scene_name}</span>
                            <span><strong class="font-medium">Bewegung:</strong> ${section.motion_check ? `Ja (${waitTimeString})` : 'Nein'}</span>
                            <span><strong class="font-medium">Nicht stören:</strong> ${section.do_not_disturb ? 'Ja' : 'Nein'}</span>
                            <span><strong class="font-medium">Helligkeit:</strong> ${section.bri_check ? 'Ja' : 'Nein'}</span>
                        </div>
                    </div>`;
            }).join('');

            return `
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border dark:border-gray-700">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-2xl font-semibold">${routine.name}</h3>
                        <div class="flex items-center text-gray-500 dark:text-gray-400 text-sm">
                            <p>Raum: ${routine.room_name}</p><span class="mx-2">|</span><p>Aktiv: ${timeString}</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <label class="relative inline-flex items-center cursor-pointer" title="Routine an/aus">
                            <input type="checkbox" data-action="toggle-routine" data-index="${index}" class="sr-only peer" ${isEnabled ? 'checked' : ''}>
                            <div class="w-11 h-6 bg-gray-200 dark:bg-gray-600 rounded-full peer peer-focus:ring-2 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                        <button data-action="edit-routine" data-index="${index}" class="text-blue-500 hover:text-blue-700 font-semibold">Bearbeiten</button>
                        <button data-action="delete-routine" data-index="${index}" class="text-red-500 hover:text-red-700 font-semibold">Löschen</button>
                    </div>
                </div>
                <div class="space-y-2 border-t dark:border-gray-700 pt-4 mt-4">
                    <h4 class="text-lg font-medium">Ablauf</h4>
                    ${sectionsHtml}
                </div>
            </div>`;
        }).join('');

        return `<div class="flex justify-end mb-4"><button data-action="add-routine" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg flex items-center"><span class="material-icons mr-2">add</span>Neue Routine</button></div><div class="space-y-6">${routines.length > 0 ? routinesHtml : '<p class="text-center text-gray-500">Keine Routinen erstellt.</p>'}</div>`;
    };
    
    const getScenesHTML = () => {
        const scenes = config.scenes || {};
        const sceneKeys = Object.keys(scenes);
        const scenesHtml = sceneKeys.map(key => `
            <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md border dark:border-gray-700">
                <div class="flex justify-between items-center">
                    <div><h3 class="text-xl font-bold">${scenes[key].name || key}</h3></div>
                    <div class="flex items-center space-x-2">
                        <button data-action="edit-scene" data-key="${key}" class="text-blue-500 hover:text-blue-700 font-semibold">Bearbeiten</button>
                        <button data-action="delete-scene" data-key="${key}" class="text-red-500 hover:text-red-700 font-semibold">Löschen</button>
                    </div>
                </div>
            </div>`).join('');
        return `<div class="flex justify-end mb-4"><button data-action="add-scene" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg flex items-center"><span class="material-icons mr-2">add</span>Neue Szene</button></div><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">${sceneKeys.length > 0 ? scenesHtml : '<p class="text-center text-gray-500 col-span-full">Keine Szenen erstellt.</p>'}</div>`;
    };

    const getStatusHTML = () => `
        <div class="space-y-8">
            <div><h2 class="text-2xl font-semibold mb-4">Live-Zustand der Routinen</h2><div id="status-container" class="space-y-4"></div></div>
            <div><h2 class="text-2xl font-semibold mb-4">Log-Datei</h2><pre id="log-container" class="bg-gray-900 text-gray-300 font-mono text-sm p-4 rounded-lg h-96 overflow-y-auto"></pre></div>
        </div>`;

    const getModalHTML = (title, formContent, submitText) => `
        <div class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
                <h3 class="text-xl font-bold p-6 border-b dark:border-gray-700 flex-shrink-0">${title}</h3>
                <form id="modal-form" class="flex-grow overflow-y-auto p-6 space-y-4">${formContent}</form>
                <div class="flex justify-end space-x-3 p-4 bg-gray-50 dark:bg-gray-900/50 border-t dark:border-gray-700 flex-shrink-0">
                    <button type="button" data-action="close-modal" class="bg-gray-200 dark:bg-gray-600 px-4 py-2 rounded-md font-medium">Abbrechen</button>
                    <button type="submit" form="modal-form" class="bg-blue-600 text-white px-4 py-2 rounded-md font-medium">${submitText}</button>
                </div>
            </div>
        </div>`;

    // --- API & Daten ---
    const updateStatus = async () => {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            const statusContainer = getEl('status-container');
            const logContainer = getEl('log-container');
            if (statusContainer) {
                const statuses = data.status || [];
                statusContainer.innerHTML = statuses.length > 0 ? statuses.map(s => `<div class="bg-white dark:bg-gray-700 p-3 rounded-md shadow-sm text-sm"><span class="font-bold">${s.name}:</span> ${s.period || 'N/A'}</div>`).join('') : '<p class="text-gray-500">Keine Statusdaten.</p>';
            }
            if (logContainer) {
                logContainer.textContent = data.log || 'Log ist leer.';
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        } catch (error) { console.error("Status-Update fehlgeschlagen:", error); }
    };

    const saveAndRestart = async () => {
        showToast('Speichere Konfiguration...', false, true);
        elements.saveAllButton.disabled = true;
        try {
            const configRes = await fetch('/api/config', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(config) });
            if (!configRes.ok) throw new Error('Konfiguration konnte nicht gespeichert werden.');
            
            showToast('Starte Logik neu...', false, true);
            const restartRes = await fetch('/api/restart', { method: 'POST' });
            if (!restartRes.ok) throw new Error('Neustart fehlgeschlagen.');
            
            showToast('Erfolgreich gespeichert und neu gestartet!');
        } catch (error) {
            showToast(error.message, true);
        } finally {
            elements.saveAllButton.disabled = false;
        }
    };

    // --- Aktionen & Modals ---
    const handleDynamicClicks = e => {
        const target = e.target.closest('[data-action]');
        if (!target) return;
        
        const { action, index, key } = target.dataset;
        if (action !== 'toggle-routine') e.preventDefault();

        const actions = {
            'add-routine': () => openRoutineModal(),
            'edit-routine': () => openRoutineModal(index),
            'delete-routine': () => deleteItem('routines', index),
            'toggle-routine': () => toggleRoutine(index),
            'add-scene': () => openSceneModal(),
            'edit-scene': () => openSceneModal(key),
            'delete-scene': () => deleteItem('scenes', key),
            'close-modal': closeModal,
        };
        actions[action]?.();
    };

    const openRoutineModal = (index = null) => {
        const isEditing = index !== null;
        const routine = isEditing ? JSON.parse(JSON.stringify(config.routines[index])) : { name: '', room_name: '', enabled: true, daily_time: {H1:7, M1:0, H2:23, M2:0}, morning:{scene_name:'none', x_scene_name:'none'}, day:{scene_name:'none', x_scene_name:'none'}, evening:{scene_name:'none', x_scene_name:'none'}, night:{scene_name:'none', x_scene_name:'none'} };
        
        const groupOptions = bridgeData.groups.map(g => `<option value="${g.name}" ${g.name === routine.room_name ? 'selected' : ''}>${g.name}</option>`).join('');
        const sensorOptions = bridgeData.sensors.map(s => `<option value="${s.id}" ${s.id == routine.sensor_id ? 'selected' : ''}>${s.name}</option>`).join('');
        const sceneOptions = Object.keys(config.scenes || {}).map(name => `<option value="${name}">${config.scenes[name].name || name}</option>`).join('');
        const timeSpans = ['morning', 'day', 'evening', 'night'];

        const timeSpanHTML = timeSpans.map(span => {
            const data = routine[span] || {};
            const waitTime = data.wait_time || { min: 5, sec: 0 };
            return `
            <div class="p-4 border-2 rounded-lg ${SECTION_COLORS[span]}">
                <h4 class="font-semibold capitalize text-lg mb-3 flex items-center">${ICONS[span]} <span class="ml-2">${span}</span></h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div><label class="block text-sm font-medium">Normal-Szene</label><select data-section="${span}" data-field="scene_name" class="mt-1 w-full rounded-md dark:bg-gray-800"><option value="none">Keine</option>${sceneOptions.replace(`value="${data.scene_name}"`, `value="${data.scene_name}" selected`)}</select></div>
                    <div><label class="block text-sm font-medium">Bewegungs-Szene</label><select data-section="${span}" data-field="x_scene_name" class="mt-1 w-full rounded-md dark:bg-gray-800"><option value="none">Keine</option>${sceneOptions.replace(`value="${data.x_scene_name}"`, `value="${data.x_scene_name}" selected`)}</select></div>
                    <div class="col-span-2 space-y-3 border-t dark:border-gray-600 pt-3 mt-2">
                        <label class="flex items-center"><input type="checkbox" data-section="${span}" data-field="bri_check" ${data.bri_check ? 'checked' : ''} class="h-4 w-4 rounded mr-2">Helligkeit prüfen (für Bewegung)</label>
                        <div><label class="block text-sm font-medium">Max. Helligkeit (Lux)</label><input type="number" data-section="${span}" data-field="max_light_level" value="${data.max_light_level || 0}" class="mt-1 w-full rounded-md dark:bg-gray-800"></div>
                        <label class="flex items-center"><input type="checkbox" data-section="${span}" data-field="motion_check" ${data.motion_check ? 'checked' : ''} class="h-4 w-4 rounded mr-2">Auf Bewegung reagieren</label>
                        <div><label class="block text-sm font-medium">Ausschaltverzögerung</label><div class="flex items-center space-x-2"><input type="number" data-section="${span}" data-field="wait_time_min" value="${waitTime.min}" class="mt-1 w-full rounded-md dark:bg-gray-800" placeholder="min"><input type="number" data-section="${span}" data-field="wait_time_sec" value="${waitTime.sec}" class="mt-1 w-full rounded-md dark:bg-gray-800" placeholder="sec"></div></div>
                        <label class="flex items-center"><input type="checkbox" data-section="${span}" data-field="do_not_disturb" ${data.do_not_disturb ? 'checked' : ''} class="h-4 w-4 rounded mr-2">Bitte nicht stören</label>
                    </div>
                </div>
            </div>`;
        }).join('');

        const formContent = `
            <input type="hidden" id="routine-index" value="${index || ''}">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><label class="block text-sm font-medium">Name</label><input type="text" id="routine-name" value="${routine.name}" required class="mt-1 block w-full rounded-md dark:bg-gray-700"></div>
                <div><label class="block text-sm font-medium">Raum</label><select id="routine-room" required class="mt-1 block w-full rounded-md dark:bg-gray-700"><option value="">Wählen...</option>${groupOptions}</select></div>
                <div><label class="block text-sm font-medium">Bewegungsmelder (optional)</label><select id="routine-sensor" class="mt-1 block w-full rounded-md dark:bg-gray-700"><option value="">Kein Sensor</option>${sensorOptions}</select></div>
                <div><label class="block text-sm font-medium">Startzeit</label><input type="time" id="routine-start-time" value="${String(routine.daily_time.H1).padStart(2, '0')}:${String(routine.daily_time.M1).padStart(2, '0')}" class="mt-1 w-full rounded-md dark:bg-gray-700"></div>
                <div><label class="block text-sm font-medium">Endzeit</label><input type="time" id="routine-end-time" value="${String(routine.daily_time.H2).padStart(2, '0')}:${String(routine.daily_time.M2).padStart(2, '0')}" class="mt-1 w-full rounded-md dark:bg-gray-700"></div>
            </div>
            <h3 class="text-lg font-semibold mt-6 mb-2 border-t dark:border-gray-600 pt-4">Ablauf-Konfiguration</h3>
            <div class="space-y-4">${timeSpanHTML}</div>`;

        modalContainer.innerHTML = getModalHTML(isEditing ? 'Routine bearbeiten' : 'Neue Routine', formContent, 'Speichern');
        modalContainer.querySelector('form').id = 'modal-form';
        modalContainer.querySelector('form').addEventListener('submit', e => handleSaveRoutine(e, index));
    };

    const handleSaveRoutine = (e, index) => {
        e.preventDefault();
        const isEditing = index !== null;
        const routine = isEditing ? config.routines[index] : { enabled: true };
        
        routine.name = getEl('routine-name').value;
        routine.room_name = getEl('routine-room').value;
        routine.sensor_id = getEl('routine-sensor').value;
        const [startH, startM] = getEl('routine-start-time').value.split(':');
        const [endH, endM] = getEl('routine-end-time').value.split(':');
        routine.daily_time = { H1: parseInt(startH), M1: parseInt(startM), H2: parseInt(endH), M2: parseInt(endM) };

        queryAll('[data-section]').forEach(el => {
            const section = el.dataset.section;
            const field = el.dataset.field;
            if (!routine[section]) routine[section] = {};
            
            if (field.startsWith('wait_time')) {
                if (!routine[section].wait_time) routine[section].wait_time = {};
                const type = field.split('_')[2];
                routine[section].wait_time[type] = parseInt(el.value) || 0;
            } else {
                routine[section][field] = el.type === 'checkbox' ? el.checked : (el.type === 'number' ? parseInt(el.value) : el.value);
            }
        });

        if (!isEditing) {
            if (!config.routines) config.routines = [];
            config.routines.push(routine);
        }
        render('routines');
        closeModal();
        showToast(`Routine '${routine.name}' gespeichert.`);
    };
    
    const openSceneModal = (key = null) => {
        const isEditing = key !== null;
        const scene = isEditing ? config.scenes[key] : { name: '', on: true, bri: 128 };
        const formContent = `
            <input type="hidden" id="scene-key" value="${key || ''}">
            <div class="mb-4"><label class="block text-sm font-medium">Name</label><input type="text" id="scene-name" value="${scene.name || key || ''}" required class="mt-1 block w-full rounded-md dark:bg-gray-700"></div>
            <div id="color-picker-container" class="flex justify-center my-4"></div>
            <div class="mb-4"><label class="block text-sm font-medium">Helligkeit</label><input type="range" id="scene-bri" min="1" max="254" value="${scene.bri}" class="w-full"></div>
            <div class="flex items-center"><input type="checkbox" id="scene-on" ${scene.on ? 'checked' : ''} class="h-4 w-4 rounded"><label for="scene-on" class="ml-2">Licht an</label></div>`;
        
        modalContainer.innerHTML = getModalHTML(isEditing ? 'Szene bearbeiten' : 'Neue Szene', formContent, 'Speichern');
        modalContainer.querySelector('form').id = 'modal-form';
        
        colorPicker = new iro.ColorPicker('#color-picker-container', { width: 280, color: scene.hue ? {h: scene.hue/182, s: scene.sat/2.54, v:100} : '#fff', layout: [{ component: iro.ui.Wheel }, { component: iro.ui.Slider, options: { sliderType: 'saturation' } }] });
        modalContainer.querySelector('form').addEventListener('submit', e => handleSaveScene(e, key));
    };

    const handleSaveScene = (e, key) => {
        e.preventDefault();
        const name = getEl('scene-name').value;
        if (!name) return showToast('Szenenname ist erforderlich.', true);

        const newKey = name.replace(/\s+/g, '_').toLowerCase();
        const sceneData = {
            name: name,
            on: getEl('scene-on').checked,
            bri: parseInt(getEl('scene-bri').value),
            hue: Math.round(colorPicker.color.hsv.h * 182.04),
            sat: Math.round(colorPicker.color.hsv.s * 2.54),
        };
        
        const isEditing = key !== null;
        if (isEditing && key !== newKey) delete config.scenes[key];
        if (!config.scenes) config.scenes = {};
        config.scenes[newKey] = sceneData;

        render('scenes');
        closeModal();
        showToast('Szene gespeichert.');
    };

    const openSettingsModal = () => {
        const bridge = config.hue_bridge || {};
        const formContent = `
            <h4 class="text-lg font-semibold mb-2">Hue Bridge</h4>
            <div class="space-y-3 p-4 border dark:border-gray-600 rounded-md">
                <div><label class="block text-sm font-medium">IP-Adresse</label><input type="text" id="setting-ip" value="${bridge.ip_address || ''}" class="mt-1 w-full rounded-md dark:bg-gray-700"></div>
                <div><label class="block text-sm font-medium">API Key (Username)</label><input type="password" id="setting-key" value="${bridge.api_key || ''}" class="mt-1 w-full rounded-md dark:bg-gray-700"></div>
            </div>`;
        modalContainer.innerHTML = getModalHTML('Einstellungen', formContent, 'Speichern');
        modalContainer.querySelector('form').id = 'modal-form';
        modalContainer.querySelector('form').addEventListener('submit', handleSaveSettings);
    };

    const handleSaveSettings = e => {
        e.preventDefault();
        if (!config.hue_bridge) config.hue_bridge = {};
        config.hue_bridge.ip_address = getEl('setting-ip').value;
        config.hue_bridge.api_key = getEl('setting-key').value;
        closeModal();
        showToast('Einstellungen übernommen. Bitte global speichern & neustarten.');
    };
    
    const toggleRoutine = index => {
        const routine = config.routines[index];
        if (routine) {
            routine.enabled = !routine.enabled;
            showToast(`Routine '${routine.name}' ${routine.enabled ? 'aktiviert' : 'deaktiviert'}.`);
            saveAndRestart();
        }
    };

    const deleteItem = (type, id) => {
        const name = type === 'routines' ? config.routines[id].name : (config.scenes[id].name || id);
        if (confirm(`Soll '${name}' wirklich gelöscht werden?`)) {
            if (type === 'routines') config.routines.splice(id, 1);
            if (type === 'scenes') delete config.scenes[id];
            render(type);
            showToast('Element gelöscht.');
        }
    };

    const closeModal = () => {
        modalContainer.innerHTML = '';
        colorPicker = null;
    };
    
    const switchTab = tab => {
        if (statusInterval) clearInterval(statusInterval);
        queryAll('.tab-content').forEach(c => c.classList.add('hidden'));
        queryAll('.tab-button').forEach(b => b.classList.remove('tab-active'));
        const activeButton = queryEl(`.tab-button[data-tab="${tab}"]`);
        const activeContent = getEl(`tab-content-${tab}`);
        if (activeButton) activeButton.classList.add('tab-active');
        if (activeContent) {
            activeContent.classList.remove('hidden');
            render(tab);
        }
    };

    // --- App starten ---
    init();
});
