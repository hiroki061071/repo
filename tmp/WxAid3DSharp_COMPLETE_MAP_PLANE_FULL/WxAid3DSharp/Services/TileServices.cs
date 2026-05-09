using System.IO;
using System.Net.Http;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace WxAid3DSharp.Services;

public sealed class TileRange
{
    public int Zoom { get; set; }
    public int XMin { get; set; }
    public int XMax { get; set; }
    public int YMin { get; set; }
    public int YMax { get; set; }
}

public static class WebMercatorTile
{
    public static (int x, int y) LonLatToTile(double lon, double lat, int zoom)
    {
        double latRad = lat * Math.PI / 180.0;
        int n = 1 << zoom;
        int x = (int)((lon + 180.0) / 360.0 * n);
        int y = (int)((1.0 - Math.Log(Math.Tan(latRad) + 1.0 / Math.Cos(latRad)) / Math.PI) / 2.0 * n);
        return (x, y);
    }

    public static TileRange CreateJapanTileRange(int zoom)
    {
        var nw = LonLatToTile(122.0, 46.0, zoom);
        var se = LonLatToTile(146.0, 24.0, zoom);
        return new TileRange { Zoom = zoom, XMin = nw.x, XMax = se.x, YMin = nw.y, YMax = se.y };
    }
}

public static class TileDownloader
{
    private static readonly HttpClient Client = new();

    public static async Task DownloadTilesAsync(string urlTemplate, TileRange range, string outputFolder)
    {
        Directory.CreateDirectory(outputFolder);
        for (int y = range.YMin; y <= range.YMax; y++)
        for (int x = range.XMin; x <= range.XMax; x++)
        {
            string url = urlTemplate.Replace("{z}", range.Zoom.ToString()).Replace("{x}", x.ToString()).Replace("{y}", y.ToString());
            string file = Path.Combine(outputFolder, $"{range.Zoom}_{x}_{y}.png");
            if (File.Exists(file)) continue;
            byte[] data = await Client.GetByteArrayAsync(url);
            await File.WriteAllBytesAsync(file, data);
        }
    }
}

public static class TileMerger
{
    public static BitmapSource MergeTiles(string folderPath, int columns, int rows)
    {
        var files = Directory.GetFiles(folderPath, "*.png").OrderBy(x => x).ToList();
        if (files.Count == 0)
            throw new FileNotFoundException($"タイルが見つかりません: {folderPath}");

        var first = new BitmapImage(new Uri(files[0], UriKind.Absolute));
        int tileWidth = first.PixelWidth;
        int tileHeight = first.PixelHeight;
        int finalWidth = tileWidth * columns;
        int finalHeight = tileHeight * rows;

        var visual = new DrawingVisual();
        using (var ctx = visual.RenderOpen())
        {
            int index = 0;
            for (int y = 0; y < rows; y++)
            for (int x = 0; x < columns; x++)
            {
                if (index >= files.Count) break;
                var tile = new BitmapImage(new Uri(files[index++], UriKind.Absolute));
                ctx.DrawImage(tile, new Rect(x * tileWidth, y * tileHeight, tileWidth, tileHeight));
            }
        }

        var target = new RenderTargetBitmap(finalWidth, finalHeight, 96, 96, PixelFormats.Pbgra32);
        target.Render(visual);
        return target;
    }
    public static BitmapSource MergeTilesByRange(string folderPath, TileRange range)
    {
        int columns = range.XMax - range.XMin + 1;
        int rows = range.YMax - range.YMin + 1;

        string firstPath = Path.Combine(folderPath, $"{range.Zoom}_{range.XMin}_{range.YMin}.png");

        if (!File.Exists(firstPath))
            throw new FileNotFoundException($"先頭タイルが見つかりません: {firstPath}");

        var first = new BitmapImage(new Uri(Path.GetFullPath(firstPath)));
        int tileWidth = first.PixelWidth;
        int tileHeight = first.PixelHeight;

        int finalWidth = tileWidth * columns;
        int finalHeight = tileHeight * rows;

        var visual = new DrawingVisual();

        using (var ctx = visual.RenderOpen())
        {
            for (int y = range.YMin; y <= range.YMax; y++)
            {
                for (int x = range.XMin; x <= range.XMax; x++)
                {
                    string file = Path.Combine(folderPath, $"{range.Zoom}_{x}_{y}.png");

                    if (!File.Exists(file))
                        continue;

                    var tile = new BitmapImage(new Uri(Path.GetFullPath(file)));

                    int drawX = (x - range.XMin) * tileWidth;
                    int drawY = (y - range.YMin) * tileHeight;

                    ctx.DrawImage(tile, new Rect(drawX, drawY, tileWidth, tileHeight));
                }
            }
        }

        var target = new RenderTargetBitmap(finalWidth, finalHeight, 96, 96, PixelFormats.Pbgra32);
        target.Render(visual);
        return target;
    }

}
