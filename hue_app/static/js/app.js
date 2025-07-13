document.addEventListener('DOMContentLoaded', () => {
    let config = {};
    let bridgeData = { groups: [], sensors: [] };
    let statusInterval;
    let colorPicker = null;

    const routinesContainer = document.getElementById('routines-container');
    const scenesContainer = document.getElementById('scenes-container');
    const statusContainer = document.getElementById('status-container');
    const logContainer = document.getElementById('log-container');
    const saveButton = document.getElementById('save-button');
    const toastElement = document.getElementById('toast');
    const clockElement = document.getElementById('clock');
    const refreshButton = document.getElementById('btn-refresh-status');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');

    const translations = {
        de: {
            title: "Hue Editor",
            subtitle: "Verwalte deine Routinen und Lichtszenen.",
            tab_routines: "Routinen",
            tab_scenes: "Szenen",
            tab_status: "Status",
            tab_settings: "Einstellungen",
            btn_new_routine: "+ Neue Routine",
            btn_new_scene: "+ Neue Szene",
            status_title: "Live-Zustand der Routinen",
            btn_refresh: "Jetzt aktualisieren",
            log_title: "Log-Datei (info.log)",
            settings_title: "Einstellungen",
            label_lang: "Sprache",
            label_ip: "Bridge IP-Adresse",
            label_refresh: "Status Aktualisierungsrate (Sekunden)",
            btn_save_all: "Speichern und Alle Routinen neu starten"
        },
        en: {
            title: "Hue Editor",
            subtitle: "Manage your routines and light scenes.",
            tab_routines: "Routines",
            tab_scenes: "Scenes",
            tab_status: "Status",
            tab_settings: "Settings",
            btn_new_routine: "+ New Routine",
            btn_new_scene: "+ New Scene",
            status_title: "Live State of Routines",
            btn_refresh: "Refresh Now",
            log_title: "Log File (info.log)",
            settings_title: "Settings",
            label_lang: "Language",
            label_ip: "Bridge IP Address",
            label_refresh: "Status Refresh Rate (seconds)",
            btn_save_all: "Save and Restart All Routines"
        }
    };

    const icons = {
        morning: '🌅',
        day: '☀️',
        evening: '🌄',
        night: '🌕'
    };
    
    const sectionColors = {
        morning: 'bg-amber-100',
        day: 'bg-yellow-100',
        evening: 'bg-orange-100',
        night: 'bg-blue-100'
    };

    const init = async () => {
        updateClock();
        setInterval(updateClock, 1000);
        applyTheme();
        showLoading();
        try {
            const [configRes, groupsRes, sensorsRes] = await Promise.all([
                fetch('/api/config'),
                fetch('/api/bridge/groups'),
                fetch('/api/bridge/sensors')
            ]);
            config = await configRes.json();
            bridgeData.groups = await groupsRes.json();
            bridgeData.sensors = await sensorsRes.json();
            renderAll();
            populateSettings();
            setLanguage(config.settings?.language || 'de');
        } catch (error) {
            console.error("Initialisierungsfehler:", error);
            showToast("Fehler beim Laden der Daten. Läuft der Server?", true);
        } finally {
            hideLoading();
        }
    };

    const renderAll = () => {
        renderRoutines();
        renderScenes();
    };

    const renderRoutines = () => {
        routinesContainer.innerHTML = '';
        if (!config.routines || config.routines.length === 0) {
            routinesContainer.innerHTML = `<p class="text-gray-500 text-center">Noch keine Routinen erstellt.</p>`;
            return;
        }
        config.routines.forEach((routine, index) => {
            const routineEl = document.createElement('div');
            routineEl.className = 'bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border-2 border-gray-200 dark:border-gray-700';
            const sections = ['morning', 'day', 'evening', 'night'];
            
            const sectionsHtml = sections.map(name => {
                const section = routine[name];
                if (!section) return '';
                const waitTime = section.wait_time || {min: 0, sec: 0};
                const waitTimeString = `${waitTime.min || 0}m ${waitTime.sec || 0}s`;

                return `
                <div class="py-2 px-3 bg-gray-100 dark:bg-gray-700 rounded-md">
                    <p class="font-semibold capitalize flex items-center">${icons[name] || ''} <span class="ml-2">${name}</span></p>
                    <div class="text-sm text-gray-700 dark:text-gray-300 grid grid-cols-2 gap-x-4">
                        <span><strong class="font-medium">Normal-Szene:</strong> ${section.scene_name}</span>
                        <span><strong class="font-medium">Bewegungs-Szene:</strong> ${section.x_scene_name}</span>
                        <span><strong class="font-medium">Bewegung:</strong> ${section.motion_check ? `Ja (${waitTimeString})` : 'Nein'}</span>
                        <span><strong class="font-medium">Nicht stören:</strong> ${section.do_not_disturb ? 'Ja' : 'Nein'}</span>
                        <span><strong class="font-medium">Helligkeits-Check:</strong> ${section.bri_check ? 'Ja' : 'Nein'}</span>
                        ${section.bri_check ? `<span><strong class="font-medium">Max. Helligkeit:</strong> ${section.max_light_level}</span>` : ''}
                    </div>
                </div>
            `}).join('');
            
            const dailyTime = routine.daily_time || {H1:0,M1:0,H2:23,M2:59};

            const isEnabled = routine.enabled !== false;

            routineEl.innerHTML = `
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-2xl font-semibold">${routine.name}</h3>
                        <div class="flex items-center text-gray-500 dark:text-gray-400 text-sm">
                            <p>Raum: ${routine.room_name}</p>
                            <span class="mx-2">|</span>
                            <p>Aktiv: ${String(dailyTime.H1).padStart(2,'0')}:${String(dailyTime.M1).padStart(2,'0')} - ${String(dailyTime.H2).padStart(2,'0')}:${String(dailyTime.M2).padStart(2,'0')}</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <label class="relative inline-flex items-center cursor-pointer" title="Routine an/aus">
                            <input type="checkbox" data-action="toggle-routine" data-index="${index}" class="sr-only peer" ${isEnabled ? 'checked' : ''}>
                            <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-2 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                        <button type="button" data-action="edit-routine" data-index="${index}" class="text-blue-500 hover:text-blue-700 font-semibold">Bearbeiten</button>
                        <button type="button" data-action="delete-routine" data-index="${index}" class="text-red-500 hover:text-red-700 font-semibold">Löschen</button>
                    </div>
                </div>
                <div class="space-y-2">
                    <h4 class="text-lg font-medium border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">Ablauf</h4>
                    ${sectionsHtml}
                </div>
            `;
            routinesContainer.appendChild(routineEl);
        });
    };

    const renderScenes = () => {
        scenesContainer.innerHTML = '';
        if (!config.scenes || Object.keys(config.scenes).length === 0) {
            scenesContainer.innerHTML = `<p class="text-gray-500 text-center">Noch keine Szenen erstellt.</p>`;
            return;
        }
        for (const [name, scene] of Object.entries(config.scenes)) {
            const sceneEl = document.createElement('div');
            sceneEl.className = 'bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md flex flex-col justify-between border-2 border-gray-200 dark:border-gray-700';
            
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
                    <div class="mt-2 text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        <p>Status: <span class="font-medium ${scene.status ? 'text-green-600' : 'text-red-600'}">${scene.status ? 'An' : 'Aus'}</span></p>
                        <p>Helligkeit: <span class="font-medium">${scene.bri}</span></p>
                        ${scene.hue !== undefined ? `<p>Farbton: <span class="font-medium">${scene.hue}</span></p>` : ''}
                        ${scene.sat !== undefined ? `<p>Sättigung: <span class="font-medium">${scene.sat}</span></p>` : ''}
                        ${scene.ct !== undefined ? `<p>Farbtemp.: <span class="font-medium">${scene.ct}</span></p>` : ''}
                    </div>
                </div>
                <div class="mt-4 flex justify-end space-x-2">
                     <button type="button" data-action="edit-scene" data-name="${name}" class="text-blue-500 hover:text-blue-700 font-semibold">Bearbeiten</button>
                     <button type="button" data-action="delete-scene" data-name="${name}" class="text-red-500 hover:text-red-700 font-semibold">Löschen</button>
                </div>
            `;
            scenesContainer.appendChild(sceneEl);
        }
    };

    const renderStatus = (statuses) => {
        statusContainer.innerHTML = '';
        if (!statuses || statuses.length === 0) {
            statusContainer.innerHTML = `<p class="text-gray-500">Warte auf Status-Daten...</p>`;
            return;
        }
        statuses.forEach(status => {
            const motionColor = status.motion_active ? 'text-green-500' : 'text-gray-500';
            const enabledColor = status.enabled ? 'text-green-500' : 'text-red-500';
            const statusEl = document.createElement('div');
            statusEl.className = 'bg-white dark:bg-gray-800 p-4 rounded-lg shadow border-2 border-gray-200 dark:border-gray-700';
            statusEl.innerHTML = `
                <h4 class="font-bold text-lg">${status.name}</h4>
                <div class="text-sm grid grid-cols-3 gap-2 mt-2">
                    <span><strong>Routine-Status:</strong> <span class="${enabledColor}">${status.enabled ? 'Aktiviert' : 'Deaktiviert'}</span></span>
                    <span><strong>Aktueller Zeitraum:</strong> <span class="flex items-center">${icons[status.period] || ''} <span class="ml-1">${status.period || 'Inaktiv'}</span></span></span>
                    <span><strong>Letzte Szene:</strong> ${status.last_scene || 'N/A'}</span>
                    <span class="${motionColor} col-span-3"><strong>Bewegung:</strong> ${status.motion_status || 'N/A'}</span>
                </div>
            `;
            statusContainer.appendChild(statusEl);
        });
    };

    const renderLog = (logText) => {
        logContainer.innerHTML = '';
        const lines = logText.split('\n');
        lines.forEach(line => {
            const span = document.createElement('span');
            if (line.includes('ERROR')) {
                span.className = 'text-red-400';
            } else if (line.includes('WARNING')) {
                span.className = 'text-yellow-400';
            } else if (line.includes('DEBUG')) {
                span.className = 'text-blue-400';
            } else {
                span.className = 'text-gray-300';
            }
            span.textContent = line + '\n';
            logContainer.appendChild(span);
        });
        logContainer.scrollTop = logContainer.scrollHeight;
    };

    const openSceneModal = (sceneName = null) => {
        const isEditing = sceneName !== null;
        const scene = isEditing ? config.scenes[sceneName] : { status: true, bri: 128, sat: 254, ct: 300, t_time: 10 };
        const modal = document.getElementById('modal-scene');
        
        const isColorMode = scene.hue !== undefined;

        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md m-4">
                <div class="p-6">
                    <h3 class="text-2xl font-bold mb-4">${isEditing ? 'Szene bearbeiten' : 'Neue Szene erstellen'}</h3>
                    <form id="form-scene" class="space-y-4">
                        <input type="hidden" id="scene-original-name" value="${sceneName || ''}">
                        <div>
                            <label for="scene-name" class="block text-sm font-medium">Szenen-Name</label>
                            <input type="text" id="scene-name" value="${isEditing ? sceneName : ''}" required class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm dark:bg-gray-700" ${isEditing ? 'readonly' : ''}>
                        </div>
                        
                        <div class="flex space-x-4 border-b dark:border-gray-700 pb-2">
                            <label><input type="radio" name="color-mode" value="ct" ${!isColorMode ? 'checked' : ''}> Weißtöne</label>
                            <label><input type="radio" name="color-mode" value="color" ${isColorMode ? 'checked' : ''}> Farbe</label>
                        </div>

                        <div id="ct-controls" class="${isColorMode ? 'hidden' : ''}">
                            <label for="scene-ct" class="block text-sm font-medium">Farbtemperatur (Kalt ⟷ Warm)</label>
                            <input type="range" id="scene-ct" min="153" max="500" value="${scene.ct || 300}" class="w-full ct-slider">
                        </div>

                        <div id="color-controls" class="${!isColorMode ? 'hidden' : ''}">
                            <label class="block text-sm font-medium">Farbe</label>
                            <div id="color-picker-container" class="flex justify-center my-2"></div>
                        </div>

                        <div>
                            <label for="scene-bri" class="block text-sm font-medium">Helligkeit (0-254)</label>
                            <input type="range" id="scene-bri" min="0" max="254" value="${scene.bri}" class="w-full">
                        </div>

                        <div class="flex items-center">
                            <input type="checkbox" id="scene-status" ${scene.status ? 'checked' : ''} class="h-4 w-4 rounded border-gray-300">
                            <label for="scene-status" class="ml-2 block text-sm">Licht an</label>
                        </div>
                    </form>
                </div>
                <div class="bg-gray-50 dark:bg-gray-900 px-6 py-3 flex justify-end space-x-3">
                    <button type="button" data-action="cancel-modal" class="bg-white dark:bg-gray-700 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-600">Abbrechen</button>
                    <button type="button" data-action="save-scene" class="bg-blue-600 text-white py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium hover:bg-blue-700">Speichern</button>
                </div>
            </div>
        `;
        modal.classList.remove('hidden');

        colorPicker = new iro.ColorPicker('#color-picker-container', {
            width: 250,
            color: isColorMode ? { h: (scene.hue || 0) / 65535 * 360, s: (scene.sat || 0) / 2.54, v: 100 } : '#fff',
            borderWidth: 1,
            borderColor: '#ccc',
            layout: [ { component: iro.ui.Wheel }, { component: iro.ui.Slider, options: { sliderType: 'saturation' } } ]
        });

        document.querySelectorAll('input[name="color-mode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                document.getElementById('ct-controls').classList.toggle('hidden', e.target.value !== 'ct');
                document.getElementById('color-controls').classList.toggle('hidden', e.target.value !== 'color');
            });
        });
    };

    const openEditRoutineModal = (routineIndex) => {
        const routine = config.routines[routineIndex];
        const modal = document.getElementById('modal-routine');
        const sceneOptions = Object.keys(config.scenes).map(name => `<option value="${name}">${name}</option>`).join('');
        const sectionNames = ['morning', 'day', 'evening', 'night'];
        
        const sectionsHtml = sectionNames.map(name => {
            const section = routine[name] || { scene_name: 'off', x_scene_name: 'off', bri_check: false, max_light_level: 0, motion_check: false, wait_time: {min: 5, sec: 0}, do_not_disturb: false };
            const waitTime = section.wait_time || {min: 5, sec: 0};
            return `
            <div class="p-4 border-2 rounded-lg ${sectionColors[name]}" data-section-name="${name}">
                <h5 class="font-semibold capitalize mb-3 text-lg flex items-center">${icons[name] || ''} <span class="ml-2">${name}</span></h5>
                
                <div class="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                    <!-- Szenen -->
                    <div><label class="block font-medium">Normal-Szene</label><select class="mt-1 block w-full rounded-md border-gray-300 shadow-sm section-scene-name">${sceneOptions.replace(`value="${section.scene_name}"`, `value="${section.scene_name}" selected`)}</select></div>
                    <div><label class="block font-medium">Szene bei Bewegung</label><select class="mt-1 block w-full rounded-md border-gray-300 shadow-sm section-x-scene-name">${sceneOptions.replace(`value="${section.x_scene_name}"`, `value="${section.x_scene_name}" selected`)}</select></div>
                    
                    <!-- Helligkeit -->
                    <div class="col-span-2 border-t mt-2 pt-2">
                        <div class="flex items-center"><input type="checkbox" ${section.bri_check ? 'checked' : ''} class="h-4 w-4 rounded border-gray-300 section-bri-check"><label class="ml-2 font-medium">Helligkeit prüfen (für Bewegung)</label></div>
                        <div class="mt-1"><label class="block">Max. Helligkeit</label><input type="number" value="${section.max_light_level}" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm section-max-light-level"></div>
                    </div>

                    <!-- Bewegung -->
                    <div class="col-span-2 border-t mt-2 pt-2">
                        <div class="flex items-center"><input type="checkbox" ${section.motion_check ? 'checked' : ''} class="h-4 w-4 rounded border-gray-300 section-motion-check"><label class="ml-2 font-medium">Auf Bewegung reagieren</label></div>
                        <div class="mt-1">
                            <label class="block">Ausschaltverzögerung</label>
                            <div class="flex items-center space-x-2">
                                <input type="number" value="${waitTime.min}" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm section-wait-time-min" placeholder="min">
                                <input type="number" value="${waitTime.sec}" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm section-wait-time-sec" placeholder="sec">
                            </div>
                        </div>
                        <div class="flex items-center mt-2"><input type="checkbox" ${section.do_not_disturb ? 'checked' : ''} class="h-4 w-4 rounded border-gray-300 section-do-not-disturb"><label class="ml-2">Bitte nicht stören</label></div>
                    </div>
                </div>
            </div>
        `}).join('');

        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl m-4">
                <div class="p-6">
                    <h3 class="text-2xl font-bold mb-4">Routine bearbeiten</h3>
                    <form id="form-routine" class="space-y-4">
                        <input type="hidden" id="routine-index" value="${routineIndex}">
                        <div>
                            <label class="block text-sm font-medium">Routine-Name</label>
                            <input type="text" id="routine-name" value="${routine.name}" required class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm dark:bg-gray-700">
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium">Startzeit (Gesamt)</label>
                                <input type="time" id="routine-start-time" value="${String(routine.daily_time.H1).padStart(2,'0')}:${String(routine.daily_time.M1).padStart(2,'0')}" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm dark:bg-gray-700">
                            </div>
                            <div>
                                <label class="block text-sm font-medium">Endzeit (Gesamt)</label>
                                <input type="time" id="routine-end-time" value="${String(routine.daily_time.H2).padStart(2,'0')}:${String(routine.daily_time.M2).padStart(2,'0')}" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm dark:bg-gray-700">
                            </div>
                        </div>
                        <div class="border-t dark:border-gray-700 pt-4 mt-4">
                            <h4 class="text-lg font-medium mb-2">Ablauf-Konfiguration</h4>
                            <div id="sections-editor" class="space-y-3 modal-body">${sectionsHtml}</div>
                        </div>
                    </form>
                </div>
                <div class="bg-gray-50 dark:bg-gray-900 px-6 py-3 flex justify-end space-x-3">
                    <button type="button" data-action="cancel-modal" class="bg-white dark:bg-gray-700 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-600">Abbrechen</button>
                    <button type="button" data-action="save-routine" class="bg-blue-600 text-white py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium hover:bg-blue-700">Routine speichern</button>
                </div>
            </div>
        `;
        modal.classList.remove('hidden');
    };
    
    const openCreateRoutineModal = () => {
         const modal = document.getElementById('modal-routine');
         const groupOptions = bridgeData.groups.map(g => `<option value="${g.id}|${g.name}">${g.name}</option>`).join('');
         const sensorOptions = bridgeData.sensors.map(s => `<option value="${s.id}">${s.name} (ID: ${s.id})</option>`).join('');

         modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-lg m-4">
                <div class="p-6">
                    <h3 class="text-2xl font-bold mb-4">Neue Routine erstellen</h3>
                    <form id="form-create-routine" class="space-y-4">
                         <div>
                            <label for="new-routine-name" class="block text-sm font-medium">Routine-Name</label>
                            <input type="text" id="new-routine-name" required class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm dark:bg-gray-700">
                        </div>
                        <div>
                            <label for="new-routine-group" class="block text-sm font-medium">Raum / Zone</label>
                            <select id="new-routine-group" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm dark:bg-gray-700">${groupOptions}</select>
                        </div>
                         <div>
                            <label for="new-routine-sensor" class="block text-sm font-medium">Bewegungsmelder</label>
                            <select id="new-routine-sensor" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm dark:bg-gray-700">
                                <option value="">Kein Sensor (rein zeitgesteuert)</option>
                                ${sensorOptions}
                            </select>
                        </div>
                    </form>
                </div>
                <div class="bg-gray-50 dark:bg-gray-900 px-6 py-3 flex justify-end space-x-3">
                    <button type="button" data-action="cancel-modal" class="bg-white dark:bg-gray-700 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-600">Abbrechen</button>
                    <button type="button" data-action="create-routine" class="bg-blue-600 text-white py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium hover:bg-blue-700">Routine erstellen</button>
                </div>
            </div>
         `;
         modal.classList.remove('hidden');
    };

    const closeModal = () => {
        document.getElementById('modal-scene').classList.add('hidden');
        document.getElementById('modal-routine').classList.add('hidden');
    };

    const handleSaveScene = () => {
        const originalName = document.getElementById('scene-original-name').value;
        const newName = document.getElementById('scene-name').value.trim().replace(/\s+/g, '_').toLowerCase();
        if (!newName) { showToast("Szenen-Name darf nicht leer sein.", true); return; }

        const newScene = {
            status: document.getElementById('scene-status').checked,
            bri: parseInt(document.getElementById('scene-bri').value),
            t_time: 10
        };

        const mode = document.querySelector('input[name="color-mode"]:checked').value;
        if (mode === 'color') {
            if(colorPicker) {
                const hsv = colorPicker.color.hsv;
                newScene.hue = Math.round(hsv.h / 360 * 65535);
                newScene.sat = Math.round(hsv.s * 2.54);
                delete newScene.ct;
            }
        } else {
            newScene.ct = parseInt(document.getElementById('scene-ct').value);
            newScene.sat = 0;
            delete newScene.hue;
        }

        if (originalName && originalName !== newName) { delete config.scenes[originalName]; }
        config.scenes[newName] = newScene;
        renderAll();
        closeModal();
        showToast("Szene gespeichert. Globale Speicherung nicht vergessen!");
    };

    const handleSaveEditedRoutine = () => {
        const routineIndex = document.getElementById('routine-index').value;
        if (routineIndex === '') return;

        const updatedRoutine = config.routines[routineIndex];
        updatedRoutine.name = document.getElementById('routine-name').value;
        
        const [startH, startM] = document.getElementById('routine-start-time').value.split(':');
        const [endH, endM] = document.getElementById('routine-end-time').value.split(':');
        updatedRoutine.daily_time = { H1: parseInt(startH), M1: parseInt(startM), H2: parseInt(endH), M2: parseInt(endM) };

        document.querySelectorAll('#sections-editor > div').forEach(sectionEl => {
            const name = sectionEl.dataset.sectionName;
            if(name) {
                updatedRoutine[name] = {
                    scene_name: sectionEl.querySelector('.section-scene-name').value,
                    x_scene_name: sectionEl.querySelector('.section-x-scene-name').value,
                    bri_check: sectionEl.querySelector('.section-bri-check').checked,
                    max_light_level: parseInt(sectionEl.querySelector('.section-max-light-level').value),
                    motion_check: sectionEl.querySelector('.section-motion-check').checked,
                    wait_time: {
                        min: parseInt(sectionEl.querySelector('.section-wait-time-min').value) || 0,
                        sec: parseInt(sectionEl.querySelector('.section-wait-time-sec').value) || 0
                    },
                    do_not_disturb: sectionEl.querySelector('.section-do-not-disturb').checked
                };
            }
        });

        renderAll();
        closeModal();
        showToast("Routine aktualisiert. Globale Speicherung nicht vergessen!");
    };
    
    const handleCreateNewRoutine = () => {
        const name = document.getElementById('new-routine-name').value;
        const [groupId, groupName] = document.getElementById('new-routine-group').value.split('|');
        const sensorId = document.getElementById('new-routine-sensor').value;

        if (!name || !groupId) {
            showToast("Bitte Routine-Name und Raum ausfüllen.", true);
            return;
        }
        
        if (!config.rooms) config.rooms = [];
        if (!config.routines) config.routines = [];

        if (!config.rooms.some(r => r.name === groupName)) {
            const newRoom = {
                name: groupName,
                group_ids: [parseInt(groupId)],
                switch_ids: []
            };
            if (sensorId) {
                newRoom.sensor_id = parseInt(sensorId);
            }
            config.rooms.push(newRoom);
        }

        const newRoutine = {
            name: name,
            room_name: groupName,
            enabled: true,
            daily_time: { H1: 7, M1: 0, H2: 23, M2: 0 },
            morning: { scene_name: "warm_min", x_scene_name: "off", bri_check: false, max_light_level: 0, motion_check: true, wait_time: {min: 2, sec: 0}, do_not_disturb: true },
            day: { scene_name: "warm_mid", x_scene_name: "off", bri_check: true, max_light_level: 18000, motion_check: true, wait_time: {min: 5, sec: 0}, do_not_disturb: true },
            evening: { scene_name: "warm_max", x_scene_name: "off", bri_check: false, max_light_level: 0, motion_check: true, wait_time: {min: 10, sec: 0}, do_not_disturb: false },
            night: { scene_name: "night", x_scene_name: "off", bri_check: false, max_light_level: 0, motion_check: true, wait_time: {min: 1, sec: 0}, do_not_disturb: false }
        };
        config.routines.push(newRoutine);

        renderAll();
        closeModal();
        showToast("Routine erstellt. Globale Speicherung nicht vergessen!");
    };
    
    const saveFullConfig = async () => {
        saveButton.disabled = true;
        saveButton.textContent = 'Speichere...';
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error);
            showToast(result.message);
        } catch (error) {
            showToast(`Fehler: ${error.message}`, true);
        } finally {
            saveButton.disabled = false;
            saveButton.textContent = 'Speichern und Alle Routinen neu starten';
        }
    };

    const updateStatus = async () => {
        try {
            const [statusRes, logRes] = await Promise.all([
                fetch('/api/status'),
                fetch('/api/log')
            ]);
            const statuses = await statusRes.json();
            const logText = await logRes.text();
            renderStatus(statuses);
            renderLog(logText);
        } catch (error) {
            console.error("Fehler beim Abrufen des Status:", error);
        }
    };

    const startStatusUpdates = () => {
        if (statusInterval) clearInterval(statusInterval);
        updateStatus();
        statusInterval = setInterval(updateStatus, 30000); // Reduziert auf 30 Sekunden
    };

    const updateClock = () => {
        const now = new Date();
        clockElement.textContent = now.toLocaleTimeString('de-DE');
    };

    const applyTheme = () => {
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
            moonIcon.classList.remove('hidden');
            sunIcon.classList.add('hidden');
        } else {
            document.documentElement.classList.remove('dark');
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    };

    darkModeToggle.addEventListener('click', () => {
        if (localStorage.theme === 'dark') {
            localStorage.theme = 'light';
        } else {
            localStorage.theme = 'dark';
        }
        applyTheme();
    });

    document.body.addEventListener('click', (e) => {
        const action = e.target.dataset.action;
        const target = e.target;

        switch(action) {
            case 'toggle-routine':
                const routineIndex = parseInt(target.dataset.index);
                config.routines[routineIndex].enabled = target.checked;
                showToast(`Routine '${config.routines[routineIndex].name}' ${target.checked ? 'aktiviert' : 'deaktiviert'}.`);
                saveFullConfig();
                break;
            case 'delete-scene':
                if (confirm(`Möchtest du die Szene "${target.dataset.name}" wirklich löschen?`)) {
                    delete config.scenes[target.dataset.name];
                    renderAll();
                    showToast("Szene gelöscht.");
                }
                break;
            case 'delete-routine':
                if (confirm(`Möchtest du die Routine "${config.routines[target.dataset.index].name}" wirklich löschen?`)) {
                    config.routines.splice(target.dataset.index, 1);
                    renderAll();
                    showToast("Routine gelöscht.");
                }
                break;
            case 'edit-scene': openSceneModal(target.dataset.name); break;
            case 'edit-routine': openEditRoutineModal(target.dataset.index); break;
            case 'save-scene': handleSaveScene(); break;
            case 'save-routine': handleSaveEditedRoutine(); break;
            case 'create-routine': handleCreateNewRoutine(); break;
            case 'cancel-modal': closeModal(); break;
        }
    });

    document.getElementById('btn-new-scene').addEventListener('click', () => openSceneModal());
    document.getElementById('btn-new-routine').addEventListener('click', () => openCreateRoutineModal());
    saveButton.addEventListener('click', saveFullConfig);
    refreshButton.addEventListener('click', updateStatus);
    
    const tabs = [{btn: 'tab-routines', content: 'content-routines'}, {btn: 'tab-scenes', content: 'content-scenes'}, {btn: 'tab-status', content: 'content-status'}, {btn: 'tab-settings', content: 'content-settings'}];
    tabs.forEach(tabInfo => {
        document.getElementById(tabInfo.btn).addEventListener('click', () => {
            tabs.forEach(t => {
                document.getElementById(t.btn).classList.remove('tab-active');
                document.getElementById(t.content).classList.add('hidden');
            });
            document.getElementById(tabInfo.btn).classList.add('tab-active');
            document.getElementById(tabInfo.content).classList.remove('hidden');
            if (tabInfo.btn === 'tab-status') {
                startStatusUpdates();
            } else {
                if (statusInterval) clearInterval(statusInterval);
            }
        });
    });

    const showToast = (message, isError = false) => {
        toastElement.textContent = message;
        toastElement.className = `fixed bottom-5 right-5 bg-gray-900 text-white py-2 px-4 rounded-lg shadow-xl transition-opacity duration-300 ${isError ? 'bg-red-600' : 'bg-gray-900'}`;
        toastElement.classList.remove('hidden');
        setTimeout(() => toastElement.classList.add('hidden'), 4000);
    };
    const showLoading = () => routinesContainer.innerHTML = `<p class="text-gray-500 text-center">Lade Daten von der Bridge...</p>`;
    const hideLoading = () => {};

    init();
});
