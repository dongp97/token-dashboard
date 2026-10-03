// ===== Theme =====
(function initTheme() {
    const saved = localStorage.getItem('td-theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        document.documentElement.setAttribute('data-theme', 'light');
    }
})();

document.getElementById('theme-toggle').addEventListener('click', function () {
    const cur = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('td-theme', next);
});

// ===== Refresh countdown =====
let refreshInterval = null;
let countdownValue = 30;
const refreshCountEl = document.getElementById('refresh-count');

function startCountdown() {
    countdownValue = 30;
    if (refreshInterval) clearInterval(refreshInterval);
    refreshInterval = setInterval(function () {
        countdownValue--;
        if (refreshCountEl) refreshCountEl.textContent = countdownValue;
        if (countdownValue <= 0) {
            clearInterval(refreshInterval);
        }
    }, 1000);
}

// ===== Data loading =====
let isLoading = false;
let hasLoaded = false;

async function loadStats() {
    if (isLoading) return;
    isLoading = true;
    const status = document.getElementById('status');
    try {
        const resp = await fetch('/api/stats');
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        renderDashboard(data);
        status.textContent = 'Connected to DSH cost-meter • ' + new Date().toLocaleTimeString();
        status.style.color = 'var(--green)';
        hasLoaded = true;
    } catch (e) {
        status.textContent = 'Error loading data: ' + e.message;
        status.style.color = 'var(--red)';
    } finally {
        isLoading = false;
        startCountdown();
    }
}

function fmt(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toLocaleString();
}

function removeSkeletons() {
    document.querySelectorAll('.card.skeleton').forEach(function (el) {
        el.classList.remove('skeleton');
    });
    document.querySelectorAll('.loading-skeleton-chart').forEach(function (el) {
        el.remove();
    });
}

// ===== Pie chart =====
const PIE_COLORS = ['#1f6feb', '#238636', '#8957e5', '#f0883e', '#d29922', '#bf5700', '#cf222e', '#3fb950'];

function renderPieChart(container, data) {
    const total = data.reduce(function (s, d) { return s + d.cost; }, 0);
    if (total === 0) {
        container.innerHTML = '<div style="color:var(--text-muted);padding:2rem 0;text-align:center">No data</div>';
        return;
    }

    let gradient = 'conic-gradient(';
    let currentAngle = 0;
    const segments = [];

    for (let i = 0; i < data.length; i++) {
        const d = data[i];
        const pct = d.cost / total;
        const angle = pct * 360;
        const color = PIE_COLORS[i % PIE_COLORS.length];
        gradient += color + ' ' + currentAngle + 'deg ' + (currentAngle + angle) + 'deg';
        if (i < data.length - 1) gradient += ', ';
        currentAngle += angle;
        segments.push({ model: d.model, color: color, pct: (pct * 100).toFixed(1), calls: d.calls, cost: d.cost });
    }
    gradient += ')';

    let legendHtml = '';
    for (let i = 0; i < segments.length; i++) {
        const s = segments[i];
        legendHtml += '<span class="pie-legend-item"><span class="pie-legend-color" style="background:' + s.color + '"></span>' + s.model + ' ' + s.pct + '%</span>';
    }

    container.innerHTML = '<div class="pie-chart-container">' +
        '<div class="pie-chart" style="background:' + gradient + '"></div>' +
        '<div class="pie-legend">' + legendHtml + '</div>' +
        '</div>';
}

