using HelixToolkit.Wpf.SharpDX;
using SharpDX;
using SharpDX.Direct3D11;
using System.IO;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Media3D = System.Windows.Media.Media3D;
using WxAid3DSharp.Models;
using WxAid3DSharp.Services;
using System.Windows.Media;

namespace WxAid3DSharp;

public partial class MainWindow : Window
{
    private readonly DispatcherTimer _rotationTimer = new();
    private readonly DispatcherTimer _timeAnimationTimer = new();
    private double _angle;
    private bool _autoRotate = true;
    private bool _isPlaying;
    private WeatherDisplayMode _displayMode = WeatherDisplayMode.Temperature;
    private TerrainQuality _terrainQuality = TerrainQuality.Medium;

    private List<AmedasStation> _allRecords = new();
    private List<AmedasStation> _stations = new();
    private List<WeatherGridPoint> _allWeatherGridRecords = new();
    private List<WeatherGridPoint> _currentWeatherGrid = new();
    private List<WindGridPoint> _allWindGridRecords = new();
    private List<WindGridPoint> _currentWindGrid = new();
    private List<DateTime> _times = new();
    private DateTime? _currentTime;

    public MainWindow()
    {
        InitializeComponent();

        // SharpDX版HelixToolkitではEffectsManagerを明示しないと、
        // 3Dモデルが真っ黒／未表示になることがあります。
        View.EffectsManager = new DefaultEffectsManager();

        SetCamera(-120, -260, 160, 120, 260, -130);

        CreateSea();
        CreateMapImagePlane();
        //TryCreateTerrain();
        LoadSampleData();
        CreateStations();
        UpdateDisplayInfo();

        // 初期表示の安定性を優先して自動回転はOFF。
        // 必要なら「回転ON/OFF」ボタンで開始できます。
        // StartAutoRotation();

        InitializeTimeAnimation();
    }

    private void LoadSampleData()
    {
        DateTime t = DateTime.Today.AddHours(9);
        _stations = new List<AmedasStation>
        {
            new() { Time = t, Name = "札幌", Latitude = 43.0642, Longitude = 141.3469, Temperature = 8.5, WindSpeed=3.2, WindDirection=270 },
            new() { Time = t, Name = "東京", Latitude = 35.6895, Longitude = 139.6917, Temperature = 18.6, Precipitation=1.0, WindSpeed=4.0, WindDirection=270 },
            new() { Time = t, Name = "大阪", Latitude = 34.6937, Longitude = 135.5023, Temperature = 20.0, WindSpeed=3.5, WindDirection=250 },
            new() { Time = t, Name = "福岡", Latitude = 33.5902, Longitude = 130.4017, Temperature = 20.4, WindSpeed=2.8, WindDirection=240 },
            new() { Time = t, Name = "那覇", Latitude = 26.2124, Longitude = 127.6792, Temperature = 25.0, WindSpeed=5.1, WindDirection=220 }
        };
        _allRecords = _stations.ToList();
        _times = _allRecords
            .Select(x => x.Time)
            .Distinct()
            .OrderBy(x => x)
            .ToList();

        TimeSlider.Minimum = 0;
        TimeSlider.Maximum = Math.Max(0, _times.Count - 1);
        TimeSlider.Value = 0;
        _currentTime = t;
        TimeText.Text = t.ToString("yyyy/MM/dd HH:mm");
    }

    private void TryCreateTerrain()
    {
        try
        {
            if (File.Exists("Assets/japan_dem.png") && File.Exists("Assets/japan_map.png"))
                CreateTerrainFromFiles("Assets/japan_dem.png", "Assets/japan_map.png");
            else
                CreatePseudoTerrain();
        }
        catch
        {
            CreatePseudoTerrain();
        }
    }

    private void CreateSea()
    {
        var builder = new MeshBuilder();
        builder.AddQuad(new Vector3(-130, -150, 0), new Vector3(130, -150, 0), new Vector3(130, 150, 0), new Vector3(-130, 150, 0));
        SeaModel.Geometry = builder.ToMeshGeometry3D();
        SeaModel.Material = new PhongMaterial { DiffuseColor = new Color4(0.04f, 0.12f, 0.32f, 1), AmbientColor = new Color4(0.02f, 0.06f, 0.15f, 1) };
        SeaModel.IsHitTestVisible = false;
    }

