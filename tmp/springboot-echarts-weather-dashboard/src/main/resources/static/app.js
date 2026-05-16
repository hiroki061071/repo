const preset = document.getElementById('preset');
const searchKeyword = document.getElementById('searchKeyword');
const searchBtn = document.getElementById('searchBtn');
const latInput = document.getElementById('lat');
const lonInput = document.getElementById('lon');
const timezoneInput = document.getElementById('timezone');
const loadBtn = document.getElementById('loadBtn');
const locationTitle = document.getElementById('locationTitle');
const metaText = document.getElementById('metaText');
const fetchedAtText = document.getElementById('fetchedAtText');
const tableBody = document.querySelector('#forecastTable tbody');

const tempChart = echarts.init(document.getElementById('tempChart'));
const precipChart = echarts.init(document.getElementById('precipChart'));
const windChart = echarts.init(document.getElementById('windChart'));

const searchCandidates = [
    { keyword: '鹿児島', lat: 31.5966, lon: 130.5571, name: '鹿児島' },
    { keyword: '京都', lat: 35.0116, lon: 135.7681, name: '京都' },
    { keyword: '横浜', lat: 35.4437, lon: 139.6380, name: '横浜' },
    { keyword: '神戸', lat: 34.6901, lon: 135.1955, name: '神戸' },
    { keyword: '熊本', lat: 32.8031, lon: 130.7079, name: '熊本' },
    { keyword: '長崎', lat: 32.7503, lon: 129.8777, name: '長崎' },
    { keyword: '宮崎', lat: 31.9111, lon: 131.4239, name: '宮崎' },
    { keyword: '大分', lat: 33.2396, lon: 131.6093, name: '大分' },
    { keyword: '松江', lat: 35.4723, lon: 133.0505, name: '松江' },
    { keyword: '富山', lat: 36.6953, lon: 137.2113, name: '富山' },
    { keyword: '金沢', lat: 36.5613, lon: 136.6562, name: '金沢' },
    { keyword: '青森', lat: 40.8244, lon: 140.7400, name: '青森' },
    { keyword: '盛岡', lat: 39.7036, lon: 141.1527, name: '盛岡' },
    { keyword: '秋田', lat: 39.7186, lon: 140.1024, name: '秋田' },
    { keyword: '山形', lat: 38.2554, lon: 140.3396, name: '山形' },
    { keyword: '福島', lat: 37.7608, lon: 140.4747, name: '福島' },
    { keyword: '高知', lat: 33.5597, lon: 133.5311, name: '高知' },
    { keyword: '徳島', lat: 34.0658, lon: 134.5593, name: '徳島' },
    { keyword: '松山', lat: 33.8392, lon: 132.7657, name: '松山' },
    { keyword: '岡山', lat: 34.6551, lon: 133.9195, name: '岡山' },
    { keyword: '静岡', lat: 34.9756, lon: 138.3828, name: '静岡' },
    { keyword: '浜松', lat: 34.7108, lon: 137.7261, name: '浜松' },
    { keyword: '千葉', lat: 35.6074, lon: 140.1065, name: '千葉' },
    { keyword: 'さいたま', lat: 35.8617, lon: 139.6455, name: 'さいたま' },
    { keyword: '宇都宮', lat: 36.5551, lon: 139.8828, name: '宇都宮' },
    { keyword: '前橋', lat: 36.3906, lon: 139.0608, name: '前橋' },
    { keyword: '水戸', lat: 36.3659, lon: 140.4712, name: '水戸' },
    { keyword: '長野', lat: 36.6513, lon: 138.1810, name: '長野' },
    { keyword: '甲府', lat: 35.6639, lon: 138.5684, name: '甲府' },
    { keyword: '和歌山', lat: 34.2260, lon: 135.1675, name: '和歌山' },
    { keyword: '奈良', lat: 34.6851, lon: 135.8048, name: '奈良' },
    { keyword: 'Yokohama', lat: 35.4437, lon: 139.6380, name: '横浜' },
    { keyword: 'Kyoto', lat: 35.0116, lon: 135.7681, name: '京都' },
    { keyword: 'Kagoshima', lat: 31.5966, lon: 130.5571, name: '鹿児島' }
];

preset.addEventListener('change', () => {
    const [lat, lon, name] = preset.value.split(',');
    latInput.value = lat;
    lonInput.value = lon;
    locationTitle.textContent = name;
});

searchBtn.addEventListener('click', applySearchCandidate);
searchKeyword.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        applySearchCandidate();
    }
});

loadBtn.addEventListener('click', loadForecast);

window.addEventListener('resize', () => {
    tempChart.resize();
    precipChart.resize();
    windChart.resize();
});

function applySearchCandidate() {
    const keyword = (searchKeyword.value || '').trim().toLowerCase();
    if (!keyword) {
        alert('地点検索キーワードを入力してください。');
        return;
    }

    const found = searchCandidates.find(c =>
        c.keyword.toLowerCase().includes(keyword) || keyword.includes(c.keyword.toLowerCase())
    );

    if (!found) {
        alert('候補にありません。プリセットを使うか、緯度経度を直接入力してください。');
        return;
    }

    latInput.value = found.lat;
    lonInput.value = found.lon;
    locationTitle.textContent = found.name;
    metaText.textContent = `検索候補を反映しました: ${found.name}`;
}

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
    const fetchedAt = formatNow();

    metaText.textContent =
        `緯度 ${data.latitude}, 経度 ${data.longitude}, タイムゾーン ${data.timezone}, 取得日数 ${days.length}日`;
    fetchedAtText.textContent = `取得時刻: ${fetchedAt}`;

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
        title: { text: '7日間の最高・最低気温' },
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
        legend: { data: ['最高気温', '最低気温'] },
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value', name: '気温(℃)' },
        series: [
            { name: '最高気温', type: 'line', smooth: true, data: tempMax },
            { name: '最低気温', type: 'line', smooth: true, data: tempMin }
        ]
    });
}

function renderPrecipChart(days) {
    const dates = days.map(d => d.date);
    const precip = days.map(d => d.precipProbabilityMax);
    const weatherLabels = days.map(d => getWeatherInfo(d.weatherCode).label);

    precipChart.setOption({
        title: { text: '7日間の最大降水確率' },
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
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value', name: '降水確率(%)', min: 0, max: 100 },
        series: [
            { name: '降水確率', type: 'bar', data: precip }
        ]
    });
}

function renderWindChart(days) {
    const dates = days.map(d => d.date);
    const wind = days.map(d => d.windSpeedMax);
    const code = days.map(d => d.weatherCode);

    windChart.setOption({
        title: { text: '7日間の最大風速 + 天気コード' },
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
        legend: { data: ['最大風速', '天気コード'] },
        xAxis: { type: 'category', data: dates },
        yAxis: [
            { type: 'value', name: '最大風速(m/s)' },
            { type: 'value', name: '天気コード' }
        ],
        series: [
            { name: '最大風速', type: 'line', smooth: true, yAxisIndex: 0, data: wind },
            { name: '天気コード', type: 'line', smooth: false, yAxisIndex: 1, data: code }
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

function formatNow() {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    const hh = String(now.getHours()).padStart(2, '0');
    const mi = String(now.getMinutes()).padStart(2, '0');
    const ss = String(now.getSeconds()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`;
}

function fmt(value) {
    return value == null ? '-' : Number(value).toFixed(1);
}

function fmti(value) {
    return value == null ? '-' : String(value);
}

loadForecast();