// ===== SVG line chart =====
function renderSvgChart(container, data) {
    if (!data || data.length === 0) {
        container.innerHTML = '<div style="color:var(--text-muted);padding:2rem 0;text-align:center">No data</div>';
        return;
    }

    const w = 500;
    const h = 200;
    const pad = { top: 15, right: 15, bottom: 25, left: 50 };
    const chartW = w - pad.left - pad.right;
    const chartH = h - pad.top - pad.bottom;

    const values = data.map(function (d) { return d.tokens; });
    const maxVal = Math.max.apply(null, values);
    const minVal = 0;

    // Grid lines
    let gridLines = '';
    const gridCount = 4;
    for (let i = 0; i <= gridCount; i++) {
        const y = pad.top + (chartH / gridCount) * i;
        gridLines += '<line class="grid-line" x1="' + pad.left + '" y1="' + y + '" x2="' + (w - pad.right) + '" y2="' + y + '"/>';
        const labelVal = Math.round(maxVal - (maxVal - minVal) * (i / gridCount));
        gridLines += '<text class="axis-label" x="' + (pad.left - 5) + '" y="' + (y + 3) + '" text-anchor="end">' + fmt(labelVal) + '</text>';
    }

    // Points
    const points = data.map(function (d, i) {
        const x = pad.left + (chartW / Math.max(data.length - 1, 1)) * i;
        const y = pad.top + chartH - ((d.tokens - minVal) / (maxVal - minVal || 1)) * chartH;
        return { x: x, y: y, date: d.date, tokens: d.tokens, cost: d.cost };
    });

    // Area path
    let areaPath = 'M ' + points[0].x + ' ' + (pad.top + chartH);
    for (let i = 0; i < points.length; i++) {
        areaPath += ' L ' + points[i].x + ' ' + points[i].y;
    }
    areaPath += ' L ' + points[points.length - 1].x + ' ' + (pad.top + chartH) + ' Z';

    // Line path
    let linePath = 'M ' + points[0].x + ' ' + points[0].y;
    for (let i = 1; i < points.length; i++) {
        linePath += ' L ' + points[i].x + ' ' + points[i].y;
    }

    // Data points circles
    let circles = '';
    for (let i = 0; i < points.length; i++) {
        const p = points[i];
        circles += '<circle class="data-point" cx="' + p.x + '" cy="' + p.y + '" data-date="' + p.date + '" data-tokens="' + p.tokens + '" data-cost="' + p.cost.toFixed(4) + '"/>';
    }

    // X axis labels (show ~5 evenly spaced)
    let xLabels = '';
    const labelStep = Math.max(1, Math.floor(data.length / 5));
    for (let i = 0; i < data.length; i += labelStep) {
        const p = points[i];
        xLabels += '<text class="axis-label" x="' + p.x + '" y="' + (h - 5) + '" text-anchor="middle">' + data[i].date.substring(5) + '</text>';
    }

    const svg = '<svg class="svg-chart" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="xMidYMid meet">' +
        gridLines +
        '<path class="area-fill" d="' + areaPath + '"/>' +
        '<path class="trend-line" d="' + linePath + '"/>' +
        circles +
        xLabels +
        '</svg>';

    container.innerHTML = '<div class="svg-chart-container">' + svg + '</div>';

    // Tooltip
    let tooltip = container.querySelector('.tooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        container.style.position = 'relative';
        container.appendChild(tooltip);
    }

    const dataPoints = container.querySelectorAll('.data-point');
    for (let i = 0; i < dataPoints.length; i++) {
        dataPoints[i].addEventListener('mouseenter', function (e) {
            const d = e.target.getAttribute('data-date');
            const t = parseInt(e.target.getAttribute('data-tokens'), 10);
            const c = e.target.getAttribute('data-cost');
            tooltip.innerHTML = '<strong>' + d + '</strong><br>Tokens: ' + fmt(t) + '<br>Cost: $' + c;
            tooltip.classList.add('visible');
        });
        dataPoints[i].addEventListener('mousemove', function (e) {
            const rect = container.querySelector('.svg-chart-container').getBoundingClientRect();
            tooltip.style.left = (e.clientX - rect.left + 10) + 'px';
            tooltip.style.top = (e.clientY - rect.top - 40) + 'px';
        });
        dataPoints[i].addEventListener('mouseleave', function () {
            tooltip.classList.remove('visible');
        });
    }
}

// ===== Dashboard render =====
function renderDashboard(data) {
    removeSkeletons();

    // Summary cards
    document.getElementById('card-sessions').textContent = data.total_sessions;
    document.getElementById('card-tokens').textContent = fmt(data.total_tokens);
    document.getElementById('card-input').textContent = fmt(data.total_input_tokens);
    document.getElementById('card-output').textContent = fmt(data.total_output_tokens);
    document.getElementById('card-cost').textContent = '$' + data.total_cost.toFixed(4);

    // Pie chart for model distribution
    const modelChart = document.getElementById('model-chart');
    renderPieChart(modelChart, data.by_model);

    // SVG line chart for daily trend
    const dailyChart = document.getElementById('daily-chart');
    renderSvgChart(dailyChart, data.daily.slice(-14));

    // Sessions table
    const tbody = document.querySelector('#sessions-table tbody');
    tbody.innerHTML = data.by_session.map(function (s) {
        return '<tr>' +
            '<td>' + s.full_id.substring(0, 20) + '...</td>' +
            '<td>' + s.calls + '</td>' +
            '<td>' + fmt(s.tokens) + '</td>' +
            '<td>$' + s.cost.toFixed(4) + '</td>' +
            '</tr>';
    }).join('');
}

// ===== Auto-refresh every 30s =====
loadStats();
setInterval(loadStats, 30000);
