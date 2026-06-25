// ============================================================
// CONFIGURATION
// ============================================================
const PASSWORD = "fraudguard2026";
const REFRESH_INTERVAL = 60000;
let refreshTimer = null;
let dailyChart = null;
let riskChart = null;

// ============================================================
// THEME
// ============================================================
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const theme = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
    updateChartsTheme(theme);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = theme === 'dark' ? 'ti ti-sun' : 'ti ti-moon';
    }
}

function updateChartsTheme(theme) {
    const isDark = theme === 'dark';
    const textColor = isDark ? '#94a3b8' : '#475569';
    const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';
    
    if (dailyChart) {
        dailyChart.options.scales.x.ticks.color = textColor;
        dailyChart.options.scales.y.ticks.color = textColor;
        dailyChart.options.scales.x.grid.color = gridColor;
        dailyChart.options.scales.y.grid.color = gridColor;
        dailyChart.update();
    }
    
    if (riskChart) {
        riskChart.options.plugins.legend.labels.color = textColor;
        riskChart.update();
    }
}

function loadTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
}

// ============================================================
// HELPERS
// ============================================================
function formatCurrency(amount) {
    if (amount >= 1000000) return '$' + (amount / 1000000).toFixed(1) + 'M';
    if (amount >= 1000) return '$' + (amount / 1000).toFixed(1) + 'K';
    return '$' + amount.toFixed(0);
}

function formatNumber(num) {
    return num.toLocaleString();
}

function safeSetText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function safeSetHTML(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
}

// ============================================================
// PASSWORD
// ============================================================
function checkPassword() {
    const input = document.getElementById('password-input');
    const error = document.getElementById('login-error');
    
    if (!input) return;
    
    if (input.value === PASSWORD) {
        document.getElementById('login-overlay').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'block';
        loadData();
        startAutoRefresh();
    } else {
        if (error) error.style.display = 'block';
        input.value = '';
        input.focus();
        setTimeout(() => { if (error) error.style.display = 'none'; }, 3000);
    }
}

// ============================================================
// LOAD DATA
// ============================================================
async function loadData() {
    try {
        const response = await fetch('data/reports.json');
        if (!response.ok) throw new Error('Failed to load data');
        const data = await response.json();
        renderDashboard(data);
        updateTimestamp(data);
        return data;
    } catch (error) {
        console.error('Error:', error);
        document.querySelector('.dashboard').innerHTML = `
            <div style="text-align:center;padding:60px;background:var(--surface);border-radius:16px;border:1px solid var(--border);">
                <div style="font-size:48px;margin-bottom:16px;">⚠️</div>
                <h3>Unable to load data</h3>
                <p style="color:var(--text-secondary);">${error.message}</p>
                <button onclick="location.reload()" style="margin-top:16px;padding:8px 24px;background:var(--blue);color:#fff;border:none;border-radius:8px;cursor:pointer;">Retry</button>
            </div>
        `;
        return null;
    }
}

// ============================================================
// RENDER
// ============================================================
function renderDashboard(data) {
    const weekly = data.weekly || {};
    const monthly = data.monthly || {};
    const summary = data.summary || {};
    const daily = data.daily?.transactions || [];

    // ---- KPI ----
    const total = weekly.total || 0;
    const blocked = weekly.blocked || 0;
    const reviewed = weekly.reviewed || 0;
    const amount = weekly.total_amount || 0;
    const blockedAmount = weekly.blocked_amount || 0;
    const risk = (weekly.avg_risk || 0) * 100;
    const users = summary.active_users_7d || 0;

    safeSetText('total-tx', formatNumber(total));
    safeSetText('total-tx-sub', `${blocked} blocked (${total > 0 ? ((blocked/total)*100).toFixed(1) : 0}%)`);

    safeSetText('total-amount', formatCurrency(amount));
    safeSetText('blocked-amount', formatCurrency(blockedAmount));
    safeSetText('blocked-count', `${blocked} transactions`);

    safeSetText('avg-risk', risk.toFixed(1) + '%');
    safeSetText('avg-risk-sub', risk > 20 ? '⚠️ Elevated' : '✅ Stable');

    safeSetText('pending-review', reviewed);
    safeSetText('active-users', users);

    // ---- RISK ----
    const riskDist = summary.risk_distribution || [];
    const totalRisk = riskDist.reduce((s, r) => s + r.count, 0) || 1;
    const riskMap = {};
    riskDist.forEach(r => { riskMap[r.risk_level] = r.count; });

    const low = ((riskMap.LOW || 0) / totalRisk * 100);
    const med = ((riskMap.MEDIUM || 0) / totalRisk * 100);
    const high = ((riskMap.HIGH || 0) / totalRisk * 100);
    const crit = ((riskMap.CRITICAL || 0) / totalRisk * 100);

    safeSetText('r-low', low.toFixed(1) + '%');
    safeSetText('r-med', med.toFixed(1) + '%');
    safeSetText('r-high', high.toFixed(1) + '%');
    safeSetText('r-crit', crit.toFixed(1) + '%');
    safeSetText('risk-total', totalRisk);

    // ---- CHARTS ----
    renderDailyChart(daily);
    renderRiskChart(low, med, high, crit, totalRisk);

    // ---- USERS ----
    renderUsers(summary.top_users || []);

    // ---- OVERRIDES ----
    renderOverrides(summary.override_activity || []);

    // ---- HEALTH ----
    safeSetText('h-analysts', (summary.override_activity || []).length || 0);
    safeSetText('h-alerts', blocked);
    safeSetText('h-users', summary.total_users || 0);
}

