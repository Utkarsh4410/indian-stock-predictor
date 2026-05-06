// API URL - points to our live Render backend
const API_BASE_URL = "https://indian-stock-predictor-u36d.onrender.com/api";

// ============================================================
//  FLOATING TECH BUBBLES — Mouse-following canvas animation
// ============================================================
(function () {
    const canvas = document.getElementById('bubblesCanvas');
    const ctx    = canvas.getContext('2d');

    const TECH = [
        { label: 'Python',      color: [55,  118, 171], r: 38 },
        { label: 'TensorFlow',  color: [220,  85,   0], r: 36 },
        { label: 'FastAPI',     color: [0,   150, 136], r: 34 },
        { label: 'LSTM',        color: [124,  58, 237], r: 32 },
        { label: 'VADER NLP',   color: [139,  92, 246], r: 30 },
        { label: 'Chart.js',    color: [229,  62,  62], r: 30 },
        { label: 'yFinance',    color: [26,   86, 219], r: 30 },
        { label: 'Render',      color: [70,  227, 183], r: 28 },
        { label: 'Numpy',       color: [74,  114, 177], r: 28 },
        { label: 'Pandas',      color: [130,  80, 210], r: 28 },
        { label: 'scikit',      color: [247, 147,  30], r: 26 },
        { label: 'Keras',       color: [210,   0,   0], r: 26 },
    ];

    let mouse = { x: -999, y: -999 };
    let W, H;
    let bubbles = [];

    function rand(min, max) { return Math.random() * (max - min) + min; }

    function initBubbles() {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;

        bubbles = TECH.map(({ label, color, r }) => ({
            label, color, r,
            x:  rand(r + 20, W - r - 20),
            y:  rand(r + 20, H - r - 20),
            vx: rand(-0.6, 0.6),
            vy: rand(-0.6, 0.6),
            alpha: rand(0.55, 0.85),   // base opacity
        }));
    }

    function drawBubble(b) {
        const { x, y, r, color, label, alpha } = b;
        const [R, G, B] = color;

        // Glow
        const glow = ctx.createRadialGradient(x, y, r * 0.5, x, y, r * 1.8);
        glow.addColorStop(0, `rgba(${R},${G},${B},${alpha * 0.25})`);
        glow.addColorStop(1, `rgba(${R},${G},${B},0)`);
        ctx.beginPath();
        ctx.arc(x, y, r * 1.8, 0, Math.PI * 2);
        ctx.fillStyle = glow;
        ctx.fill();

        // Main bubble with radial gradient (light top-left → dark bottom-right)
        const grad = ctx.createRadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r);
        grad.addColorStop(0, `rgba(${Math.min(255,R+80)},${Math.min(255,G+80)},${Math.min(255,B+80)},${alpha})`);
        grad.addColorStop(1, `rgba(${Math.max(0,R-40)},${Math.max(0,G-40)},${Math.max(0,B-40)},${alpha})`);
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();

        // Rim
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(${R},${G},${B},${alpha * 0.8})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Gloss highlight
        const gloss = ctx.createRadialGradient(x - r * 0.25, y - r * 0.3, 0, x - r * 0.1, y - r * 0.1, r * 0.6);
        gloss.addColorStop(0, `rgba(255,255,255,${alpha * 0.55})`);
        gloss.addColorStop(1, `rgba(255,255,255,0)`);
        ctx.beginPath();
        ctx.ellipse(x - r * 0.18, y - r * 0.2, r * 0.5, r * 0.32, -0.5, 0, Math.PI * 2);
        ctx.fillStyle = gloss;
        ctx.fill();

        // Label
        ctx.font = `bold ${Math.max(9, r * 0.32)}px Outfit, Arial, sans-serif`;
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = `rgba(0,0,0,0.5)`;
        ctx.fillText(label, x + 0.8, y + 0.8);
        ctx.fillStyle = `rgba(255,255,255,${alpha + 0.15})`;
        ctx.fillText(label, x, y);
    }

    function update() {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
        ctx.clearRect(0, 0, W, H);

        bubbles.forEach(b => {
            // Mouse attraction: gentle pull toward cursor
            const dx  = mouse.x - b.x;
            const dy  = mouse.y - b.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const ATTRACT_RADIUS = 200;
            const ATTRACT_FORCE  = 0.03;

            if (dist < ATTRACT_RADIUS && dist > 0) {
                const force = (1 - dist / ATTRACT_RADIUS) * ATTRACT_FORCE;
                b.vx += (dx / dist) * force;
                b.vy += (dy / dist) * force;
            }

            // Speed cap
            const speed = Math.sqrt(b.vx * b.vx + b.vy * b.vy);
            const MAX_SPEED = 2.5;
            if (speed > MAX_SPEED) {
                b.vx = (b.vx / speed) * MAX_SPEED;
                b.vy = (b.vy / speed) * MAX_SPEED;
            }

            // Move
            b.x += b.vx;
            b.y += b.vy;

            // Bounce off walls with damping
            if (b.x - b.r < 0)  { b.x = b.r;    b.vx = Math.abs(b.vx) * 0.85; }
            if (b.x + b.r > W)  { b.x = W - b.r; b.vx = -Math.abs(b.vx) * 0.85; }
            if (b.y - b.r < 0)  { b.y = b.r;    b.vy = Math.abs(b.vy) * 0.85; }
            if (b.y + b.r > H)  { b.y = H - b.r; b.vy = -Math.abs(b.vy) * 0.85; }

            drawBubble(b);
        });

        requestAnimationFrame(update);
    }

    // Track mouse
    window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
    window.addEventListener('mouseleave', () => { mouse.x = -999; mouse.y = -999; });
    window.addEventListener('resize', initBubbles);

    initBubbles();
    update();
})();


