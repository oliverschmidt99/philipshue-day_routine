// web/static/js/main.js
import * as api from './modules/api.js';
import * as ui from './modules/ui.js';
import { runSetupWizard } from './modules/setup.js';

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const status = await api.checkSetupStatus();
        if (status.setup_needed) {
            document.getElementById('main-app').classList.add('hidden');
            document.getElementById('setup-wizard').classList.add('flex');
            runSetupWizard();
        } else {
            document.getElementById('setup-wizard').classList.add('hidden');
            document.getElementById('main-app').classList.remove('hidden');
            runMainApp();
        }
    } catch (error) {
        document.body.innerHTML = `<div class="m-4 p-4 text-center text-red-800 bg-red-100 rounded-lg shadow-md"><h2 class="text-xl font-bold">Verbindung zum Server fehlgeschlagen</h2><p class="mt-2">Das Backend (main.py) läuft nicht. Bitte starte es und lade die Seite neu.</p></div>`;
    }
});

function runMainApp() {
    let config = {};
    let bridgeData = {};
    let colorPicker = null;
    let statusInterval;
    let chartInstance = null;
    let clockAnimationInterval;

    const init = async () => {
        ui.updateClock();
        setInterval(ui.updateClock, 1000);
        try {
            [config, bridgeData] = await Promise.all([api.loadConfig(), api.loadBridgeData()]);
            renderAll();
            setupEventListeners();
        } catch (error) {
            ui.showToast(`Initialisierungsfehler: ${error.message}`, true);
        }
    };

    const renderAll = () => {
        ui.renderRoutines(config.routines);
        ui.renderScenes(config.scenes);
    };

    const setupEventListeners = () => {
        document.getElementById('save-button').addEventListener('click', saveFullConfig);
        document.getElementById('btn-new-routine').addEventListener('click', () => ui.openCreateRoutineModal(bridgeData));
        document.getElementById('btn-new-scene').addEventListener('click', () => { colorPicker = ui.openSceneModal({ status: true, bri: 128, ct: 366 }, null); });
        document.getElementById('btn-save-settings').addEventListener('click', saveSettings);
        document.body.addEventListener('click', e => {
            const button = e.target.closest('[data-action]');
            if (!button) return;
            const action = button.dataset.action;
            const routineCard = e.target.closest('[data-index]');
            const sceneCard = e.target.closest('[data-name]');
            const actions = {
                'toggle-routine': () => { config.routines[routineCard.dataset.index].enabled = button.checked; ui.showToast(`Routine ${button.checked ? 'aktiviert' : 'deaktiviert'}. Speichern nicht vergessen!`); },
                'delete-scene': () => { if (confirm(`Szene "${sceneCard.dataset.name}" löschen?`)) { delete config.scenes[sceneCard.dataset.name]; renderAll(); }},
                'delete-routine': () => { if (confirm(`Routine "${config.routines[routineCard.dataset.index].name}" löschen?`)) { config.routines.splice(routineCard.dataset.index, 1); renderAll(); }},
                'edit-scene': () => colorPicker = ui.openSceneModal(config.scenes[sceneCard.dataset.name], sceneCard.dataset.name),
                'edit-routine': () => ui.openEditRoutineModal(config.routines[routineCard.dataset.index], routineCard.dataset.index, Object.keys(config.scenes)),
                'save-scene': handleSaveScene,
                'save-routine': handleSaveEditedRoutine,
                'create-routine': handleCreateNewRoutine,
                'cancel-modal': ui.closeModal,
            };
            if (actions[action]) actions[action]();
        });
        const tabs = [ { btn: 'tab-routines', content: 'content-routines' }, { btn: 'tab-scenes', content: 'content-scenes' }, { btn: 'tab-status', content: 'content-status', init: startStatusUpdates }, { btn: 'tab-analyse', content: 'content-analyse', init: setupAnalyseTab }, { btn: 'tab-einstellungen', content: 'content-einstellungen', init: loadSettings }, { btn: 'tab-hilfe', content: 'content-hilfe', init: loadHelp } ];
        tabs.forEach(tabInfo => { const btn = document.getElementById(tabInfo.btn); if (!btn) return; btn.addEventListener('click', () => { tabs.forEach(t => { document.getElementById(t.btn)?.classList.remove('tab-active'); document.getElementById(t.content)?.classList.add('hidden'); }); btn.classList.add('tab-active'); document.getElementById(tabInfo.content)?.classList.remove('hidden'); if (statusInterval) clearInterval(statusInterval); if(clockAnimationInterval) clearInterval(clockAnimationInterval); if (tabInfo.init) tabInfo.init(); }); });
    };
    
    const updateStatus = async () => { try { const { statusData, logText } = await api.updateStatus(); ui.renderStatus(statusData.routines || [], statusData.sun_times); ui.renderSunTimes(statusData.sun_times || null); ui.renderLog(logText); } catch (error) { console.error("Fehler beim Abrufen des Status:", error); } };
    const animateClockIndicator = () => { const indicators = document.querySelectorAll('.current-time-indicator'); if (indicators.length === 0) return; const now = new Date(); const timeToPercent = (h, m) => ((h * 60 + m) / 1440) * 100; const nowPercent = timeToPercent(now.getHours(), now.getMinutes()); indicators.forEach(indicator => { indicator.style.transform = `translateX(${nowPercent}%)`; }); };
    const startStatusUpdates = () => { if (statusInterval) clearInterval(statusInterval); if (clockAnimationInterval) clearInterval(clockAnimationInterval); updateStatus(); statusInterval = setInterval(updateStatus, 5000); animateClockIndicator(); clockAnimationInterval = setInterval(animateClockIndicator, 1000); };
    const setupAnalyseTab = () => { ui.populateAnalyseSensors(bridgeData.sensors); const periodSelect = document.getElementById('analyse-period'); const datePicker = document.getElementById('analyse-date-picker'); const weekPicker = document.getElementById('analyse-week-picker'); const getWeekNumber = (d) => { d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())); d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7)); const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1)); const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7); return [d.getUTCFullYear(), weekNo]; }; datePicker.value = new Date().toISOString().split('T')[0]; const [year, weekNo] = getWeekNumber(new Date()); weekPicker.value = `${year}-W${String(weekNo).padStart(2, '0')}`; periodSelect.addEventListener('change', () => { datePicker.style.display = (periodSelect.value === 'week') ? 'none' : 'block'; weekPicker.style.display = (periodSelect.value === 'week') ? 'block' : 'none'; }); document.getElementById('btn-fetch-data').addEventListener('click', loadChartData); if (bridgeData.sensors && bridgeData.sensors.length > 0) { loadChartData(); } };
    const loadChartData = async () => { const sensorId = document.getElementById('analyse-sensor').value; const period = document.getElementById('analyse-period').value; let date; if (period === 'week') { const [year, weekNum] = document.getElementById('analyse-week-picker').value.split('-W'); const d = new Date(year, 0, 1 + (weekNum - 1) * 7); d.setDate(d.getDate() - (d.getDay() + 6) % 7); date = d.toISOString().split('T')[0]; } else { date = document.getElementById('analyse-date-picker').value; } if (!sensorId || !date) return; try { const data = await api.loadChartData(sensorId, period, date); chartInstance = ui.renderChart(chartInstance, data, period, date); } catch (error) { ui.showToast(error.message, true); } };
    const loadHelp = async () => { const helpContainer = document.getElementById('help-content-container'); try { const content = await api.loadHelpContent(); helpContainer.innerHTML = content; helpContainer.querySelectorAll('.faq-question').forEach(btn => { btn.addEventListener('click', () => { const answer = btn.nextElementSibling; const icon = btn.querySelector('i'); const isOpening = !answer.style.maxHeight; answer.style.maxHeight = isOpening ? answer.scrollHeight + "px" : null; icon.style.transform = isOpening ? 'rotate(180deg)' : 'rotate(0deg)'; }); }); } catch(e) { helpContainer.innerHTML = `<p class="text-red-500">Hilfe konnte nicht geladen werden.</p>`; } };
    const loadSettings = () => { const settings = config.global_settings || {}; const location = config.location || {}; document.getElementById('setting-bridge-ip').value = config.bridge_ip || ''; document.getElementById('setting-latitude').value = location.latitude || ''; document.getElementById('setting-longitude').value = location.longitude || ''; document.getElementById('setting-hysteresis').value = settings.hysteresis_percent || 25; document.getElementById('setting-datalogger-interval').value = settings.datalogger_interval_minutes || 15; document.getElementById('setting-loglevel').value = settings.log_level || 'INFO'; };

    const saveFullConfig = async () => { const btn = document.getElementById('save-button'); btn.disabled = true; btn.textContent = 'Speichere...'; try { await api.saveFullConfig(config); ui.showToast('Konfiguration gespeichert & neu gestartet!'); } catch (error) { ui.showToast(`Fehler: ${error.message}`, true); } finally { btn.disabled = false; btn.textContent = 'Speichern und Alle Routinen neu starten'; } };
    const saveSettings = async () => { const newConfig = JSON.parse(JSON.stringify(config)); newConfig.bridge_ip = document.getElementById('setting-bridge-ip').value; newConfig.location = { latitude: parseFloat(document.getElementById('setting-latitude').value), longitude: parseFloat(document.getElementById('setting-longitude').value) }; newConfig.global_settings = { hysteresis_percent: parseInt(document.getElementById('setting-hysteresis').value), datalogger_interval_minutes: parseInt(document.getElementById('setting-datalogger-interval').value), log_level: document.getElementById('setting-loglevel').value }; try { await api.saveFullConfig(newConfig); config = newConfig; ui.showToast("Einstellungen gespeichert."); } catch(e) { ui.showToast(`Fehler: ${e.message}`, true); } };
    const handleSaveScene = () => { const form = document.getElementById('form-scene'); const originalName = form.querySelector('#scene-original-name').value; const newName = form.querySelector('#scene-name').value.trim().replace(/\s+/g, '_').toLowerCase(); if (!newName) return ui.showToast("Name fehlt.", true); const newScene = { status: form.querySelector('#scene-status').checked, bri: parseInt(form.querySelector('#scene-bri').value) }; if (form.querySelector('input[name="color-mode"]:checked').value === 'color' && colorPicker) { const hsv = colorPicker.color.hsv; newScene.hue = Math.round(hsv.h / 360 * 65535); newScene.sat = Math.round(hsv.s / 100 * 254); } else { newScene.ct = parseInt(form.querySelector('#scene-ct').value); } if (originalName && originalName !== newName) delete config.scenes[originalName]; config.scenes[newName] = newScene; renderAll(); ui.closeModal(); };
    const handleCreateNewRoutine = () => { const name = document.getElementById('new-routine-name').value; const [groupId, groupName] = document.getElementById('new-routine-group').value.split('|'); const sensorId = document.getElementById('new-routine-sensor').value; if (!name || !groupId) return ui.showToast("Name oder Raum fehlt.", true); const newRoutine = { name, room_name: groupName, enabled: true, daily_time: { H1: 7, M1: 0, H2: 23, M2: 0 }, ...Object.fromEntries(['morning', 'day', 'evening', 'night'].map(p => [p, { scene_name: "off", x_scene_name: "off" }])) }; if(!config.routines) config.routines = []; config.routines.push(newRoutine); if(!config.rooms) config.rooms = []; if (!config.rooms.some(r => r.name === groupName)) { config.rooms.push({ name: groupName, group_ids: [parseInt(groupId)], sensor_id: sensorId ? parseInt(sensorId) : undefined }); } renderAll(); ui.closeModal(); ui.openEditRoutineModal(newRoutine, config.routines.length - 1, Object.keys(config.scenes)); };
    
    const handleSaveEditedRoutine = () => {
        const modal = document.getElementById('modal-routine');
        if (!modal) return;
        const index = modal.querySelector('#routine-index').value;
        const routine = config.routines[index];
        if (!routine) return;
        const startMinutes = parseInt(modal.querySelector('#time-slider-start').value);
        const endMinutes = parseInt(modal.querySelector('#time-slider-end').value);
        routine.daily_time = {
            H1: Math.floor(startMinutes / 60), M1: startMinutes % 60,
            H2: Math.floor(endMinutes / 60), M2: endMinutes % 60
        };
        modal.querySelectorAll('[data-section-name]').forEach(el => {
            const name = el.dataset.sectionName;
            routine[name] = {
                scene_name: el.querySelector('.section-scene-name').value,
                x_scene_name: el.querySelector('.section-x-scene-name').value,
                motion_check: el.querySelector('.section-motion-check').checked,
                wait_time: { min: parseInt(el.querySelector('.section-wait-time-min').value) || 0, sec: parseInt(el.querySelector('.section-wait-time-sec').value) || 0 },
                do_not_disturb: el.querySelector('.section-do-not-disturb').checked,
                bri_check: el.querySelector('.section-bri-check').checked,
                max_light_level: parseInt(el.querySelector('.brightness-slider').value),
            };
        });
        renderAll();
        ui.closeModal();
        ui.showToast("Routine aktualisiert. Globale Speicherung nicht vergessen!");
    };

    init();
}