document.addEventListener('DOMContentLoaded', () => {
    // Globale Zustandsvariablen
    let config = {};
    let bridgeData = { groups: [], sensors: [] };
    let statusInterval;

    // DOM-Elemente referenzieren
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');
    const clockElement = document.getElementById('clock');
    const routinesContainer = document.getElementById('routines-container');
    const toastElement = document.getElementById('toast');
    
    // --- Darkmode Logik (FINAL UND FUNKTIONAL) ---
    const applyTheme = () => {
        // Prüft, ob 'dark' im localStorage ist oder vom System bevorzugt wird
        const isDark = localStorage.theme === 'dark' || 
                       (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
        
        // Setzt oder entfernt die 'dark' Klasse auf dem Haupt-HTML-Element
        document.documentElement.classList.toggle('dark', isDark);

        // Schaltet die Sichtbarkeit der Icons um
        if (sunIcon && moonIcon) {
            sunIcon.classList.toggle('hidden', isDark);
            moonIcon.classList.toggle('hidden', !isDark);
        }
    };

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            const isDarkMode = document.documentElement.classList.contains('dark');
            localStorage.setItem('theme', isDarkMode ? 'light' : 'dark');
            applyTheme();
        });
    }

    // --- Tab-Navigation (FINAL UND FUNKTIONAL) ---
    const tabs = document.querySelectorAll('[data-tab-target]');
    const tabContents = document.querySelectorAll('[data-tab-content]');
    const activeTabClasses = ['border-blue-500', 'text-blue-600', 'dark:text-blue-400'];
    const inactiveTabClasses = ['border-transparent', 'text-gray-500', 'hover:text-gray-700', 'dark:hover:text-gray-300'];

    tabs.forEach((tab, index) => {
        if (index === 0) {
            tab.classList.add(...activeTabClasses);
            tab.classList.remove(...inactiveTabClasses);
        } else {
            tab.classList.add(...inactiveTabClasses);
            tab.classList.remove(...activeTabClasses);
        }

        tab.addEventListener('click', () => {
            const target = document.querySelector(tab.dataset.tabTarget);
            tabs.forEach(t => {
                t.classList.remove(...activeTabClasses);
                t.classList.add(...inactiveTabClasses);
            });
            tabContents.forEach(tc => tc.classList.add('hidden'));

            tab.classList.add(...activeTabClasses);
            tab.classList.remove(...inactiveTabClasses);
            target.classList.remove('hidden');

            if (target.id === 'content-status') {
                startStatusUpdates();
            } else {
                if (statusInterval) clearInterval(statusInterval);
            }
        });
    });
    
    // --- Event Delegation für dynamische Inhalte (Bearbeiten-Knopf) ---
    document.addEventListener('click', (event) => {
        const target = event.target;
        if (target.matches('[data-action="edit-routine"]')) {
            const routineIndex = target.dataset.index;
            openRoutineModal(routineIndex);
        }
        // Hier können später weitere Aktionen wie 'delete-routine' etc. hinzugefügt werden
    });


    // --- Modal-Logik (NEU) ---
    const openRoutineModal = (routineIndex) => {
        const routine = config.routines[routineIndex];
        const modal = document.getElementById('modal-routine');
        if (!modal || !routine) return;

        // Fülle das Modal mit den Daten der Routine
        modal.querySelector('#modal-routine-title').textContent = `Routine bearbeiten: ${routine.name}`;
        // Hier würde man normalerweise die Formularfelder mit den Daten füllen
        
        modal.classList.remove('hidden');
        
        // Schließ-Logik für das Modal
        modal.querySelector('[data-action="close-modal"]').addEventListener('click', () => {
            modal.classList.add('hidden');
        });
    };


    // --- Initialisierung ---
    const init = async () => {
        applyTheme();
        updateClock();
        setInterval(updateClock, 1000);
        
        showLoading('Lade Konfiguration...');
        try {
            const res = await fetch('/api/config');
            if (!res.ok) throw new Error('Konfiguration konnte nicht geladen werden.');
            config = await res.json();
            renderAll();
        } catch (error) {
            console.error("Initialisierungsfehler:", error);
            showToast("Fehler beim Laden der Konfiguration.", true);
        } finally {
            hideLoading();
        }
    };

    // --- Rendering Funktionen ---
    const renderAll = () => {
        renderRoutines();
    };

    const renderRoutines = () => {
        if (!routinesContainer) return;
        routinesContainer.innerHTML = '';
        if (!config.routines || !config.routines.length) {
            routinesContainer.innerHTML = `<p class="text-gray-500 text-center py-4">Keine Routinen erstellt.</p>`;
            return;
        }
        config.routines.forEach((routine, index) => {
            const routineEl = document.createElement('div');
            routineEl.className = 'bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700';
            
            const icons = { morning: '🌅', day: '☀️', evening: '🌄', night: '🌕' };
            const sections = ['morning', 'day', 'evening', 'night'];
            const sectionsHtml = sections.map(name => {
                const section = routine[name];
                if (!section) return '';
                const waitTime = section.wait_time || {min: 0, sec: 0};
                const waitTimeString = `${waitTime.min || 0}m ${waitTime.sec || 0}s`;

                return `
                <div class="p-2 my-1 bg-gray-100 dark:bg-gray-700 rounded-md">
                    <p class="font-semibold capitalize flex items-center">${icons[name] || ''} <span class="ml-2">${name}</span></p>
                    <div class="text-sm text-gray-600 dark:text-gray-300 grid grid-cols-2 gap-x-4">
                        <span><strong class="font-medium">Szene:</strong> ${section.scene_name}</span>
                        <span><strong class="font-medium">Bewegung:</strong> ${section.motion_check ? `Ja (${waitTimeString})` : 'Nein'}</span>
                    </div>
                </div>`;
            }).join('');
            
            const dailyTime = routine.daily_time || {H1:0,M1:0,H2:23,M2:59};
            const isEnabled = routine.enabled !== false;

            routineEl.innerHTML = `
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-2xl font-semibold">${routine.name}</h3>
                        <div class="flex items-center text-gray-500 dark:text-gray-400 text-sm">
                            <span>Raum: ${routine.room_name}</span>
                            <span class="mx-2">|</span>
                            <span>Aktiv: ${String(dailyTime.H1).padStart(2,'0')}:${String(dailyTime.M1).padStart(2,'0')} - ${String(dailyTime.H2).padStart(2,'0')}:${String(dailyTime.M2).padStart(2,'0')}</span>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <button type="button" data-action="edit-routine" data-index="${index}" class="text-blue-500 hover:text-blue-700 font-semibold">Bearbeiten</button>
                        <button type="button" data-action="delete-routine" data-index="${index}" class="text-red-500 hover:text-red-700 font-semibold">Löschen</button>
                    </div>
                </div>
                <div class="space-y-2">
                    <h4 class="text-lg font-medium border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">Ablauf</h4>
                    <div class="space-y-2">${sectionsHtml}</div>
                </div>`;
            routinesContainer.appendChild(routineEl);
        });
    };
    
    // --- Hilfsfunktionen ---
    const updateClock = () => {
        if (clockElement) clockElement.textContent = new Date().toLocaleTimeString('de-DE');
    };
    
    const showToast = (message, isError = false) => {
        if (!toastElement) return;
        toastElement.textContent = message;
        toastElement.className = `fixed bottom-5 right-5 text-white py-2 px-4 rounded-lg shadow-xl ${isError ? 'bg-red-600' : 'bg-gray-800'}`;
        toastElement.classList.remove('hidden');
        setTimeout(() => toastElement.classList.add('hidden'), 4000);
    };
    
    const showLoading = (message) => {
        if (routinesContainer) routinesContainer.innerHTML = `<p class="text-gray-500 text-center py-8">${message}</p>`;
    };
    const hideLoading = () => {
        // Wird von renderRoutines überschrieben
    };

    const startStatusUpdates = () => { /* Platzhalter */ };

    // App starten
    init();
});
