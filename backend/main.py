"""
main.py
-------
Standalone runnable entrypoint for Smriti (স্মৃতি) — AI Cognitive Care & Memory Assistance Platform.
Serves full interactive visual web interface directly at http://localhost:8000/
and FastAPI docs at http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from backend.app.routers.analysis import router
from backend.app.services.seed_demo_data import seed
from backend.app.services.voice_assistant import process_voice_query, get_screen_voice_guidance

app = FastAPI(title="Smriti (স্মৃতি) — AI Cognitive Care & Memory Assistance Platform")

# Enable CORS for Caregiver Dashboard & Mobile App clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


class VoiceQueryRequest(BaseModel):
    patient_id: str = Field("demo-patient-01", description="Patient profile ID")
    spoken_phrase: str = Field("How am I doing today?", description="Spoken text query")


@app.post("/voice/intent", tags=["voice"])
def voice_intent_alias(payload: VoiceQueryRequest):
    return process_voice_query(payload.patient_id, payload.spoken_phrase)


@app.on_event("startup")
def startup_seed():
    seed(num_patients=12, sessions_per_patient=10)
    print("Smriti Demo data seeded: demo-patient-01 through demo-patient-12")


INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smriti (স্মৃতি) — Cognitive Care & Memory Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #FAF8F5; }
        .active-tab { background-color: #064E3B; color: white; }
        .inactive-tab { background-color: #E5E7EB; color: #374151; }
        .game-card:hover { transform: translateY(-4px); transition: all 0.2s ease-in-out; }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between text-gray-800">

    <!-- Top Header -->
    <header class="bg-white shadow-sm border-b border-emerald-100 px-6 py-4 flex flex-wrap justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-emerald-700 text-white rounded-xl flex items-center justify-center font-bold text-xl shadow">
                🧠
            </div>
            <div>
                <h1 class="text-xl font-bold text-emerald-950">Smriti (স্মৃতি)</h1>
                <p class="text-xs text-emerald-700 font-medium">CogniCare NE • SIH 2026 • PS 26003</p>
            </div>
        </div>

        <div class="flex items-center space-x-4 mt-2 sm:mt-0">
            <!-- Language Selector -->
            <select id="langSelect" onchange="changeLanguage()" class="bg-emerald-50 border border-emerald-200 text-emerald-900 text-sm rounded-lg p-2 font-semibold">
                <option value="en">🇬🇧 English</option>
                <option value="hi">🇮🇳 हिन्दी (Hindi)</option>
                <option value="as">🌾 অসমীয়া (Assamese)</option>
                <option value="mzo">🏔️ Mizo ṭawng</option>
                <option value="kha">🌲 Ka Ktien Khasi</option>
            </select>

            <!-- Mode Selector -->
            <div class="flex rounded-lg bg-gray-100 p-1">
                <button id="patientModeBtn" onclick="switchMode('patient')" class="px-4 py-1.5 rounded-md text-sm font-bold active-tab transition">
                    👤 Patient
                </button>
                <button id="caregiverModeBtn" onclick="switchMode('caregiver')" class="px-4 py-1.5 rounded-md text-sm font-bold inactive-tab transition">
                    🩺 Caregiver
                </button>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-6xl mx-auto px-4 py-6 flex-grow w-full">

        <!-- Voice Guidance Banner -->
        <div class="bg-gradient-to-r from-emerald-800 to-teal-900 text-white p-4 rounded-2xl shadow-md mb-6 flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-2xl">
                    🗣️
                </div>
                <div>
                    <p class="text-xs uppercase tracking-wider font-semibold text-emerald-200" id="guidanceTitle">Step-by-Step Voice Guidance</p>
                    <p class="text-sm md:text-base font-medium text-white" id="guidanceText">Welcome to Smriti! Choose your favorite game to begin your daily practice.</p>
                </div>
            </div>
            <button onclick="speakGuidance()" class="bg-emerald-400 hover:bg-emerald-300 text-emerald-950 font-bold px-4 py-2 rounded-xl text-sm transition flex items-center space-x-2">
                <i class="fas fa-volume-up"></i>
                <span>Listen</span>
            </button>
        </div>

        <!-- PATIENT VIEW -->
        <div id="patientView">
            
            <!-- Difficulty Selector -->
            <div class="flex items-center justify-between mb-6 bg-white p-4 rounded-xl shadow-sm border border-emerald-50">
                <span class="font-bold text-gray-700 text-sm flex items-center space-x-2">
                    <i class="fas fa-[#064E3B] fa-gauge-high text-emerald-700"></i>
                    <span>Select Difficulty Level:</span>
                </span>
                <div class="flex space-x-2">
                    <button onclick="setDifficulty('easy')" id="btn-easy" class="px-4 py-1.5 text-xs font-bold rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-300">Easy</button>
                    <button onclick="setDifficulty('medium')" id="btn-medium" class="px-4 py-1.5 text-xs font-bold rounded-lg bg-emerald-700 text-white border border-emerald-700 shadow">Medium</button>
                    <button onclick="setDifficulty('hard')" id="btn-hard" class="px-4 py-1.5 text-xs font-bold rounded-lg bg-gray-100 text-gray-700 border border-gray-200">Hard</button>
                </div>
            </div>

            <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center space-x-2">
                <span>🎮 Play Memory & Cognitive Games</span>
            </h2>

            <!-- Game Cards Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                <!-- Game 1: Memory Match -->
                <div class="game-card bg-white p-6 rounded-2xl shadow-sm border border-emerald-100 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="w-12 h-12 bg-pink-50 text-pink-600 rounded-xl flex items-center justify-center text-2xl font-bold">🌸</span>
                            <span class="text-xs bg-emerald-50 text-emerald-800 font-bold px-2.5 py-1 rounded-full border border-emerald-200">Visual Paired Memory</span>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900">Memory Match</h3>
                        <p class="text-xs text-gray-500 mt-1">Match pairs of Assam flowers, tea leaves, and family faces</p>
                    </div>
                    <button onclick="playGame('memory_match', 'Memory Match')" class="mt-5 w-full bg-emerald-700 hover:bg-emerald-800 text-white font-bold py-2.5 rounded-xl text-sm transition">
                        Play Game <i class="fas fa-arrow-right ml-1"></i>
                    </button>
                </div>

                <!-- Game 2: Number Sequence -->
                <div class="game-card bg-white p-6 rounded-2xl shadow-sm border border-emerald-100 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-2xl font-bold">🔢</span>
                            <span class="text-xs bg-blue-50 text-blue-800 font-bold px-2.5 py-1 rounded-full border border-blue-200">Auditory Sequential</span>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900">Number Sequence</h3>
                        <p class="text-xs text-gray-500 mt-1">Repeat the numbers spoken to you in correct order</p>
                    </div>
                    <button onclick="playGame('number_sequence', 'Number Sequence')" class="mt-5 w-full bg-emerald-700 hover:bg-emerald-800 text-white font-bold py-2.5 rounded-xl text-sm transition">
                        Play Game <i class="fas fa-arrow-right ml-1"></i>
                    </button>
                </div>

                <!-- Game 3: Word Recall -->
                <div class="game-card bg-white p-6 rounded-2xl shadow-sm border border-emerald-100 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="w-12 h-12 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center text-2xl font-bold">📖</span>
                            <span class="text-xs bg-amber-50 text-amber-800 font-bold px-2.5 py-1 rounded-full border border-amber-200">Semantic Heritage</span>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900">Word Recall</h3>
                        <p class="text-xs text-gray-500 mt-1">Remember words from local cultural traditions</p>
                    </div>
                    <button onclick="playGame('word_recall', 'Word Recall')" class="mt-5 w-full bg-emerald-700 hover:bg-emerald-800 text-white font-bold py-2.5 rounded-xl text-sm transition">
                        Play Game <i class="fas fa-arrow-right ml-1"></i>
                    </button>
                </div>

                <!-- Game 4: Picture Association -->
                <div class="game-card bg-white p-6 rounded-2xl shadow-sm border border-emerald-100 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center text-2xl font-bold">🖼️</span>
                            <span class="text-xs bg-purple-50 text-purple-800 font-bold px-2.5 py-1 rounded-full border border-purple-200">Visual Semantic</span>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900">Picture Association</h3>
                        <p class="text-xs text-gray-500 mt-1">Match traditional pictures with their meanings</p>
                    </div>
                    <button onclick="playGame('picture_association', 'Picture Association')" class="mt-5 w-full bg-emerald-700 hover:bg-emerald-800 text-white font-bold py-2.5 rounded-xl text-sm transition">
                        Play Game <i class="fas fa-arrow-right ml-1"></i>
                    </button>
                </div>

            </div>
        </div>

        <!-- CAREGIVER VIEW -->
        <div id="caregiverView" class="hidden">
            <h2 class="text-lg font-bold text-gray-800 mb-4">🩺 Caregiver Monitoring Dashboard (demo-patient-12)</h2>
            
            <!-- Anomaly Alert Card -->
            <div id="anomalyAlertCard" class="bg-amber-50 border-l-4 border-amber-500 p-5 rounded-xl mb-6 shadow-sm">
                <div class="flex items-start space-x-3">
                    <div class="text-amber-600 text-xl font-bold">⚠️</div>
                    <div>
                        <h4 class="font-bold text-amber-900 text-sm">Noticeable Change Detected in Activity Patterns</h4>
                        <p id="alertMsgText" class="text-xs text-amber-800 mt-1">Loading caregiver evaluation...</p>
                        <p id="alertRecText" class="text-xs text-amber-900 font-semibold mt-2">Action Recommendation: Gentle check-in suggested.</p>
                    </div>
                </div>
            </div>

            <!-- Monitoring Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6" id="monitoringGrid">
                <!-- Dynamically loaded breakdown cards -->
            </div>
        </div>

    </main>

    <!-- Footer API Docs Link -->
    <footer class="bg-white border-t border-gray-200 px-6 py-3 text-center text-xs text-gray-500">
        Smriti AI Backend Running • <a href="/docs" target="_blank" class="text-emerald-700 font-bold underline hover:text-emerald-900">View OpenAPI Docs (/docs)</a>
    </footer>

    <!-- Interactive Game Modal -->
    <div id="gameModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 hidden z-50">
        <div class="bg-white rounded-2xl max-w-md w-full p-6 text-center shadow-2xl relative">
            <button onclick="closeModal()" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 font-bold text-xl">&times;</button>
            <div class="text-4xl mb-2" id="modalIcon">🎮</div>
            <h3 class="text-xl font-bold text-gray-900" id="modalTitle">Playing Game</h3>
            <p class="text-xs text-gray-500 mt-1" id="modalSub">Recording Cognitive Metrics...</p>
            
            <div class="my-6 bg-emerald-50 p-4 rounded-xl border border-emerald-100">
                <p class="text-sm font-semibold text-emerald-900" id="modalAction">Action: Tap matching pair</p>
                <div class="mt-4 flex justify-center space-x-4 text-3xl cursor-pointer">
                    <span onclick="recordScore(95)" class="hover:scale-125 transition">🌸</span>
                    <span onclick="recordScore(90)" class="hover:scale-125 transition">🌿</span>
                    <span onclick="recordScore(85)" class="hover:scale-125 transition">👵</span>
                </div>
            </div>

            <div id="resultBox" class="hidden bg-white p-3 rounded-lg border border-gray-200">
                <p class="text-xs text-gray-500">Calculated Cognitive Score (CPS):</p>
                <p class="text-2xl font-extrabold text-emerald-700" id="resCPS">88.5</p>
                <p class="text-xs font-bold text-emerald-900" id="resLabel">Steady Practice</p>
            </div>
        </div>
    </div>

    <script>
        let currentLang = 'en';
        let currentDifficulty = 'medium';

        function setDifficulty(diff) {
            currentDifficulty = diff;
            ['easy', 'medium', 'hard'].forEach(d => {
                const btn = document.getElementById('btn-' + d);
                if (d === diff) {
                    btn.className = "px-4 py-1.5 text-xs font-bold rounded-lg bg-emerald-700 text-white border border-emerald-700 shadow";
                } else {
                    btn.className = "px-4 py-1.5 text-xs font-bold rounded-lg bg-gray-100 text-gray-700 border border-gray-200";
                }
            });
            fetchGuidance('difficulty_selection');
        }

        function switchMode(mode) {
            const pBtn = document.getElementById('patientModeBtn');
            const cBtn = document.getElementById('caregiverModeBtn');
            const pView = document.getElementById('patientView');
            const cView = document.getElementById('caregiverView');

            if (mode === 'patient') {
                pBtn.className = "px-4 py-1.5 rounded-md text-sm font-bold active-tab transition";
                cBtn.className = "px-4 py-1.5 rounded-md text-sm font-bold inactive-tab transition";
                pView.classList.remove('hidden');
                cView.classList.add('hidden');
                fetchGuidance('home');
            } else {
                cBtn.className = "px-4 py-1.5 rounded-md text-sm font-bold active-tab transition";
                pBtn.className = "px-4 py-1.5 rounded-md text-sm font-bold inactive-tab transition";
                cView.classList.remove('hidden');
                pView.classList.add('hidden');
                loadCaregiverData();
                fetchGuidance('caregiver_dashboard');
            }
        }

        async function fetchGuidance(screenId) {
            try {
                const res = await fetch(`/analysis/voice-guidance/${screenId}?lang=${currentLang}`);
                const data = await res.json();
                document.getElementById('guidanceText').innerText = data.spoken_guidance;
            } catch (e) {}
        }

        function changeLanguage() {
            currentLang = document.getElementById('langSelect').value;
            fetchGuidance('home');
        }

        function speakGuidance() {
            const text = document.getElementById('guidanceText').innerText;
            const utter = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.speak(utter);
        }

        function playGame(gameKey, title) {
            document.getElementById('modalTitle').innerText = title;
            document.getElementById('modalSub').innerText = `Difficulty: ${currentDifficulty.toUpperCase()}`;
            document.getElementById('resultBox').classList.add('hidden');
            document.getElementById('gameModal').classList.remove('hidden');
            fetchGuidance(gameKey);
        }

        function closeModal() {
            document.getElementById('gameModal').classList.add('hidden');
        }

        async function recordScore(acc) {
            try {
                const res = await fetch('/analysis/cps', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        patient_id: 'demo-patient-01',
                        game_type: 'memory_match',
                        difficulty: currentDifficulty,
                        accuracy: acc,
                        response_time: 2.2,
                        completion_rate: 100
                    })
                });
                const data = await res.json();
                document.getElementById('resCPS').innerText = data.cps_score;
                document.getElementById('resLabel').innerText = data.display_label;
                document.getElementById('resultBox').classList.remove('hidden');
            } catch (e) {}
        }

        async function loadCaregiverData() {
            try {
                const res = await fetch('/analysis/monitoring/demo-patient-12');
                const data = await res.json();
                document.getElementById('alertMsgText').innerText = data.anomaly_status.alert_message;
                document.getElementById('alertRecText').innerText = data.anomaly_status.caregiver_action_recommendation;

                const grid = document.getElementById('monitoringGrid');
                grid.innerHTML = '';
                const bd = data.monitoring_breakdown.game_breakdown;
                for (let key in bd) {
                    const item = bd[key];
                    grid.innerHTML += `
                        <div class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm">
                            <div class="flex justify-between items-center mb-2">
                                <h4 class="font-bold text-sm text-gray-900">${item.title}</h4>
                                <span class="text-xs bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">${item.difficulty}</span>
                            </div>
                            <div class="flex justify-between items-end mt-4">
                                <div>
                                    <p class="text-xs text-gray-500">Average CPS Score</p>
                                    <p class="text-xl font-extrabold text-emerald-800">${item.average_cps}</p>
                                </div>
                                <div class="text-right">
                                    <p class="text-xs text-gray-500">Accuracy</p>
                                    <p class="text-sm font-bold text-gray-700">${item.average_accuracy}%</p>
                                </div>
                            </div>
                        </div>
                    `;
                }
            } catch (e) {}
        }

        // Initialize guidance
        fetchGuidance('home');
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def root_ui():
    """Serves the full interactive visual web UI for Smriti (स्मৃতি)."""
    return HTMLResponse(content=INDEX_HTML)
