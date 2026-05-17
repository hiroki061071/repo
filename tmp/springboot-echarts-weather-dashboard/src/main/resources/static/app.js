const preset = document.getElementById('preset');
const searchKeyword = document.getElementById('searchKeyword');
const searchBtn = document.getElementById('searchBtn');
const searchResults = document.getElementById('searchResults');

const latInput = document.getElementById('lat');
const lonInput = document.getElementById('lon');
const timezoneInput = document.getElementById('timezone');

const loadBtn = document.getElementById('loadBtn');
const favoriteBtn = document.getElementById('favoriteBtn');
const favoriteSelect = document.getElementById('favoriteSelect');
const favoriteLoadBtn = document.getElementById('favoriteLoadBtn');

const locationTitle = document.getElementById('locationTitle');
const metaText = document.getElementById('metaText');
const fetchedAtText = document.getElementById('fetchedAtText');
const apiFetchedAtText = document.getElementById('apiFetchedAtText');

const tableBody = document.querySelector('#forecastTable tbody');

const tempChart = echarts.init(document.getElementById('tempChart'));
const precipChart = echarts.init(document.getElementById('precipChart'));
const windChart = echarts.init(document.getElementById('windChart'));

const FAVORITE_KEY = 'weather-dashboard-favorites';

preset.addEventListener('change', () => {
    const [lat, lon, name] = preset.value.split(',');
    latInput.value = lat;
    lonInput.value = lon;
    locationTitle.textContent = name;
});

searchBtn.addEventListener('click', searchGeocode);
searchKeyword.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        searchGeocode();
    }
});

loadBtn.addEventListener('click', loadForecast);
favoriteBtn.addEventListener('click', saveFavorite);
favoriteLoadBtn.addEventListener('click', loadFavorite);

window.addEventListener('resize', () => {
    tempChart.resize();
    precipChart.resize();
    windChart.resize();
});

async function searchGeocode() {
    const keyword = (searchKeyword.value || '').trim();
    if (!keyword) {
        alert('地名を入力してください。');
        return;
    }

    searchResults.innerHTML = '検索中...';

    try {
        const url = `/api/geocode?name=${encodeURIComponent(keyword)}`;
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        const list = await res.json();
        renderSearchResults(list);

    } catch (err) {
        console.error(err);
        searchResults.innerHTML = `検索失敗: ${err.message}`;
    }
}

function renderSearchResults(list) {
    searchResults.innerHTML = '';

    if (!list || list.length === 0) {
        searchResults.innerHTML = '候補が見つかりませんでした。';
        return;
    }

    for (const item of list) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'result-item';
        btn.textContent = `${item.name} (${item.country}) [${item.latitude}, ${item.longitude}]`;

        btn.addEventListener('click', () => {
            latInput.value = item.latitude;
            lonInput.value = item.longitude;
            locationTitle.textContent = item.name;
            metaText.textContent = `検索候補を反映しました: ${item.name} (${item.country})`;
        });

        searchResults.appendChild(btn);
    }
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

    metaText.textContent =
        `緯度 ${data.latitude}, 経度 ${data.longitude}, タイムゾーン ${data.timezone}, 取得日数 ${days.length}日`;
    fetchedAtText.textContent = `取得時刻: ${formatNow()}`;
    apiFetchedAtText.textContent = `API応答時刻: ${data.fetchedAt ?? '-'}`;

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
        `;

        tableBody.appendChild(tr);
    }
}

function renderTempChart(days) {
    const dates = days.map(d => d.date);
    const tempMax = days.map(d => d.tempMax);
    const tempMin = days.map(d => d.tempMin);
    const codes = days.map(d => d.weatherCode);
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
                    `天気コード: ${fmti(codes[i])}`,
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
    const codes = days.map(d => d.weatherCode);
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
                    `天気コード: ${fmti(codes[i])}`,
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
        title: { text: '7日間の最大風速' },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                const i = params[0].dataIndex;
                const weather = getWeatherInfo(code[i]);

                return [
                    `<b>${dates[i]}</b>`,
                    `${weather.icon} ${weather.label}`,
                    `天気コード: ${fmti(code[i])}`,
                    `最大風速: ${fmt(wind[i])} m/s`
                ].join('<br>');
            }
        },
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value', name: '最大風速(m/s)' },
        series: [
            { name: '最大風速', type: 'line', smooth: true, data: wind }
        ]
    });
}

function saveFavorite() {
    const name = locationTitle.textContent || '無名地点';
    const lat = latInput.value;
    const lon = lonInput.value;

    if (!lat || !lon) {
        alert('緯度経度がありません。');
        return;
    }

    const favorites = loadFavorites();
    const exists = favorites.some(f => f.name === name && String(f.lat) === String(lat) && String(f.lon) === String(lon));
    if (!exists) {
        favorites.push({ name, lat, lon });
        localStorage.setItem(FAVORITE_KEY, JSON.stringify(favorites));
    }

    refreshFavoriteSelect();
    alert(`お気に入りに保存しました: ${name}`);
}

function loadFavorite() {
    const raw = favoriteSelect.value;
    if (!raw) {
        return;
    }

    const item = JSON.parse(raw);
    latInput.value = item.lat;
    lonInput.value = item.lon;
    locationTitle.textContent = item.name;
    metaText.textContent = `お気に入りを反映しました: ${item.name}`;
}

function loadFavorites() {
    try {
        return JSON.parse(localStorage.getItem(FAVORITE_KEY) || '[]');
    } catch {
        return [];
    }
}

function refreshFavoriteSelect() {
    const favorites = loadFavorites();

    favoriteSelect.innerHTML = '<option value="">選択してください</option>';
    for (const f of favorites) {
        const option = document.createElement('option');
        option.value = JSON.stringify(f);
        option.textContent = `${f.name} (${f.lat}, ${f.lon})`;
        favoriteSelect.appendChild(option);
    }
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

refreshFavoriteSelect();
loadForecast();