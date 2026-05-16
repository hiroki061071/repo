const preset = document.getElementById('preset');
const latInput = document.getElementById('lat');
const lonInput = document.getElementById('lon');
const timezoneInput = document.getElementById('timezone');
const loadBtn = document.getElementById('loadBtn');
const locationTitle = document.getElementById('locationTitle');
const metaText = document.getElementById('metaText');
const tableBody = document.querySelector('#forecastTable tbody');

const tempChart = echarts.init(document.getElementById('tempChart'));
const precipChart = echarts.init(document.getElementById('precipChart'));
const windChart = echarts.init(document.getElementById('windChart'));

preset.addEventListener('change', () => {
    const [lat, lon, name] = preset.value.split(',');
    latInput.value = lat;
    lonInput.value = lon;
    locationTitle.textContent = name;
});

loadBtn.addEventListener('click', loadForecast);

window.addEventListener('resize', () => {
    tempChart.resize();
    precipChart.resize();
    windChart.resize();
});

async function loadForecast() {
    const lat = latInput.value;
    const lon = lonInput.value;
    const timezone = timezoneInput.value;

    const url = `/api/forecast?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&timezone=${encodeURIComponent(timezone)}`;
    metaText.textContent = '予報を取得中...';

    try {
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        renderDashboard(data);
    } catch (err) {
        console.error(err);
        metaText.textContent = `取得失敗: ${err.message}`;
        alert(`予報の取得に失敗しました: ${err.message}`);
    }
}

function renderDashboard(data) {
    const days = data.days || [];
    metaText.textContent =
        `緯度 ${data.latitude}, 経度 ${data.longitude}, タイムゾーン ${data.timezone}, 取得日数 ${days.length}日`;

    renderTable(days);
    renderTempChart(days);
    renderPrecipChart(days);
    renderWindChart(days);
}

function renderTable(days) {
    tableBody.innerHTML = '';

    for (const d of days) {
        const tr = document.createElement('tr');

        const weather = getWeatherInfo(d.weatherCode);

        tr.innerHTML = `
            <td>${d.date ?? ''}</td>
            <td>${weather.icon} ${weather.label}</td>
            <td>${fmt(d.tempMax)} ℃</td>
            <td>${fmt(d.tempMin)} ℃</td>
            <td>${fmti(d.precipProbabilityMax)} %</td>
            <td>${fmt(d.windSpeedMax)} m/s</td>
            <td>${fmti(d.weatherCode)}</td>
        `;

        tableBody.appendChild(tr);
    }
}

function renderTempChart(days) {
    const dates = days.map(d => d.date);
    const tempMax = days.map(d => d.tempMax);
    const tempMin = days.map(d => d.tempMin);
    const weatherLabels = days.map(d => getWeatherInfo(d.weatherCode).label);

    tempChart.setOption({
        title: {
            text: '7日間の最高・最低気温'
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                const i = params[0].dataIndex;
                return [
                    `<b>${dates[i]}</b>`,
                    `天気: ${weatherLabels[i]}`,
                    `最高気温: ${fmt(tempMax[i])} ℃`,
                    `最低気温: ${fmt(tempMin[i])} ℃`
                ].join('<br>');
            }
        },
        legend: {
            data: ['最高気温', '最低気温']
        },
        xAxis: {
            type: 'category',
            data: dates
        },
        yAxis: {
            type: 'value',
            name: '気温(℃)'
        },
        series: [
            {
                name: '最高気温',
                type: 'line',
                smooth: true,
                data: tempMax
            },
            {
                name: '最低気温',
                type: 'line',
                smooth: true,
                data: tempMin
            }
        ]
    });
}

