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
            // Prüft, ob der Darkmode gerade aktiv ist
            const isDarkMode = document.documentElement.classList.contains('dark');
            // Speichert den *entgegengesetzten* Wert im localStorage
            localStorage.setItem('theme', isDarkMode ? 'light' : 'dark');
            // Wendet das neue Theme an
            applyTheme();
        });
    }

    // --- Tab-Navigation (FINAL UND FUNKTIONAL) ---
    const tabs = document.querySelectorAll('[data-tab-target]');
    const tabContents = document.querySelectorAll('[data-tab-content]');
    const activeTabClasses = ['border-blue-500', 'text-blue-600', 'dark:text-blue-400'];
    const inactiveTabClasses = ['border-transparent', 'text-gray-500', 'hover:text-gray-700', 'dark:hover:text-gray-300'];

    tabs.forEach((tab, index) => {
        // Setze den ersten Tab standardmäßig als aktiv
        if (index === 0) {
            tab.classList.add(...activeTabClasses);
            tab.classList.remove(...inactiveTabClasses);
        } else {
            tab.classList.add(...inactiveTabClasses);
            tab.classList.remove(...activeTabClasses);
        }

        tab.addEventListener('click', () => {
            const target = document.querySelector(tab.dataset.tabTarget);

            // Deaktiviere alle
            tabs.forEach(t => {
                t.classList.remove(...activeTabClasses);
                t.classList.add(...inactiveTabClasses);
            });
            tabContents.forEach(tc => tc.classList.add('hidden'));

            // Aktiviere den geklickten Tab und Inhalt
            tab.classList.add(...activeTabClasses);
            tab.classList.remove(...inactiveTabClasses);
            target.classList.remove('hidden');

            // Spezifische Logik für den Status-Tab
            if (target.id === 'content-status') {
                startStatusUpdates();
            } else {
                if (statusInterval) clearInterval(statusInterval);
            }
        });
    });

    // --- Initialisierung ---
    const init = async () => {
        applyTheme(); // Theme sofort anwenden
        updateClock();
        setInterval(updateClock, 1000);
        
        showLoading('Lade Konfiguration und Bridge-Daten...');
        try {
            // Lade alle notwendigen Daten parallel, um die rote Fehlermeldung zu verhindern
            const [configRes, groupsRes, sensorsRes] = await Promise.all([
                fetch('/api/config'),
                fetch('/api/bridge/groups'),
                fetch('/api/bridge/sensors')
            ]);

            if (!configRes.ok || !groupsRes.ok || !sensorsRes.ok) {
                throw new Error('Netzwerkantwort war nicht ok.');
            }
            
            config = await configRes.json();
            bridgeData.groups = await groupsRes.json();
            bridgeData.sensors = await sensorsRes.json();
            
            renderAll();
            
        } catch (error) {
            console.error("Initialisierungsfehler:", error);
            showToast("Fehler beim Laden der Daten. Läuft der Server?", true);
        } finally {
            hideLoading();
        }
    };

    // --- Rendering Funktionen ---
    const renderAll = () => {
        renderRoutines();
        // Hier können später renderScenes() etc. aufgerufen werden
    };

    const renderRoutines = () => {
        if (!routinesContainer) return;
        routinesContainer.innerHTML = '';
        if (!config.routines || config.routines.length === 0) {
            routinesContainer.innerHTML = `<p class="text-gray-500 text-center py-4">Keine Routinen erstellt.</p>`;
            return;
        }
        config.routines.forEach((routine) => {
            const routineEl = document.createElement('div');
            routineEl.className = 'bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700';
            // (Der Code zum Rendern der einzelnen Routinen bleibt hier unverändert)
            // Du kannst den Code aus deiner funktionierenden Version hier einfügen.
            const icons = {
                morning: '🌅',
                day: '☀️',
                evening: '🌄',
                night: '🌕'
            };
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
                            <input type="checkbox" data-action="toggle-routine" data-index="${routine.name}" class="sr-only peer" ${isEnabled ? 'checked' : ''}>
                            <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-2 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                        <button type="button" data-action="edit-routine" data-index="${routine.name}" class="text-blue-500 hover:text-blue-700 font-semibold">Bearbeiten</button>
                        <button type="button" data-action="delete-routine" data-index="${routine.name}" class="text-red-500 hover:text-red-700 font-semibold">Löschen</button>
                    </div>
                </div>
                <div class="space-y-2">
                    <h4 class="text-lg font-medium border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">Ablauf</h4>
                    <div class="space-y-3">${sectionsHtml}</div>
                </div>
            `;
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

    const startStatusUpdates = () => {
        // Platzhalter für die Status-Update-Logik
    };

    // App starten
    init();
});