    private void CreateMapImagePlane()
    {
        string mapPath = Path.Combine(
            AppDomain.CurrentDomain.BaseDirectory,
            "Assets",
            "japan_map.png");

        if (!File.Exists(mapPath))
        {
            MessageBox.Show("地図画像なし:\n" + mapPath);
            return;
        }

        float width = 300f;
        float height = 300f;
        float z = 3.0f;   // 最前面

        var builder = new MeshBuilder();

        builder.AddQuad(
            new Vector3(-width / 2, -height / 2, z),
            new Vector3(width / 2, -height / 2, z),
            new Vector3(width / 2, height / 2, z),
            new Vector3(-width / 2, height / 2, z));

        MapImagePlaneModel.Geometry = builder.ToMeshGeometry3D();

        // ▼ 左右反転だけ適用（真っ暗化しにくい）
        MapImagePlaneModel.Transform =
            new Media3D.ScaleTransform3D(-1, 1, 1);

        MapImagePlaneModel.Material = new PhongMaterial
        {
            DiffuseMap = TextureModel.Create(mapPath),
            DiffuseColor = new Color4(1f, 1f, 1f, 1f),
            AmbientColor = new Color4(1f, 1f, 1f, 1f),
            SpecularColor = new Color4(0f, 0f, 0f, 0f)
        };

        MapImagePlaneModel.IsTransparent = false;
        MapImagePlaneModel.CullMode = CullMode.None;
        MapImagePlaneModel.IsHitTestVisible = false;

        // ▼ 地図を180度回転
        MapImagePlaneModel.Transform =
            new Media3D.RotateTransform3D(
                new Media3D.AxisAngleRotation3D(
                    new Media3D.Vector3D(0, 0, 1),
                    180));
    }

    private int GetTerrainStep() => _terrainQuality switch { TerrainQuality.Low => 8, TerrainQuality.High => 2, _ => 4 };

    private void CreateTerrainFromFiles(string demPath, string mapPath)
    {
        var dem = new BitmapImage(
            new Uri(demPath, UriKind.RelativeOrAbsolute));
        CreateTerrainFromBitmaps(dem, mapPath);
    }

    private void CreatePseudoTerrain()
    {
        int width = 80, height = 100, step = 8;
        double mapWidth = 260, mapHeight = 300, heightScale = 55;

        var positions = new Vector3Collection();
        var tex = new Vector2Collection();
        var indices = new IntCollection();

        int cols = width / step;
        int rows = height / step;

        for (int row = 0; row < rows; row++)
        {
            for (int col = 0; col < cols; col++)
            {
                double nx = (double)(col * step) / (width - 1);
                double ny = (double)(row * step) / (height - 1);

                double z = Math.Max(
                    0,
                    Math.Sin(nx * Math.PI * 8) *
                    Math.Sin(ny * Math.PI * 7) * 0.18
                    +
                    Math.Exp(-Math.Pow(nx - .55, 2) * 45) *
                    Math.Exp(-Math.Pow(ny - .52, 2) * 28));

                positions.Add(new Vector3(
                    (float)((nx - .5) * mapWidth),
                    (float)((.5 - ny) * mapHeight),
                    (float)(z * heightScale + .3)));

                // 地図テクスチャ用UV座標
                tex.Add(new Vector2((float)nx, (float)ny));
            }
        }

        AddGridIndices(indices, cols, rows);

        TerrainModel.Geometry = new MeshGeometry3D
        {
            Positions = positions,
            TextureCoordinates = tex,
            Indices = indices
        };

        string mapPath = Path.Combine(
            AppDomain.CurrentDomain.BaseDirectory,
            "Assets",
            "japan_map.png");

        if (File.Exists(mapPath))
        {
            TerrainModel.Material = new PhongMaterial
            {
                DiffuseMap = TextureModel.Create(mapPath),
                DiffuseColor = new Color4(1f, 1f, 1f, 1f),
                AmbientColor = new Color4(1f, 1f, 1f, 1f),
                SpecularColor = new Color4(.03f, .03f, .03f, 1f)
            };
        }
        else
        {
            TerrainModel.Material = new PhongMaterial
            {
                DiffuseColor = new Color4(.35f, .65f, .36f, 1),
                AmbientColor = new Color4(.18f, .28f, .18f, 1)
            };
        }

        TerrainModel.IsHitTestVisible = false;
    }

    private void CreateTerrainFromBitmaps(BitmapSource heightmap, string texturePath)
    {
        int width = heightmap.PixelWidth, height = heightmap.PixelHeight, step = GetTerrainStep();
        double mapWidth = 260.0, mapHeight = 300.0, heightScale = 80.0;
        var positions = new Vector3Collection();
        var tex = new Vector2Collection();
        var indices = new IntCollection();
        int cols = width / step, rows = height / step;
        for (int row = 0; row < rows; row++)
        for (int col = 0; col < cols; col++)
        {
            int x = Math.Min(col * step, width - 1), y = Math.Min(row * step, height - 1);
            positions.Add(CreatePointFromHeightmap(heightmap, x, y, width, height, mapWidth, mapHeight, heightScale));
            tex.Add(new Vector2((float)x / (width - 1), (float)y / (height - 1)));
        }
        AddGridIndices(indices, cols, rows);
        TerrainModel.Geometry = new MeshGeometry3D { Positions = positions, TextureCoordinates = tex, Indices = indices };
        TerrainModel.Material = new PhongMaterial
        {
            DiffuseMap = TextureModel.Create(texturePath),
            DiffuseColor = new Color4(1f, 1f, 1f, 1f),
            AmbientColor = new Color4(1f, 1f, 1f, 1f),
            SpecularColor = new Color4(.03f, .03f, .03f, 1f)
        };
        TerrainModel.IsHitTestVisible = false;
    }