function renderPrecipChart(days) {
    const dates = days.map(d => d.date);
    const precip = days.map(d => d.precipProbabilityMax);
    const weatherLabels = days.map(d => getWeatherInfo(d.weatherCode).label);

    precipChart.setOption({
        title: {
            text: '7日間の最大降水確率'
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                const i = params[0].dataIndex;
                return [
                    `<b>${dates[i]}</b>`,
                    `天気: ${weatherLabels[i]}`,
                    `降水確率: ${fmti(precip[i])} %`
                ].join('<br>');
            }
        },
        xAxis: {
            type: 'category',
            data: dates
        },
        yAxis: {
            type: 'value',
            name: '降水確率(%)',
            min: 0,
            max: 100
        },
        series: [
            {
                name: '降水確率',
                type: 'bar',
                data: precip
            }
        ]
    });
}

function renderWindChart(days) {
    const dates = days.map(d => d.date);
    const wind = days.map(d => d.windSpeedMax);
    const code = days.map(d => d.weatherCode);

    windChart.setOption({
        title: {
            text: '7日間の最大風速 + 天気コード'
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                const i = params[0].dataIndex;
                const weather = getWeatherInfo(code[i]);

                return [
                    `<b>${dates[i]}</b>`,
                    `${weather.icon} ${weather.label}`,
                    `最大風速: ${fmt(wind[i])} m/s`,
                    `天気コード: ${fmti(code[i])}`
                ].join('<br>');
            }
        },
        legend: {
            data: ['最大風速', '天気コード']
        },
        xAxis: {
            type: 'category',
            data: dates
        },
        yAxis: [
            {
                type: 'value',
                name: '最大風速(m/s)'
            },
            {
                type: 'value',
                name: '天気コード'
            }
        ],
        series: [
            {
                name: '最大風速',
                type: 'line',
                smooth: true,
                yAxisIndex: 0,
                data: wind
            },
            {
                name: '天気コード',
                type: 'line',
                smooth: false,
                yAxisIndex: 1,
                data: code
            }
        ]
    });
}

function getWeatherInfo(code) {
    const weatherMap = {
        0:  { label: '快晴', icon: '☀️' },
        1:  { label: '晴れ', icon: '🌤️' },
        2:  { label: '晴れ時々曇り', icon: '⛅' },
        3:  { label: '曇り', icon: '☁️' },

        45: { label: '霧', icon: '🌫️' },
        48: { label: '着氷性の霧', icon: '🌫️' },

        51: { label: '弱い霧雨', icon: '🌦️' },
        53: { label: '並の霧雨', icon: '🌦️' },
        55: { label: '強い霧雨', icon: '🌧️' },

        56: { label: '弱い着氷性霧雨', icon: '🌧️' },
        57: { label: '強い着氷性霧雨', icon: '🌧️' },

        61: { label: '弱い雨', icon: '🌧️' },
        63: { label: '並の雨', icon: '🌧️' },
        65: { label: '強い雨', icon: '🌧️' },

        66: { label: '弱い着氷性雨', icon: '🌧️' },
        67: { label: '強い着氷性雨', icon: '🌧️' },

        71: { label: '弱い雪', icon: '🌨️' },
        73: { label: '並の雪', icon: '🌨️' },
        75: { label: '強い雪', icon: '❄️' },

        77: { label: '雪粒', icon: '❄️' },

        80: { label: '弱いにわか雨', icon: '🌦️' },
        81: { label: '並のにわか雨', icon: '🌦️' },
        82: { label: '激しいにわか雨', icon: '⛈️' },

        85: { label: '弱いにわか雪', icon: '🌨️' },
        86: { label: '強いにわか雪', icon: '❄️' },

        95: { label: '雷雨', icon: '⛈️' },
        96: { label: '弱い雹を伴う雷雨', icon: '⛈️' },
        99: { label: '強い雹を伴う雷雨', icon: '⛈️' }
    };

    return weatherMap[code] || { label: '不明', icon: '❔' };
}

function fmt(value) {
    return value == null ? '-' : Number(value).toFixed(1);
}

function fmti(value) {
    return value == null ? '-' : String(value);
}

loadForecast();