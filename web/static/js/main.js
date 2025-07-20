import * as api from './modules/api.js';
import * as ui from './modules/ui.js';
import { runSetupWizard } from './modules/setup.js';

function runMainApp() {
    let config = {};
    let bridgeData = { groups: [], sensors: [] };
    let statusInterval;
    let colorPicker = null;
    let chartInstance = null;

    // DOM-Elemente holen (einmalig, um wiederholte Aufrufe zu vermeiden)
    const routinesContainer = document.getElementById('routines-container');
    const scenesContainer = document.getElementById('scenes-container');
    const saveButton = document.getElementById('save-button');
    const refreshButton = document.getElementById('btn-refresh-status');

    const init = async () => {
        ui.updateClock();
        setInterval(ui.updateClock, 1000);
        
        routinesContainer.innerHTML = `<p class="text-gray-500 text-center">Lade Konfiguration...</p>`;
        
        try {
            config = await api.loadConfig();
            bridgeData = await api.loadBridgeData();
            
            ui.renderRoutines(config.routines);
            ui.renderScenes(config.scenes);
            setupEventListeners();
        } catch (error) {
            console.error("Initialisierungsfehler:", error);
            ui.showToast(`Fehler beim Initialisieren: ${error.message}`, true);
            routinesContainer.innerHTML = `<p class="text-red-500 text-center font-semibold">${error.message}</p>`;
        }
    };

    const setupEventListeners = () => {
        saveButton.addEventListener('click', saveFullConfig);

        const tabs = [
            { btn: 'tab-routines', content: 'content-routines' },
            { btn: 'tab-scenes', content: 'content-scenes' },
            { btn: 'tab-status', content: 'content-status', init: startStatusUpdates },
            { btn: 'tab-analyse', content: 'content-analyse', init: setupAnalyseTab },
            { btn: 'tab-einstellungen', content: 'content-einstellungen', init: loadSettings },
            { btn: 'tab-hilfe', content: 'content-hilfe', init: loadHelp }
        ];
        tabs.forEach(tabInfo => {
            const btn = document.getElementById(tabInfo.btn);
            if (btn) {
                btn.addEventListener('click', () => {
                    tabs.forEach(t => {
                        document.getElementById(t.btn).classList.remove('tab-active');
                        document.getElementById(t.content).classList.add('hidden');
                    });
                    btn.classList.add('tab-active');
                    document.getElementById(tabInfo.content).classList.remove('hidden');

                    if (statusInterval) clearInterval(statusInterval);
                    if (tabInfo.init) tabInfo.init();
                });
            }
        });

        document.getElementById('btn-new-routine').addEventListener('click', () => openCreateRoutineModal());
        document.getElementById('btn-new-scene').addEventListener('click', () => openSceneModal());
        refreshButton.addEventListener('click', updateStatus);

        // Event Listener für dynamisch erstellte Elemente (Modals, etc.)
        document.body.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (!action) return;

            const routineIndex = e.target.closest('[data-index]')?.dataset.index;
            const sceneName = e.target.dataset.name;

            switch (action) {
                case 'toggle-routine':
                    config.routines[routineIndex].enabled = e.target.checked;
                    ui.showToast(`Routine '${config.routines[routineIndex].name}' ${e.target.checked ? 'aktiviert' : 'deaktiviert'}.`);
                    break;
                case 'delete-scene':
                    if (confirm(`Möchtest du die Szene "${sceneName}" wirklich löschen?`)) {
                        delete config.scenes[sceneName];
                        renderAll();
                        ui.showToast("Szene gelöscht.");
                    }
                    break;
                case 'delete-routine':
                    if (confirm(`Möchtest du die Routine "${config.routines[routineIndex].name}" wirklich löschen?`)) {
                        config.routines.splice(routineIndex, 1);
                        renderAll();
                        ui.showToast("Routine gelöscht.");
                    }
                    break;
                case 'edit-scene': openSceneModal(sceneName); break;
                case 'edit-routine': openEditRoutineModal(routineIndex); break;
                case 'save-scene': handleSaveScene(); break;
                case 'save-routine': handleSaveEditedRoutine(); break;
                case 'create-routine': handleCreateNewRoutine(); break;
                case 'cancel-modal': closeModal(); break;
            }
        });
    };
    
    const saveFullConfig = async () => {
        saveButton.disabled = true;
        saveButton.textContent = 'Speichere...';
        try {
            const result = await api.saveFullConfig(config);
            ui.showToast(result.message);
        } catch (error) {
            ui.showToast(`Fehler: ${error.message}`, true);
        } finally {
            saveButton.disabled = false;
            saveButton.textContent = 'Speichern und Alle Routinen neu starten';
        }
    };

    const updateStatus = async () => {
        try {
            const { statusData, logText } = await api.updateStatus();
            ui.renderStatus(statusData.routines || [], config);
            ui.renderSunTimes(statusData.sun_times || null);
            ui.renderLog(logText);
        } catch (error) {
            console.error("Fehler beim Abrufen des Status:", error);
        }
    };

    const startStatusUpdates = () => {
        if (statusInterval) clearInterval(statusInterval);
        updateStatus();
        statusInterval = setInterval(updateStatus, 5000);
    };

    const loadHelp = async () => {
        try {
            const content = await api.loadHelpContent();
            const helpContainer = document.getElementById('help-content-container');
            helpContainer.innerHTML = content;
            helpContainer.querySelectorAll('.faq-question').forEach(button => {
                button.addEventListener('click', () => {
                    const answer = button.nextElementSibling;
                    const icon = button.querySelector('i');
                    if (answer.style.maxHeight) {
                        answer.style.maxHeight = null;
                        icon.style.transform = 'rotate(0deg)';
                    } else {
                        answer.style.maxHeight = answer.scrollHeight + "px";
                        icon.style.transform = 'rotate(180deg)';
                    }
                });
            });
        } catch (error) {
            ui.showToast(error.message, true);
        }
    };
    
    const openCreateRoutineModal = () => { /* ... Implement logic ... */ };
    const setupAnalyseTab = () => { /* ... Implement logic ... */ };
    const loadSettings = () => { /* ... Implement logic ... */ };
    const openSceneModal = () => { /* ... Implement logic ... */ };
    const openEditRoutineModal = () => { /* ... Implement logic ... */ };
    const handleSaveScene = () => { /* ... Implement logic ... */ };
    const handleSaveEditedRoutine = () => { /* ... Implement logic ... */ };
    const handleCreateNewRoutine = () => { /* ... Implement logic ... */ };
    const closeModal = () => { /* ... Implement logic ... */ };
    const renderAll = () => {
        ui.renderRoutines(config.routines);
        ui.renderScenes(config.scenes);
    };


    init();
}

// --- Initial check on page load ---
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const status = await api.checkSetupStatus();
        if (status.setup_needed) {
            document.getElementById('setup-wizard').classList.remove('hidden');
            document.getElementById('setup-wizard').classList.add('flex');
            document.getElementById('main-app').classList.add('hidden');
            runSetupWizard();
        } else {
            document.getElementById('setup-wizard').classList.add('hidden');
            document.getElementById('main-app').classList.remove('hidden');
            runMainApp();
        }
    } catch (error) {
        document.body.innerHTML = `<div class="text-red-500 text-center p-8">Fehler bei der Verbindung zum Server. Läuft das Python-Skript?</div>`;
        console.error(error);
    }
});
