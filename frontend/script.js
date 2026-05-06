// Use the URL of your backend. For local testing, use http://127.0.0.1:8000
const API_BASE_URL = "http://127.0.0.1:8000/api";

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