    private static void AddGridIndices(IntCollection indices, int cols, int rows)
    {
        for (int row = 0; row < rows - 1; row++)
        for (int col = 0; col < cols - 1; col++)
        {
            int i0 = row * cols + col, i1 = i0 + 1, i3 = (row + 1) * cols + col, i2 = i3 + 1;
            indices.Add(i0); indices.Add(i1); indices.Add(i2); indices.Add(i0); indices.Add(i2); indices.Add(i3);
        }
    }

    private Vector3 CreatePointFromHeightmap(BitmapSource bitmap, int x, int y, int width, int height, double mapWidth, double mapHeight, double heightScale)
    {
        double nx = (double)x / (width - 1), ny = (double)y / (height - 1);
        double z = GetHeightValue(bitmap, x, y) * heightScale + 0.3;
        return new Vector3((float)((nx - .5) * mapWidth), (float)((.5 - ny) * mapHeight), (float)z);
    }

    private static double GetHeightValue(BitmapSource bitmap, int x, int y)
    {
        int bpp = (bitmap.Format.BitsPerPixel + 7) / 8;
        byte[] pixel = new byte[Math.Max(1, bpp)];
        bitmap.CopyPixels(new Int32Rect(x, y, 1, 1), pixel, pixel.Length, 0);
        byte r = pixel.Length > 2 ? pixel[2] : pixel[0], g = pixel.Length > 1 ? pixel[1] : pixel[0], b = pixel[0];
        double brightness = (r + g + b) / 3.0 / 255.0;
        const double seaThreshold = 0.02;
        if (brightness <= seaThreshold) return 0;
        return Math.Pow((brightness - seaThreshold) / (1.0 - seaThreshold), 1.8);
    }

    private Vector3 LonLatToPoint(double lon, double lat, double z = 3.0)
    {
        const double minLon = 118.125;
        const double maxLon = 146.25;

        const double northLat = 48.922499;
        const double southLat = 21.943046;

        double mapWidth = 300.0;
        double mapHeight = 300.0;

        double xNorm = (lon - minLon) / (maxLon - minLon);

        double yNorth = MercatorY(northLat);
        double ySouth = MercatorY(southLat);
        double yLat = MercatorY(lat);

        double yNorm = (yLat - yNorth) / (ySouth - yNorth);

        double x = (xNorm - 0.5) * mapWidth;
        double y = (0.5 - yNorm) * mapHeight;

        return new Vector3((float)x, (float)y, (float)z);
    }

    private double MercatorY(double lat)
    {
        double rad = lat * Math.PI / 180.0;
        return Math.Log(Math.Tan(Math.PI / 4.0 + rad / 2.0));
    }

    private void CreateStations()
    {
        StationGroup.Children.Clear(); LabelGroup.Children.Clear();
        foreach (var s in _stations)
        {
            if (_displayMode == WeatherDisplayMode.WindVector) { CreateWindVector(s); continue; }
            var basePoint = LonLatToPoint(s.Longitude, s.Latitude, 4);
            double value = GetDisplayValue(s), h = GetColumnHeight(value);
            var top = new Vector3(basePoint.X, basePoint.Y, basePoint.Z + (float)h);
            var builder = new MeshBuilder(); builder.AddCylinder(basePoint, top, 1.2, 24); builder.AddSphere(top, 2.0);
            var color = GetDisplayColor(value);
            StationGroup.Children.Add(new MeshGeometryModel3D
            {
                Geometry = builder.ToMeshGeometry3D(),
                Material = new PhongMaterial
                {
                    DiffuseColor = color,
                    AmbientColor = color,
                    SpecularColor = new Color4(.25f, .25f, .25f, 1)
                },
                IsHitTestVisible = false
            });
            CreateStationLabel(s.Name, top);
        }
    }

    private void CreateWindVector(AmedasStation s)
    {
        var start = LonLatToPoint(s.Longitude, s.Latitude, 8); start.Z += 2;
        double len = Math.Max(4, s.WindSpeed * 4), rad = s.WindDirection * Math.PI / 180.0 + Math.PI;
        var end = new Vector3(start.X + (float)(Math.Sin(rad) * len), start.Y + (float)(Math.Cos(rad) * len), start.Z);
        var builder = new MeshBuilder(); builder.AddArrow(start, end, 1.0, 3.0, 18);
        var color = GetWindSpeedColor(s.WindSpeed);
        StationGroup.Children.Add(new MeshGeometryModel3D
        {
            Geometry = builder.ToMeshGeometry3D(),
            Material = new PhongMaterial
            {
                DiffuseColor = color,
                AmbientColor = color
            },
            IsHitTestVisible = false
        });
        CreateStationLabel(s.Name, end);
    }

