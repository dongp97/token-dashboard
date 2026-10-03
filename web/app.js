async function loadStats() {
    const status = document.getElementById('status');
    try {
        const resp = await fetch('/api/stats');
        const data = await resp.json();
        renderDashboard(data);
        status.textContent = 'Connected to DSH cost-meter';
        status.style.color = '#3fb950';
    } catch (e) {
        status.textContent = 'Error loading data: ' + e.message;
        status.style.color = '#f85149';
    }
}

function fmt(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toLocaleString();
}

function renderDashboard(data) {
    // Summary cards
    document.getElementById('card-sessions').textContent = data.total_sessions;
    document.getElementById('card-tokens').textContent = fmt(data.total_tokens);
    document.getElementById('card-input').textContent = fmt(data.total_input_tokens);
    document.getElementById('card-output').textContent = fmt(data.total_output_tokens);
    document.getElementById('card-cost').textContent = '$' + data.total_cost.toFixed(4);

    // Model chart
    const modelChart = document.getElementById('model-chart');
    const maxModelCost = Math.max(...data.by_model.map(m => m.cost), 1);
    modelChart.innerHTML = data.by_model.map(m => {
        const pct = (m.cost / maxModelCost * 100).toFixed(0);
        return `
            <div class="bar-row">
                <div class="bar-label" title="${m.model}">${m.model}</div>
                <div class="bar-track">
                    <div class="bar-fill model" style="width: ${pct}%">${m.calls} calls</div>
                </div>
                <div class="bar-value">$${m.cost.toFixed(4)}</div>
            </div>
        `;
    }).join('');

    // Daily chart
    const dailyChart = document.getElementById('daily-chart');
    const maxDailyTokens = Math.max(...data.daily.map(d => d.tokens), 1);
    dailyChart.innerHTML = data.daily.slice(-14).map(d => {
        const pct = (d.tokens / maxDailyTokens * 100).toFixed(0);
        return `
            <div class="bar-row">
                <div class="bar-label">${d.date}</div>
                <div class="bar-track">
                    <div class="bar-fill daily" style="width: ${pct}%">${fmt(d.tokens)}</div>
                </div>
                <div class="bar-value">$${d.cost.toFixed(4)}</div>
            </div>
        `;
    }).join('');

    // Sessions table
    const tbody = document.querySelector('#sessions-table tbody');
    tbody.innerHTML = data.by_session.map(s => `
        <tr>
            <td>${s.full_id.substring(0, 20)}...</td>
            <td>${s.calls}</td>
            <td>${fmt(s.tokens)}</td>
            <td>$${s.cost.toFixed(4)}</td>
        </tr>
    `).join('');
}

loadStats();
