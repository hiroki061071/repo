namespace WxAid3DSharp.Models;

public sealed class AmedasStation
{
    public DateTime Time { get; set; }
    public string Name { get; set; } = "";
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public double Temperature { get; set; }
    public double Precipitation { get; set; }
    public double WindSpeed { get; set; }
    public double WindDirection { get; set; }
}