    private void CreateStationLabel(string text, Vector3 position)
    {
        //LabelGroup.Children.Add(new BillboardTextModel3D { TextInfo = new TextInfo { Text = text, Origin = new Vector3(position.X, position.Y, position.Z + 5), Foreground = new Color4(1, 1, 1, 1), Background = new Color4(0, 0, 0, .6f), Scale = 10f } });
    }

    private double GetDisplayValue(AmedasStation s) => _displayMode switch { WeatherDisplayMode.Precipitation => s.Precipitation, WeatherDisplayMode.WindSpeed => s.WindSpeed, _ => s.Temperature };
    private double GetColumnHeight(double v) => _displayMode switch { WeatherDisplayMode.Precipitation => Math.Max(.5, v * 3), WeatherDisplayMode.WindSpeed => Math.Max(1, v * 2), _ => Math.Max(1, v * 1.2) };
    private Color4 GetDisplayColor(double v) => _displayMode switch { WeatherDisplayMode.Precipitation => GetPrecipitationColor(v), WeatherDisplayMode.WindSpeed => GetWindSpeedColor(v), _ => GetTemperatureColor(v) };
    private static Color4 GetTemperatureColor(double t) => t < 5 ? new Color4(.1f, .3f, 1, 1) : t < 15 ? new Color4(.1f, .8f, 1, 1) : t < 25 ? new Color4(1, .8f, .1f, 1) : new Color4(1, .1f, .1f, 1);
    private static Color4 GetPrecipitationColor(double r) => r <= 0 ? new Color4(.7f, .7f, .7f, 1) : r < 1 ? new Color4(.3f, .8f, 1, 1) : r < 5 ? new Color4(.1f, .4f, 1, 1) : r < 20 ? new Color4(1, .8f, .1f, 1) : new Color4(1, .1f, .1f, 1);
    private static Color4 GetWindSpeedColor(double w) => w < 2 ? new Color4(.6f, .8f, 1, 1) : w < 5 ? new Color4(.2f, 1, .3f, 1) : w < 10 ? new Color4(1, .8f, .1f, 1) : new Color4(1, .1f, .1f, 1);
    private static Color4 WithAlpha(Color4 c, float a) => new(c.Red, c.Green, c.Blue, a);

    private void CreateWindGridFromCurrentData()
    {
        WindGridGroup.Children.Clear();
        foreach (var p in _currentWindGrid)
        {
            var start = LonLatToPoint(p.Longitude, p.Latitude, 10); start.Z += 2;
            double len = Math.Max(3, p.WindSpeed * 2.5), rad = p.WindDirection * Math.PI / 180.0 + Math.PI;
            var end = new Vector3(start.X + (float)(Math.Sin(rad) * len), start.Y + (float)(Math.Cos(rad) * len), start.Z);
            var builder = new MeshBuilder(); builder.AddArrow(start, end, .6, 1.8, 12);
            var color = GetWindSpeedColor(p.WindSpeed);
            WindGridGroup.Children.Add(new MeshGeometryModel3D
            {
                Geometry = builder.ToMeshGeometry3D(),
                Material = new PhongMaterial
                {
                    DiffuseColor = color,
                    AmbientColor = color
                },
                IsHitTestVisible = false
            });
        }
    }

    private void CreateWeatherGridSurface(List<WeatherGridPoint> grid)
    {
        WeatherGridGroup.Children.Clear();
        var lats = grid.Select(p => p.Latitude).Distinct().OrderBy(x => x).ToList();
        var lons = grid.Select(p => p.Longitude).Distinct().OrderBy(x => x).ToList();
        var dict = grid.ToDictionary(p => (p.Latitude, p.Longitude), p => p);
        for (int y = 0; y < lats.Count - 1; y++)
        for (int x = 0; x < lons.Count - 1; x++)
        {
            if (!dict.TryGetValue((lats[y], lons[x]), out var p00) || !dict.TryGetValue((lats[y], lons[x+1]), out var p10) || !dict.TryGetValue((lats[y+1], lons[x]), out var p01) || !dict.TryGetValue((lats[y+1], lons[x+1]), out var p11)) continue;
            double value = _displayMode == WeatherDisplayMode.TemperatureGrid ? (p00.Temperature+p10.Temperature+p01.Temperature+p11.Temperature)/4.0 : (p00.Precipitation+p10.Precipitation+p01.Precipitation+p11.Precipitation)/4.0;
            var builder = new MeshBuilder(); builder.AddQuad(LonLatToPoint(p00.Longitude,p00.Latitude,16), LonLatToPoint(p10.Longitude,p10.Latitude,16), LonLatToPoint(p11.Longitude,p11.Latitude,16), LonLatToPoint(p01.Longitude,p01.Latitude,16));
            var color = WithAlpha(_displayMode == WeatherDisplayMode.TemperatureGrid ? GetTemperatureColor(value) : GetPrecipitationColor(value), .55f);
            WeatherGridGroup.Children.Add(new MeshGeometryModel3D
            {
                Geometry = builder.ToMeshGeometry3D(),
                Material = new PhongMaterial
                {
                    DiffuseColor = color,
                    AmbientColor = color,
                    SpecularColor = new Color4(.05f, .05f, .05f, .3f)
                },
                IsTransparent = true,
                CullMode = CullMode.None,
                IsHitTestVisible = false
            });
        }
    }

