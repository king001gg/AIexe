import streamlit as st

from config.settings import AppSettings

CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --primary: #6366f1;
    --primary-light: #818cf8;
    --primary-dark: #4f46e5;
    --violet: #8b5cf6;
    --violet-light: #a78bfa;
    --accent: #06b6d4;
    --accent-light: #22d3ee;
    --bg-deep: #050814;
    --bg-mid: #0a0e1a;
    --bg-surface: #0f172a;
    --glass: rgba(15, 23, 42, 0.55);
    --glass-strong: rgba(15, 23, 42, 0.75);
    --glass-border: rgba(148, 163, 184, 0.12);
    --glass-border-bright: rgba(129, 140, 248, 0.35);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --gradient-1: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
    --gradient-2: linear-gradient(135deg, #4f46e5, #6366f1, #22d3ee);
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.3);
    --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.18);
    --radius-sm: 8px;
    --radius-md: 12px;
}

/* ===== 背景：量子极光 + 网格 ===== */
.stApp {
    background: radial-gradient(ellipse 80% 60% at 15% -10%, rgba(99, 102, 241, 0.14), transparent 60%),
                radial-gradient(ellipse 60% 50% at 100% 10%, rgba(34, 211, 238, 0.10), transparent 55%),
                radial-gradient(ellipse 70% 60% at 50% 110%, rgba(139, 92, 246, 0.12), transparent 60%),
                linear-gradient(160deg, #050814 0%, #0a0e1a 30%, #0f172a 60%, #0c1220 100%) !important;
    color: var(--text-primary) !important;
}

.bg-grid {
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(99, 102, 241, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99, 102, 241, 0.05) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
    -webkit-mask-image: radial-gradient(ellipse at center, black 35%, transparent 78%);
    mask-image: radial-gradient(ellipse at center, black 35%, transparent 78%);
}

.scan-beam {
    position: fixed;
    top: -30%;
    left: 0;
    width: 100%;
    height: 30%;
    background: linear-gradient(180deg, transparent, rgba(99, 102, 241, 0.05), rgba(34, 211, 238, 0.07), transparent);
    pointer-events: none;
    z-index: 0;
    animation: scanDown 11s linear infinite;
}

@keyframes scanDown {
    0% { transform: translateY(0); }
    100% { transform: translateY(480%); }
}

.stApp::after {
    content: '';
    position: fixed;
    top: -30%;
    right: -20%;
    width: 60vw;
    height: 60vw;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.10) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    animation: floatGlow 20s ease-in-out infinite;
}

.stApp::before {
    content: '';
    position: fixed;
    bottom: -20%;
    left: -15%;
    width: 50vw;
    height: 50vw;
    background: radial-gradient(circle, rgba(6, 182, 212, 0.08) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    animation: floatGlow 25s ease-in-out infinite reverse;
}

@keyframes floatGlow {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -20px) scale(1.05); }
    66% { transform: translate(-20px, 15px) scale(0.95); }
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.5px !important;
    font-weight: 600 !important;
}

.stMarkdown, label, .stTextInput label, .stSelectbox label, .stRadio label {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-secondary) !important;
}

header[data-testid="stHeader"] {
    background: rgba(5, 8, 20, 0.85) !important;
    border-bottom: 1px solid var(--glass-border) !important;
    backdrop-filter: blur(12px) saturate(140%);
    -webkit-backdrop-filter: blur(12px) saturate(140%);
}

header[data-testid="stHeader"] button {
    color: var(--text-secondary) !important;
}

header[data-testid="stHeader"] button:hover {
    color: var(--text-primary) !important;
    background: rgba(99, 102, 241, 0.1) !important;
}

header[data-testid="stHeader"] svg {
    fill: var(--text-secondary) !important;
}

footer[data-testid="stFooter"],
.stApp > footer {
    background: rgba(5, 8, 20, 0.85) !important;
    border-top: 1px solid var(--glass-border) !important;
    color: var(--text-muted) !important;
    font-family: 'Inter', sans-serif !important;
}

footer a, .stApp > footer a {
    color: var(--text-muted) !important;
}

footer a:hover, .stApp > footer a:hover {
    color: var(--primary-light) !important;
}

.stApp > footer button,
.stApp > footer svg {
    color: var(--text-muted) !important;
    fill: var(--text-muted) !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10, 14, 26, 0.92) 0%, rgba(5, 8, 20, 0.96) 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
    backdrop-filter: blur(18px) saturate(150%);
    -webkit-backdrop-filter: blur(18px) saturate(150%);
}

section[data-testid="stSidebar"] > div {
    padding-top: 2rem !important;
}

section[data-testid="stSidebar"] .stMarkdown {
    color: var(--text-secondary) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15), var(--shadow-md) !important;
    background: rgba(15, 23, 42, 0.8) !important;
}

.stTextInput > div > div > input::placeholder {
    color: var(--text-muted) !important;
}

.stSelectbox > div > div,
.stSelectbox > div > div > div {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.3s ease !important;
}

