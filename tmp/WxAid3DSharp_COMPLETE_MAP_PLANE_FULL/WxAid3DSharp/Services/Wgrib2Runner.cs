using System.Diagnostics;
using System.IO;

namespace WxAid3DSharp.Services;

public static class Wgrib2Runner
{
    public static void ExtractCsv(string wgrib2Path, string gribPath, string keyword, string outputCsvPath)
    {
        if (!File.Exists(wgrib2Path))
            throw new FileNotFoundException("Tools/wgrib2.exe が見つかりません。READMEを確認して配置してください。", wgrib2Path);

        var psi = new ProcessStartInfo
        {
            FileName = wgrib2Path,
            Arguments = $"\"{gribPath}\" -match \"{keyword}\" -csv \"{outputCsvPath}\"",
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };

        using var process = Process.Start(psi) ?? throw new InvalidOperationException("wgrib2の起動に失敗しました。");
        string stderr = process.StandardError.ReadToEnd();
        process.WaitForExit();
        if (process.ExitCode != 0)
            throw new InvalidOperationException(stderr);
    }
}