    //private void CreateContourLines(List<WeatherGridPoint> grid)
    //{
    //    ContourGroup.Children.Clear();
    //    if (grid.Count == 0) return;
    //    var lats = grid.Select(p => p.Latitude).Distinct().OrderBy(x => x).ToList();
    //    var lons = grid.Select(p => p.Longitude).Distinct().OrderBy(x => x).ToList();
    //    var dict = grid.ToDictionary(p => (p.Latitude, p.Longitude), p => p);
    //    double[] levels = _displayMode == WeatherDisplayMode.TemperatureGrid ? new double[] {0,5,10,15,20,25,30} : new double[] {1,5,10,20,30,50};
    //    foreach (double level in levels)
    //    {
    //        var lb = new LineBuilder();
    //        for (int y=0;y<lats.Count-1;y++) for(int x=0;x<lons.Count-1;x++)
    //            if (dict.TryGetValue((lats[y], lons[x]), out var p00) && dict.TryGetValue((lats[y], lons[x+1]), out var p10) && dict.TryGetValue((lats[y+1], lons[x+1]), out var p11) && dict.TryGetValue((lats[y+1], lons[x]), out var p01)) AddContourForCell(lb,p00,p10,p11,p01,level);
    //        ContourGroup.Children.Add(new LineGeometryModel3D { Geometry = lb.ToLineGeometry3D(), Color = System.Windows.Media.Colors.White, Thickness = 1.2, IsHitTestVisible = false });
    //    }
    //}

    private void CreateContourLines(List<WeatherGridPoint> grid)
    {
        return;
    }

    private void AddContourForCell(LineBuilder b, WeatherGridPoint p00, WeatherGridPoint p10, WeatherGridPoint p11, WeatherGridPoint p01, double level)
    {
        var pts = new List<Vector3>(); CheckEdge(pts,p00,p10,level); CheckEdge(pts,p10,p11,level); CheckEdge(pts,p11,p01,level); CheckEdge(pts,p01,p00,level);
        if (pts.Count == 2) b.AddLine(pts[0], pts[1]); else if (pts.Count == 4) { b.AddLine(pts[0], pts[1]); b.AddLine(pts[2], pts[3]); }
    }
    private void CheckEdge(List<Vector3> pts, WeatherGridPoint a, WeatherGridPoint b, double level)
    {
        double va=GetGridValue(a), vb=GetGridValue(b); if(level<Math.Min(va,vb)||level>Math.Max(va,vb)||Math.Abs(va-vb)<1e-4) return;
        double t=(level-va)/(vb-va); pts.Add(LonLatToPoint(a.Longitude+(b.Longitude-a.Longitude)*t, a.Latitude+(b.Latitude-a.Latitude)*t, 18));
    }
    private double GetGridValue(WeatherGridPoint p) => _displayMode == WeatherDisplayMode.PrecipitationGrid ? p.Precipitation : p.Temperature;

    //private void CreateStreamLines(List<WindGridPoint> windGrid)
    //{
    //    StreamLineGroup.Children.Clear(); if (windGrid.Count == 0) return;
    //    double minLon=windGrid.Min(p=>p.Longitude), maxLon=windGrid.Max(p=>p.Longitude), minLat=windGrid.Min(p=>p.Latitude), maxLat=windGrid.Max(p=>p.Latitude);
    //    for(double lat=minLat; lat<=maxLat; lat+=2.0) for(double lon=minLon; lon<=maxLon; lon+=2.0)
    //    {
    //        var line=TraceStreamLine(windGrid,lon,lat,25,.15); if(line.Count<2) continue;
    //        var lb=new LineBuilder(); for(int i=0;i<line.Count-1;i++) lb.AddLine(line[i],line[i+1]);
    //        StreamLineGroup.Children.Add(new LineGeometryModel3D { Geometry=lb.ToLineGeometry3D(), Color = System.Windows.Media.Colors.White, Thickness=1.3, IsHitTestVisible=false });
    //    }
    //}