.stSelectbox > div > div:hover {
    border-color: rgba(99, 102, 241, 0.3) !important;
}

.stSelectbox svg {
    fill: var(--text-secondary) !important;
}

div[data-baseweb="select"] > div {
    background: var(--glass) !important;
    border-color: var(--glass-border) !important;
}

div[data-baseweb="select"] ul {
    background: var(--bg-surface) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

div[data-baseweb="select"] li {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
}

div[data-baseweb="select"] li:hover {
    background: rgba(99, 102, 241, 0.1) !important;
    color: var(--text-primary) !important;
}

div[data-baseweb="select"] [data-testid="stMarkdownContainer"] {
    color: var(--text-primary) !important;
}

.stRadio > div {
    background: transparent !important;
}

.stRadio > div > label {
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    padding: 0.5rem 1.5rem !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.stButton > button:hover {
    background: rgba(99, 102, 241, 0.12) !important;
    border-color: var(--glass-border-bright) !important;
    color: var(--primary-light) !important;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.15) !important;
}

.stChatInput > div > div > div > textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.stChatInput > div > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12) !important;
}

.stChatInput button {
    background: var(--gradient-2) !important;
    background-size: 200% 200% !important;
    border: none !important;
    color: white !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.3s ease !important;
    animation: gradientShift 5s ease infinite;
}

.stChatInput button:hover {
    opacity: 0.92 !important;
    box-shadow: var(--shadow-glow) !important;
}

[data-testid="stChatMessage"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 16px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: var(--shadow-sm) !important;
    backdrop-filter: blur(14px) saturate(140%);
    -webkit-backdrop-filter: blur(14px) saturate(140%);
}

[data-testid="stChatMessage"]:hover {
    border-color: rgba(99, 102, 241, 0.25) !important;
    box-shadow: var(--shadow-md), 0 0 30px rgba(99, 102, 241, 0.08) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stChatMessage"] .stMarkdown {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    line-height: 1.75 !important;
}

[data-testid="stChatMessage"] p {
    color: var(--text-primary) !important;
}

.streamlit-expanderHeader {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.streamlit-expanderHeader:hover {
    border-color: rgba(99, 102, 241, 0.25) !important;
}

.streamlit-expanderContent {
    background: transparent !important;
}

hr {
    border-color: var(--glass-border) !important;
}

.stSuccess {
    background: rgba(52, 211, 153, 0.10) !important;
    border: 1px solid rgba(52, 211, 153, 0.25) !important;
    border-radius: var(--radius-sm) !important;
    color: #34d399 !important;
    font-family: 'Inter', sans-serif !important;
}

.stWarning {
    background: rgba(251, 191, 36, 0.10) !important;
    border: 1px solid rgba(251, 191, 36, 0.25) !important;
    border-radius: var(--radius-sm) !important;
    color: #fbbf24 !important;
    font-family: 'Inter', sans-serif !important;
}

.stError {
    background: rgba(248, 113, 113, 0.10) !important;
    border: 1px solid rgba(248, 113, 113, 0.25) !important;
    border-radius: var(--radius-sm) !important;
    color: #f87171 !important;
    font-family: 'Inter', sans-serif !important;
}

::-webkit-scrollbar {
    width: 5px !important;
}

::-webkit-scrollbar-track {
    background: transparent !important;
}

::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.25) !important;
    border-radius: 10px !important;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.45) !important;
}

.stTextInput > div > div,
.stTextArea > div > div,
.stNumberInput > div > div > div,
.stDateInput > div > div > div,
.stTimeInput > div > div > div,
.stMultiselect > div > div,
.stSlider > div > div > div > div {
    background: var(--glass) !important;
    border-color: var(--glass-border) !important;
}

input[type="text"],
input[type="password"],
input[type="number"],
input[type="email"],
input[type="tel"],
input[type="url"],
input[type="search"],
textarea,
select {
    background: var(--glass) !important;
    color: var(--text-primary) !important;
    border-color: var(--glass-border) !important;
}

.stRadio > div[role="radiogroup"] {
    background: transparent !important;
}

.stRadio label div[data-testid="stMarkdownContainer"],
.stCheckbox label div[data-testid="stMarkdownContainer"] {
    color: var(--text-secondary) !important;
}

.stCheckbox > div {
    background: transparent !important;
}

code {
    background: rgba(99, 102, 241, 0.12) !important;
    color: var(--accent-light) !important;
    border: 1px solid rgba(99, 102, 241, 0.18) !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85em !important;
    padding: 2px 6px !important;
}

pre {
    background: rgba(15, 23, 42, 0.9) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
}

/* ===== 头部 ===== */
.tech-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;
}

.tech-logo {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    background: var(--gradient-1);
    background-size: 200% 200%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    box-shadow: var(--shadow-glow);
    animation: logoPulse 4s ease-in-out infinite, gradientShift 6s ease infinite;
    flex-shrink: 0;
}

