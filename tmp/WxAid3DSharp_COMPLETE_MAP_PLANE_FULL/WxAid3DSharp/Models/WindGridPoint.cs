namespace WxAid3DSharp.Models;

public sealed class WindGridPoint
{
    public DateTime Time { get; set; }
    public double Latitude { get; set; }
    public double Longitude { get; set; }
    public double WindSpeed { get; set; }
    public double WindDirection { get; set; }
    public double U { get; set; }
    public double V { get; set; }
}