const elements = {
    tickerInput: document.getElementById('tickerInput'),
    predictBtn: document.getElementById('predictBtn'),
    btnText: document.querySelector('.btn-text'),
    loader: document.querySelector('.loader'),
    errorMsg: document.getElementById('errorMsg'),
    dashboard: document.getElementById('resultsDashboard'),
    lastClosePrice: document.getElementById('lastClosePrice'),
    predictedPrice: document.getElementById('predictedPrice'),
    priceChange: document.getElementById('priceChange'),
    overallSentiment: document.getElementById('overallSentiment'),
    sentimentScore: document.getElementById('sentimentScore'),
    newsList: document.getElementById('newsList')
};

let priceChartInstance = null;

elements.predictBtn.addEventListener('click', async () => {
    const ticker = elements.tickerInput.value.trim().toUpperCase();
    if (!ticker) return;

    // UI Loading State
    elements.btnText.classList.add('hidden');
    elements.loader.classList.remove('hidden');
    elements.predictBtn.disabled = true;
    elements.errorMsg.classList.add('hidden');
    elements.dashboard.classList.add('hidden');

    try {
        // Fetch Prediction and Sentiment in parallel
        const [predictRes, sentimentRes] = await Promise.all([
            fetch(`${API_BASE_URL}/predict?ticker=${ticker}`),
            fetch(`${API_BASE_URL}/sentiment?ticker=${ticker}`)
        ]);

        if (!predictRes.ok) throw new Error("Failed to fetch prediction data");
        
        const predictData = await predictRes.json();
        let sentimentData = null;
        
        if (sentimentRes.ok) {
            sentimentData = await sentimentRes.json();
        }

        updateDashboard(predictData, sentimentData);

    } catch (error) {
        elements.errorMsg.textContent = error.message || "An error occurred fetching data.";
        elements.errorMsg.classList.remove('hidden');
    } finally {
        elements.btnText.classList.remove('hidden');
        elements.loader.classList.add('hidden');
        elements.predictBtn.disabled = false;
    }
});

function updateDashboard(predictData, sentimentData) {
    // 1. Update Prices
    elements.lastClosePrice.textContent = `₹${predictData.last_price.toFixed(2)}`;
    elements.predictedPrice.textContent = `₹${predictData.predicted_price.toFixed(2)}`;
    
    const change = predictData.price_change;
    const isPositive = change >= 0;
    
    elements.priceChange.textContent = `${isPositive ? '+' : ''}${change.toFixed(2)} (${predictData.percent_change.toFixed(2)}%)`;
    elements.priceChange.className = `change-badge ${isPositive ? 'badge-positive' : 'badge-negative'}`;

    // 2. Render Chart
    renderChart(predictData.historical_dates, predictData.historical_prices, predictData.predicted_price);

    // 3. Update Sentiment
    if (sentimentData && !sentimentData.error) {
        elements.overallSentiment.textContent = sentimentData.overall_label;
        elements.sentimentScore.textContent = `Score: ${sentimentData.overall_score.toFixed(2)}`;
        
        elements.newsList.innerHTML = sentimentData.articles.map(article => `
            <div class="news-item">
                <a href="${article.link}" target="_blank" class="news-title">${article.title}</a>
                <div class="news-meta">
                    <span>${article.label}</span> • 
                    <span>${article.publisher}</span>
                </div>
            </div>
        `).join('');
    } else {
        elements.overallSentiment.textContent = "No Data";
        elements.newsList.innerHTML = "<p>Could not load recent news.</p>";
    }

    // Show Dashboard
    elements.dashboard.classList.remove('hidden');
}

function renderChart(labels, dataPoints, predictedPrice) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    if (priceChartInstance) {
        priceChartInstance.destroy();
    }

    // Add predicted point to the end
    const chartLabels = [...labels, "Next Day (Predicted)"];
    const actualData = [...dataPoints, null];
    const predictedData = [...Array(dataPoints.length - 1).fill(null), dataPoints[dataPoints.length - 1], predictedPrice];

    priceChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: 'Historical Price',
                    data: actualData,
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    tension: 0.1,
                    pointRadius: 0
                },
                {
                    label: 'Prediction',
                    data: predictedData,
                    borderColor: '#8b5cf6',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.1,
                    pointRadius: 4,
                    pointBackgroundColor: '#8b5cf6'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', maxTicksLimit: 10 } },
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
            }
        }
    });
}