@keyframes logoPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.25); }
    50% { box-shadow: 0 0 42px rgba(99, 102, 241, 0.45); }
}

.tech-title-group {
    flex: 1;
}

.tech-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(120deg, #818cf8, #22d3ee, #a78bfa, #818cf8);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    line-height: 1.2;
    animation: gradientShift 6s ease infinite;
}

.tech-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.5px;
    margin-top: 2px;
}

/* ===== 状态栏 ===== */
.status-bar {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 10px 16px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    margin-bottom: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: var(--text-muted);
    flex-wrap: wrap;
    backdrop-filter: blur(12px) saturate(140%);
    -webkit-backdrop-filter: blur(12px) saturate(140%);
    box-shadow: var(--shadow-sm);
}

.status-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #34d399;
    box-shadow: 0 0 8px rgba(52, 211, 153, 0.6);
    animation: statusPulse 3s ease-in-out infinite;
}

@keyframes statusPulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(52, 211, 153, 0.6); }
    50% { opacity: 0.5; box-shadow: 0 0 4px rgba(52, 211, 153, 0.3); }
}

.status-label {
    color: var(--text-muted);
}

.status-value {
    color: var(--text-primary);
    font-weight: 500;
}

.status-divider {
    width: 1px;
    height: 14px;
    background: var(--glass-border);
}

/* ===== 侧边栏 ===== */
.sidebar-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 8px 0 12px 0;
    border-bottom: 1px solid var(--glass-border);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sidebar-header-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background: var(--gradient-2);
    background-size: 200% 200%;
    font-size: 0.7rem;
    animation: gradientShift 6s ease infinite;
}

.tech-footer {
    font-family: 'Inter', sans-serif;
    color: var(--text-muted);
    font-size: 0.7rem;
    letter-spacing: 0.5px;
    text-align: center;
    padding: 12px 0;
    border-top: 1px solid var(--glass-border);
    line-height: 1.6;
}

.tech-footer .version {
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
}

/* ===== 空状态 ===== */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
}

.empty-state-icon {
    font-size: 3rem;
    margin-bottom: 16px;
    opacity: 0.5;
    animation: floatGlow 6s ease-in-out infinite;
}

.empty-state-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: var(--text-muted);
    line-height: 1.6;
}

#particles-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}

.stMainBlockContainer {
    position: relative;
    z-index: 1 !important;
}

.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--primary), var(--accent), transparent);
    background-size: 200% 100%;
    opacity: 0.3;
    margin: 16px 0;
    border: none;
    animation: gradientShift 5s ease infinite;
}

.conv-list-container {
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 8px;
}

.conv-list-container::-webkit-scrollbar {
    width: 3px;
}

.conv-list-container::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.18);
    border-radius: 10px;
}

.conv-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    margin-bottom: 4px;
    border-radius: var(--radius-sm);
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
    background: transparent;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
}

.conv-item:hover {
    background: rgba(99, 102, 241, 0.08);
    border-color: var(--glass-border);
}

.conv-item-active {
    background: rgba(99, 102, 241, 0.12) !important;
    border-color: rgba(99, 102, 241, 0.3) !important;
    box-shadow: inset 0 0 20px rgba(99, 102, 241, 0.06);
}

.conv-item-info {
    flex: 1;
    min-width: 0;
}

.conv-item-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.3;
}

.conv-item-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-muted);
    margin-top: 2px;
}
</style>
"""

def _build_js():
    return f"""
<div class="bg-grid"></div>
<div class="scan-beam"></div>
<canvas id="particles-canvas"></canvas>
<script>
(function() {{
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    const PARTICLE_COUNT = {AppSettings.PARTICLE_COUNT};
    const CONNECT_DIST = {AppSettings.PARTICLE_CONNECT_DIST};

    function resize() {{
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }}

    function createParticle() {{
        return {{
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 1.5 + 0.5,
            speedX: (Math.random() - 0.5) * 0.3,
            speedY: (Math.random() - 0.5) * 0.3,
            opacity: Math.random() * 0.5 + 0.1
        }};
    }}

    function init() {{
        resize();
        particles = [];
        for (let i = 0; i < PARTICLE_COUNT; i++) {{
            particles.push(createParticle());
        }}
    }}

    function draw() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {{
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(99, 102, 241, ${{p.opacity}})`;
            ctx.fill();
            p.x += p.speedX;
            p.y += p.speedY;
            if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
            if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
        }});
        for (let i = 0; i < particles.length; i++) {{
            for (let j = i + 1; j < particles.length; j++) {{
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CONNECT_DIST) {{
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(99, 102, 241, ${{0.06 * (1 - dist / CONNECT_DIST)}})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }}
            }}
        }}
        requestAnimationFrame(draw);
    }}

    window.addEventListener('resize', resize);
    init();
    draw();
}})();
</script>
"""


def render_styles():
    st.markdown(CSS_TEMPLATE + _build_js(), unsafe_allow_html=True)
