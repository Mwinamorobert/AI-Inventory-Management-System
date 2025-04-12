function refreshInsights() {
    console.log('Refreshing insights');
    fetch('/insights/', { method: 'GET' })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const forecastData = doc.querySelector('#forecast-chart-data')?.textContent;
            const anomaliesData = doc.querySelector('#anomalies-chart-data')?.textContent;
            const stockTrendData = doc.querySelector('#stock-trend-data')?.textContent;

            if (forecastData) {
                Plotly.newPlot('forecast-chart', JSON.parse(forecastData));
            } else {
                document.getElementById('forecast-chart').innerHTML = '<p class="text-muted text-center">No forecast data yet! Add more items. 🌟</p>';
            }

            if (anomaliesData) {
                Plotly.newPlot('anomalies-chart', JSON.parse(anomaliesData));
            } else {
                document.getElementById('anomalies-chart').innerHTML = '<p class="text-muted text-center">No anomalies! Looking good! 🌟</p>';
            }

            if (stockTrendData) {
                Plotly.newPlot('stock-trend-chart', JSON.parse(stockTrendData));
            } else {
                document.getElementById('stock-trend-chart').innerHTML = '<p class="text-muted text-center">No trend data yet! 🌟</p>';
            }

            document.querySelectorAll('.spinner-container').forEach(spinner => spinner.style.display = 'none');

            // Restore theme toggle button text after fetch
            const toggleButton = document.getElementById('theme-toggle');
            if (toggleButton) {
                const isDark = localStorage.getItem('theme') === 'dark';
                toggleButton.textContent = isDark ? '☀️ Toggle Theme' : '🌙 Toggle Theme';
            }
        })
        .catch(error => console.error('Error refreshing insights:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    refreshInsights();
    setInterval(refreshInsights, 30000);  // Update every 30 seconds
});