    private void CreateStreamLines(List<WindGridPoint> windGrid)
    {
        return;
    }

    private List<Vector3> TraceStreamLine(List<WindGridPoint> grid,double lon,double lat,int steps,double dt)
    {
        var res=new List<Vector3>();
        for(int i=0;i<steps;i++){ var w=grid.OrderBy(p=>Math.Pow(p.Longitude-lon,2)+Math.Pow(p.Latitude-lat,2)).FirstOrDefault(); if(w==null) break; res.Add(LonLatToPoint(lon,lat,20)); lon+=w.U*dt; lat+=w.V*dt; }
        return res;
    }

    private List<WeatherGridPoint> ConvertTemperatureCsv(List<WgribCsvRecord> recs) => recs.Where(r=>r.Field.Contains("TMP",StringComparison.OrdinalIgnoreCase)).Select(r=>new WeatherGridPoint{Time=r.Time1, Latitude=r.Latitude, Longitude=r.Longitude, Temperature=r.Value-273.15}).ToList();
    private List<WindGridPoint> ConvertWindCsv(List<WgribCsvRecord> uRecords, List<WgribCsvRecord> vRecords)
    {
        var joined = from u in uRecords.Where(r=>r.Field.Contains("UGRD",StringComparison.OrdinalIgnoreCase)) join v in vRecords.Where(r=>r.Field.Contains("VGRD",StringComparison.OrdinalIgnoreCase)) on new {u.Time1,u.Latitude,u.Longitude} equals new {v.Time1,v.Latitude,v.Longitude} select new {u,v};
        return joined.Select(x=>{ double u=x.u.Value, v=x.v.Value, speed=Math.Sqrt(u*u+v*v), dir=(270.0-Math.Atan2(v,u)*180.0/Math.PI)%360.0; if(dir<0)dir+=360; return new WindGridPoint{Time=x.u.Time1,Latitude=x.u.Latitude,Longitude=x.u.Longitude,U=u,V=v,WindSpeed=speed,WindDirection=dir}; }).ToList();
    }

    private void SetCurrentTimeByIndex(int index)
    {
        if (_times.Count == 0) return; index = Math.Clamp(index, 0, _times.Count - 1); _currentTime = _times[index]; TimeText.Text = _currentTime.Value.ToString("yyyy/MM/dd HH:mm");
        StationGroup.Children.Clear(); LabelGroup.Children.Clear(); WindGridGroup.Children.Clear(); WeatherGridGroup.Children.Clear(); ContourGroup.Children.Clear(); StreamLineGroup.Children.Clear();
        if (_displayMode == WeatherDisplayMode.WindGrid || _displayMode == WeatherDisplayMode.StreamLine)
        { _currentWindGrid = _allWindGridRecords.Where(x=>x.Time==_currentTime.Value).ToList(); if(_displayMode==WeatherDisplayMode.StreamLine) CreateStreamLines(_currentWindGrid); else CreateWindGridFromCurrentData(); }
        else if (_displayMode == WeatherDisplayMode.TemperatureGrid || _displayMode == WeatherDisplayMode.PrecipitationGrid)
        { _currentWeatherGrid = _allWeatherGridRecords.Where(x=>x.Time==_currentTime.Value).ToList(); CreateWeatherGridSurface(_currentWeatherGrid); CreateContourLines(_currentWeatherGrid); }
        else
        { _stations = _allRecords.Where(x=>x.Time==_currentTime.Value).ToList(); CreateStations(); }
        UpdateDisplayInfo();
    }

