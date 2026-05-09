namespace WxAid3DSharp.Models;

public sealed class WeatherGridPoint
{
    public DateTime Time { get; set; }
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public double Temperature { get; set; }
    public double Precipitation { get; set; }
}
