namespace WxAid3DSharp.Models;

public sealed class WgribCsvRecord
{
    public DateTime Time0 { get; set; }
    public DateTime Time1 { get; set; }
    public string Field { get; set; } = "";
    public string Level { get; set; } = "";
    public double Longitude { get; set; }
    public double Latitude { get; set; }
    public double Value { get; set; }
}
