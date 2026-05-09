using CsvHelper;
using System.Globalization;
using System.IO;
using WxAid3DSharp.Models;

namespace WxAid3DSharp.Services;

public static class AmedasCsvLoader
{
    public static List<AmedasStation> Load(string path)
    {
        var config = new CsvHelper.Configuration.CsvConfiguration(CultureInfo.InvariantCulture)
        {
            HasHeaderRecord = true,
            IgnoreBlankLines = true,
            TrimOptions = CsvHelper.Configuration.TrimOptions.Trim,
            HeaderValidated = null,
            MissingFieldFound = null,
            BadDataFound = null
        };

        using var reader = new StreamReader(path);
        using var csv = new CsvReader(reader, config);

        return csv.GetRecords<AmedasStation>().ToList();
    }
}

public static class WeatherGridCsvLoader
{
    public static List<WeatherGridPoint> Load(string path)
    {
        using var reader = new StreamReader(path);
        using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);

        return csv.GetRecords<WeatherGridPoint>().ToList();
    }
}

public static class WindGridCsvLoader
{
    public static List<WindGridPoint> Load(string path)
    {
        using var reader = new StreamReader(path);
        using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);

        return csv.GetRecords<WindGridPoint>().ToList();
    }
}

public static class WgribCsvLoader
{
    public static List<WgribCsvRecord> Load(string path)
    {
        using var reader = new StreamReader(path);
        using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);

        var records = new List<WgribCsvRecord>();

        while (csv.Read())
        {
            records.Add(new WgribCsvRecord
            {
                Time0 = csv.GetField<DateTime>(0),
                Time1 = csv.GetField<DateTime>(1),
                Field = csv.GetField<string>(2) ?? "",
                Level = csv.GetField<string>(3) ?? "",
                Longitude = csv.GetField<double>(4),
                Latitude = csv.GetField<double>(5),
                Value = csv.GetField<double>(6)
            });
        }

        return records;
    }
}