// ============================================================
// DAILY CHART (Chart.js)
// ============================================================
function renderDailyChart(data) {
    const ctx = document.getElementById('dailyChart');
    if (!ctx) return;

    const d = data.slice(0, 7).reverse();
    const labels = d.map(x => new Date(x.date).toLocaleDateString('en', { month: 'short', day: 'numeric' }));

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#475569';
    const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';

    if (dailyChart) dailyChart.destroy();

    dailyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total',
                    data: d.map(x => x.total || 0),
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    borderRadius: 4,
                    order: 1
                },
                {
                    label: 'Blocked',
                    data: d.map(x => x.blocked || 0),
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderRadius: 4,
                    order: 2
                },
                {
                    label: 'Approved',
                    data: d.map(x => x.approved || 0),
                    backgroundColor: 'rgba(16, 185, 129, 0.6)',
                    borderColor: '#10b981',
                    borderWidth: 2,
                    borderRadius: 4,
                    order: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: textColor }
                }
            }
        }
    });
}

// ============================================================
// RISK CHART (Chart.js Doughnut)
// ============================================================
function renderRiskChart(low, med, high, crit, total) {
    const ctx = document.getElementById('riskChart');
    if (!ctx) return;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#475569';

    if (riskChart) riskChart.destroy();

    riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low', 'Medium', 'High', 'Critical'],
            datasets: [{
                data: [low, med, high, crit],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// ============================================================
// TABLES
// ============================================================
function renderUsers(users) {
    const tbody = document.getElementById('user-table');
    if (!tbody) return;

    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty">No user data</td></tr>';
        return;
    }

    tbody.innerHTML = users.slice(0, 5).map(u => {
        const rate = u.login_count > 0 ? ((u.successful / u.login_count) * 100).toFixed(1) : 0;
        return `
            <tr>
                <td><strong>${u.username || 'Unknown'}</strong></td>
                <td>${u.login_count || 0}</td>
                <td class="success">${u.successful || 0}</td>
                <td class="danger">${u.failed || 0}</td>
                <td>${rate}%</td>
            </tr>
        `;
    }).join('');
}

function renderOverrides(overrides) {
    const tbody = document.getElementById('override-table');
    if (!tbody) return;

    if (!overrides || overrides.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty">No override data</td></tr>';
        return;
    }

    tbody.innerHTML = overrides.slice(0, 5).map(o => {
        const rate = o.total > 0 ? ((o.approved / o.total) * 100).toFixed(1) : 0;
        return `
            <tr>
                <td><strong>${o.analyst || 'Unknown'}</strong></td>
                <td>${o.total || 0}</td>
                <td class="success">${o.approved || 0}</td>
                <td class="danger">${o.blocked || 0}</td>
                <td>${rate}%</td>
            </tr>
        `;
    }).join('');
}

// ============================================================
// TIMESTAMP
// ============================================================
function updateTimestamp(data) {
    const el = document.getElementById('timestamp');
    if (!el) return;
    const date = new Date(data.generated_at);
    el.textContent = date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================================
// REFRESH
// ============================================================
function refreshData() {
    const el = document.getElementById('timestamp');
    if (el) el.textContent = 'Refreshing...';
    loadData();
}

function startAutoRefresh() {
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(loadData, REFRESH_INTERVAL);
}

// ============================================================
// KEYBOARD
// ============================================================
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && document.getElementById('login-overlay')?.style.display !== 'none') {
        checkPassword();
    }
    if (e.key === 'r' && e.ctrlKey) {
        e.preventDefault();
        refreshData();
    }
});

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    console.log('🛡️ FraudGuard Dashboard loaded');
    const input = document.getElementById('password-input');
    if (input) input.focus();
});