    private void StartAutoRotation(){ _rotationTimer.Interval=TimeSpan.FromMilliseconds(33); _rotationTimer.Tick+=(_,_)=>{ if(!_autoRotate)return; _angle+=.25; MapGroup.Transform=new Media3D.RotateTransform3D(new Media3D.AxisAngleRotation3D(new Media3D.Vector3D(0,0,1),_angle));}; _rotationTimer.Start(); }
    private void InitializeTimeAnimation(){ _timeAnimationTimer.Interval=TimeSpan.FromMilliseconds(800); _timeAnimationTimer.Tick+=(_,_)=>{ if(_times.Count==0)return; int next=(int)TimeSlider.Value+1; if(next>=_times.Count)next=0; TimeSlider.Value=next;}; }
    private void SetCamera(double px,double py,double pz,double lx,double ly,double lz){ if(View.Camera is PerspectiveCamera cam){ cam.Position=new Media3D.Point3D(px,py,pz); cam.LookDirection=new Media3D.Vector3D(lx,ly,lz); cam.UpDirection=new Media3D.Vector3D(0,0,1);} }
    private void UpdateDisplayInfo(){ (ModeTitle.Text, LegendText.Text)=_displayMode switch { WeatherDisplayMode.Precipitation=>("表示：降水量","灰：0mm\n水色：1mm未満\n青：1〜5mm\n黄：5〜20mm\n赤：20mm以上"), WeatherDisplayMode.WindSpeed=>("表示：風速","水色：2m/s未満\n緑：2〜5m/s\n黄：5〜10m/s\n赤：10m/s以上"), WeatherDisplayMode.WindVector=>("表示：風ベクトル","矢印：風の流れ\n色：風速"), WeatherDisplayMode.WindGrid=>("表示：格子風ベクトル","矢印：風の流れ\n長さ：風速\n色：風速階級"), WeatherDisplayMode.StreamLine=>("表示：流線","線：風の流れ\nU/V格子風から近似"), WeatherDisplayMode.TemperatureGrid=>("表示：気温面","青：5℃未満\n水色：5〜15℃\n黄：15〜25℃\n赤：25℃以上"), WeatherDisplayMode.PrecipitationGrid=>("表示：降水面","灰：0mm\n水色：1mm未満\n青：1〜5mm\n黄：5〜20mm\n赤：20mm以上"), _=>("表示：気温","青：5℃未満\n水色：5〜15℃\n黄：15〜25℃\n赤：25℃以上")}; }
    private void LoadCsv_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new Microsoft.Win32.OpenFileDialog
        {
            Title = "AMeDAS CSVを選択",
            Filter = "CSV files (*.csv)|*.csv",
            CheckFileExists = true,
            Multiselect = false
        };

        if (dialog.ShowDialog() != true)
            return;

        try
        {
            _allRecords = AmedasCsvLoader.Load(dialog.FileName);

            if (_allRecords.Count == 0)
            {
                MessageBox.Show("CSVにデータがありません。", "CSV読込");
                return;
            }

            _times = _allRecords
                .Select(x => x.Time)
                .Distinct()
                .OrderBy(x => x)
                .ToList();

            _displayMode = WeatherDisplayMode.Temperature;

            TimeSlider.Minimum = 0;
            TimeSlider.Maximum = Math.Max(0, _times.Count - 1);
            TimeSlider.Value = 0;

            _currentTime = _times[0];

            _stations = _allRecords
                .Where(x => x.Time == _currentTime.Value)
                .ToList();

            StationGroup.Children.Clear();
            LabelGroup.Children.Clear();
            WindGridGroup.Children.Clear();
            WeatherGridGroup.Children.Clear();
            ContourGroup.Children.Clear();
            StreamLineGroup.Children.Clear();

            CreateStations();
            UpdateDisplayInfo();

            TimeText.Text = _currentTime.Value.ToString("yyyy/MM/dd HH:mm");

            MessageBox.Show(
                $"CSVを読み込みました。\n件数: {_allRecords.Count}\n時刻数: {_times.Count}",
                "CSV読込完了");
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                "CSV読込に失敗しました。\n\n" + ex.Message,
                "CSV読込エラー",
                MessageBoxButton.OK,
                MessageBoxImage.Error);
        }
    }

    private void Temperature_Click(object s,RoutedEventArgs e){_displayMode=WeatherDisplayMode.Temperature; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value));}
    private void Precipitation_Click(object s,RoutedEventArgs e){_displayMode=WeatherDisplayMode.Precipitation; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value));}
    private void WindSpeed_Click(object s,RoutedEventArgs e){_displayMode=WeatherDisplayMode.WindSpeed; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value));}
    private void WindVector_Click(object s,RoutedEventArgs e){_displayMode=WeatherDisplayMode.WindVector; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value));}
    private void WindGrid_Click(object s,RoutedEventArgs e){_displayMode=WeatherDisplayMode.WindGrid; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value));}
    private void StreamLine_Click(object s,RoutedEventArgs e){_displayMode=WeatherDisplayMode.StreamLine; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value));}
    private void TemperatureGrid_Click(object s,RoutedEventArgs e){_displayMode=WeatherDisplayMode.TemperatureGrid; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value));}
    private void PrecipitationGrid_Click(object s,RoutedEventArgs e){_displayMode=WeatherDisplayMode.PrecipitationGrid; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value));}
    private void TopView_Click(object s,RoutedEventArgs e)=>SetCamera(0,0,340,0,0,-340);
    private void ObliqueView_Click(object s,RoutedEventArgs e)=>SetCamera(-120,-260,140,120,260,-120);
    private void SideView_Click(object s,RoutedEventArgs e)=>SetCamera(-340,0,65,340,0,-25);
    private void RotateToggle_Click(object s,RoutedEventArgs e)
    {
        if (!_rotationTimer.IsEnabled)
            StartAutoRotation();

        _autoRotate = !_autoRotate;
    }
    private void Window_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Space)
        {
            if (!_rotationTimer.IsEnabled)
                StartAutoRotation();

            _autoRotate = !_autoRotate;
        }
    }
    private void TimeSlider_ValueChanged(object sender,RoutedPropertyChangedEventArgs<double> e){ if(_times.Count==0)return; SetCurrentTimeByIndex((int)Math.Round(TimeSlider.Value)); }
    private void PlayButton_Click(object sender,RoutedEventArgs e){ _isPlaying=!_isPlaying; if(_isPlaying){_timeAnimationTimer.Start(); PlayButton.Content="停止";}else{_timeAnimationTimer.Stop(); PlayButton.Content="再生";} }

    private void SaveImage_Click(object sender,RoutedEventArgs e){ var d=new Microsoft.Win32.SaveFileDialog{Filter="PNG Image (*.png)|*.png",FileName=$"WxAid3D_{_displayMode}_{DateTime.Now:yyyyMMdd_HHmmss}.png"}; if(d.ShowDialog()==true) SaveViewportToPng(d.FileName); }
    private void SaveViewportToPng(string file){ var rt=new RenderTargetBitmap((int)View.ActualWidth,(int)View.ActualHeight,96,96,System.Windows.Media.PixelFormats.Pbgra32); rt.Render(View); var enc=new PngBitmapEncoder(); enc.Frames.Add(BitmapFrame.Create(rt)); using var fs=new FileStream(file,FileMode.Create); enc.Save(fs); }

    private void LoadGrib2_Click(object sender,RoutedEventArgs e)
    {
        var d=new Microsoft.Win32.OpenFileDialog{Filter="GRIB2 files (*.grib2;*.bin)|*.grib2;*.bin|All files (*.*)|*.*"}; if(d.ShowDialog()!=true)return;
        Directory.CreateDirectory("Temp/extracted"); string w="Tools/wgrib2.exe", tmp="Temp/extracted/tmp.csv", u="Temp/extracted/ugrd.csv", v="Temp/extracted/vgrd.csv";
        try{ Wgrib2Runner.ExtractCsv(w,d.FileName,"TMP",tmp); Wgrib2Runner.ExtractCsv(w,d.FileName,"UGRD",u); Wgrib2Runner.ExtractCsv(w,d.FileName,"VGRD",v); _allWeatherGridRecords=ConvertTemperatureCsv(WgribCsvLoader.Load(tmp)); _allWindGridRecords=ConvertWindCsv(WgribCsvLoader.Load(u),WgribCsvLoader.Load(v)); _times=_allWeatherGridRecords.Select(x=>x.Time).Union(_allWindGridRecords.Select(x=>x.Time)).Distinct().OrderBy(x=>x).ToList(); TimeSlider.Maximum=Math.Max(0,_times.Count-1); TimeSlider.Value=0; _displayMode=WeatherDisplayMode.TemperatureGrid; SetCurrentTimeByIndex(0);} catch(Exception ex){ MessageBox.Show(ex.Message,"GRIB2読込エラー",MessageBoxButton.OK,MessageBoxImage.Error); }
    }

    private async void DownloadMapTiles_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            var range = WebMercatorTile.CreateJapanTileRange(6);

            string mapTileFolder = Path.Combine(
                AppDomain.CurrentDomain.BaseDirectory,
                "Assets",
                "Tiles",
                "map");

            string outputMapPath = Path.Combine(
                AppDomain.CurrentDomain.BaseDirectory,
                "Assets",
                "japan_map.png");

            await TileDownloader.DownloadTilesAsync(
                "https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png",
                range,
                mapTileFolder);

            var mergedMap = TileMerger.MergeTilesByRange(
                mapTileFolder,
                range);

            // 地図画像そのものを左右反転して保存
            var flippedMap = new TransformedBitmap(
                mergedMap,
                new ScaleTransform(
                    -1,
                    1,
                    mergedMap.PixelWidth / 2.0,
                    mergedMap.PixelHeight / 2.0));

            SaveBitmapSourceAsPng(flippedMap, outputMapPath);

            // 地図専用平面レイヤへ即反映
            CreateMapImagePlane();

            MessageBox.Show(
                "標準地図タイルを取得・結合し、左右反転補正して地図平面レイヤへ反映しました。\n\n" +
                "出力: " + outputMapPath + "\n" +
                "出典：国土地理院 地理院タイル",
                "完了",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                ex.Message,
                "タイル取得エラー",
                MessageBoxButton.OK,
                MessageBoxImage.Error);
        }
    }

    private static void SaveBitmapSourceAsPng(BitmapSource bitmap, string path)
    {
        string? dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrWhiteSpace(dir))
            Directory.CreateDirectory(dir);

        var encoder = new PngBitmapEncoder();
        encoder.Frames.Add(BitmapFrame.Create(bitmap));

        using var stream = new FileStream(path, FileMode.Create);
        encoder.Save(stream);
    }

}
