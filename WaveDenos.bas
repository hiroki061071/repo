Attribute VB_Name = "Module1"
Option Explicit
Const Pi As Double = 3.14159265358979
'Sub SMB_waveheight()
'    Dim V As Double
'    Dim d As Double
'    Dim H As Double
'    V = Range("B6").Value '風速 (m/s)
'    d = Range("B7").Value * 1000 '吹送距離 (m)
'    H = (0.0014 * V ^ 2.5) * (1 + 0.0033 * d) '有義波高 (m)
'    Range("E6").Value = H
'End Sub

Function SMB(height As Double, fetch As Double) As Double
    ' Constants for SMB equation
    Const g As Double = 9.81
    Const rhoa As Double = 1.23
    Const rhow As Double = 1025
    
    ' Convert fetch to meters
    fetch = fetch * 1000
    
    ' Calculate wind stress
    Dim ustar As Double
    ustar = 0.032 * (height ^ 0.5)
    Dim tau As Double
    tau = rhoa * ustar ^ 2
    
    ' Calculate friction velocity and wind speed at 10 m height
    Dim u10 As Double
    u10 = 10 / (1 - (0.0001 * height))
    Dim ustar10 As Double
    ustar10 = ustar * (u10 / (0.4 * ustar))
    
    ' Calculate wave parameters
    Dim wave_age As Double
    wave_age = (g * fetch) / (u10 ^ 2)
    Dim wave_height As Double
    wave_height = (tau / rhow) * (1 + (0.56 * wave_age) ^ 0.5)
    
    ' Calculate wave period
    Dim wave_period As Double
    wave_period = (2 * 3.14) * ((wave_age / 0.83) ^ 0.5)
    
    SMB = wave_height
End Function

Function SMB3(A As Double, F As Double, U As Double) As Double
' Constants for SMB3 equation
    Const g As Double = 9.81
    Const A1 As Double = 0.0017
    Const B1 As Double = 0.702
    Const C1 As Double = 1.05
    Const D1 As Double = 0.035
    SMB3 = ((g * F) / (2 * 3.14 * U ^ 2)) ^ 2 * A1 * F ^ B1 * U ^ C1 * Exp(-D1 * F) ' Calculate SMB3 equation
End Function

Sub testSMB()
    ' Test case with height = 10m and fetch = 1km
    Dim height As Double
    Dim fetch As Double
    height = Sheets("WaveDemo").Cells(3, 2)
    fetch = Sheets("WaveDemo").Cells(4, 2)
    Dim h As Double
    Dim T As Double
    h = SMB(height, fetch)
    T = (2 * 3.14) * ((h / 0.83) ^ 0.5)
    Debug.Print "SMB result: H = " & h & "m, T = " & T & "s"
'    Sheets("WaveDemo").Cells(3, 5) = SMB(height, fetch)
End Sub

Sub testSMB2()
    ' Test case with height = 10m and fetch = 1km
    Dim height As Double
    Dim fetch As Double
    Dim wind_speed As Double
    Dim fetch_time As Double
    Dim equiv_fetch As Double
    Dim wave_height As Double
    Dim wave_period As Double
    
    wind_speed = Sheets("WaveDemo").Cells(8, 2)
    fetch_time = Sheets("WaveDemo").Cells(9, 2)
    equiv_fetch = wind_speed * fetch_time / 3600 ' Convert fetch time to hours and calculate equivalent fetch
    Sheets("WaveDemo").Cells(8, 5) = equiv_fetch
    ' Use the shorter of equivalent fetch and original fetch
    fetch = Sheets("WaveDemo").Cells(9, 2)
    If equiv_fetch < fetch Then
        fetch = equiv_fetch
    End If

    height = Sheets("WaveDemo").Cells(10, 2)
    
    wave_height = SMB(height, fetch)
    wave_period = 2 * 3.14 * ((wave_height / 9.81) ^ 0.5)
    
    Sheets("WaveDemo").Cells(8, 8) = wave_height
    Sheets("WaveDemo").Cells(9, 8) = wave_period
End Sub

Sub calculate_wave_properties()
    ' Constants for SMB3 equation
    Const g As Double = 9.81
    
    ' Input values for wind speed U1 and fetch F1
    Dim U1 As Double
    Dim F1 As Double
    Dim time1 As Double
    Dim equiv_F1 As Double
    Dim H1 As Double
    Dim T1 As Double
    Dim iflag As Integer
    
    U1 = 7
    time1 = 6
    F1 = U1 * time1 / 3600 ' Convert fetch time to hours and calculate fetch
    equiv_F1 = SMB3(0, F1, U1) ' Calculate equivalent fetch using SMB3 function
    If equiv_F1 < F1 Then
        F1 = equiv_F1 ' Use the shorter of equivalent fetch and original fetch
        iflag = 0 ' If there is a corresponding point, set iflag to 0
    Else
        iflag = 1 ' If there is no corresponding point, set iflag to 1
    End If
    Sheets("WaveDemo").[iflag] = iflag
    H1 = SMB3(0, F1, U1) ' Calculate wave height using SMB3 function
    T1 = (2 * 3.14) * ((H1 / g) ^ 0.5)

    ' Output results for wave properties
    Debug.Print "Wind speed (U1) = " & U1 & " m/s"
    Debug.Print "Fetch (F1) = " & F1 & " m"
    Debug.Print "Equivalent Fetch = " & equiv_F1 & " m"
    Debug.Print "Wave height (H1) = " & H1 & " m"
    Debug.Print "Wave period (T1) = " & T1 & " s"
    
    ' Input values for wind speed U2 and fetch F2
    Dim U2 As Double
    Dim F2 As Double
    Dim time2 As Double
    Dim equiv_F2 As Double
    Dim H2 As Double
    Dim T2 As Double
    
    U2 = 15
    time2 = 8
    F2 = U2 * time2 / 3600 ' Convert fetch time to hours and calculate fetch
    equiv_F2 = SMB3(0, F2, U2) ' Calculate equivalent fetch using SMB3 function
    If equiv_F2 < F2 Then
        F2 = equiv_F2 ' Use the shorter of equivalent fetch and original fetch
    End If
    H2 = SMB3(0, F2, U2) ' Calculate wave height using SMB3 function
    T2 = (2 * 3.14) * ((H2 / g) ^ 0.5)
    
    ' Output results for wave properties
    Debug.Print "Wind speed (U2) = " & U2 & " m/s"
    Debug.Print "Fetch (F2) = " & F2 & " m"
    Debug.Print "Equivalent Fetch = " & equiv_F2 & " m"
    Debug.Print "Wave height (H2) = " & H2 & " m"
    Debug.Print "Wave period (T2) = " & T2 & " s"
End Sub

''コード内の senkai サブルーチンは、次の操作を実行するように見えます。
''波の周期 T と Pi の値から深海の波長 L0 を計算します。
''h (水深) と T を入力として関数 SHALWAVL を使用して、浅瀬での波長 L を計算します。
''h と L から相対波高 x を計算します。
''x から浅瀬波数 n を計算します。
''L0、n、L に基づいて浅瀬係数 Ks を計算します。
''入射波角 a0 と L と L0 から波角 a を計算します。
''波角a0とL､L0から波高低減率を算出します｡
''結果の値は、Excel ファイルの「WaveDemo」シートのセルに保存されます。
''※こちらは検算済のため、絶対に修正しないこと！！
'
'Sub shinkai()
'
'    ' MOD Start 2023/2/4　H.Murakami
'    Dim objMyClass As New waveDLL.MyClass1
'    ' MOD Start 2023/3/25　H.Murakami
'    Const Pi As Double = 3.14159265358979
'    Dim T As Double
'    Dim L0 As Double
'    Dim h As Double
'    Dim L As Double
'    Dim x As Double
'    Dim Sinh As Double
'    Dim n As Double
'    Dim Ks As Double
'    Dim a0 As Double
'    Dim sina As Double
'    Dim A As Double
'
'    T = Sheets("WaveDemo").Cells(36, 1)
'
'    L0 = 4.9 / Pi * (T) ^ 2
'
'    Sheets("WaveDemo").Cells(36, 2) = L0
'    Sheets("WaveDemo").Cells(36, 3) = L0 * T
'
'    h = Sheets("WaveDemo").Cells(36, 4)
'
'    L = objMyClass.SHALWAVL(h, T)
'    '計算式SHALWAVL(A36,D36)を優先
'    'Sheets("WaveDemo").Cells(36, 5) = L
'    Sheets("WaveDemo").Cells(36, 6) = L / T
'
'    x = 4 * Pi * h / L
'    Sinh = (Exp(x) - Exp(-x)) / 2
'    n = 0.5 * (1 + x / Sinh)
'    Ks = Sqr(L0 / (2 * n * L))
'    Sheets("WaveDemo").Cells(36, 7) = n
'    Sheets("WaveDemo").Cells(36, 8) = Ks
'
'    a0 = Sheets("WaveDemo").Cells(36, 9) * Pi / 180
'    sina = Sin(a0) * L / L0
'
'    A = Atn(sina / Sqr(1 - (sina) ^ 2))
'
'    Sheets("WaveDemo").Cells(36, 10) = A * 180 / Pi
'    Sheets("WaveDemo").Cells(36, 11) = (1 + (1 - (L / L0) ^ 2) * (Tan(a0)) ^ 2) ^ (-0.25)
'
'End Sub

Function shinkai2(T As Double, L0 As Double, c0 As Double, h As Double, theta As Double) As Variant
    ' Constants for water properties
    Const g As Double = 9.81

    ' Calculate deep water properties
    Dim k0 As Double
    Dim L As Double
    Dim c As Double
    Dim n As Double
    Dim Ks As Double
    Dim kr As Double
    Dim theta_r As Double

    k0 = (2 * 3.14) / L0 ' Calculate wave number for deep water
    L = (g * T ^ 2) / (2 * 3.14) ^ 2 ' Calculate wavelength for given period and water depth
    c = (g * h) ^ 0.5 ' Calculate wave speed for given water depth
    n = c0 / c ' Calculate refractive index
    Ks = (1 + (2 * (n ^ 2 - 1)) / (n + (n ^ 2 - 1) ^ 0.5)) / 2 ' Calculate shallow water coefficient
    theta_r = WorksheetFunction.Asin(Sin(theta * WorksheetFunction.Pi / 180) / n) * 180 / WorksheetFunction.Pi ' Calculate refracted angle
    kr = (2 * 3.14) / L * n ' Calculate refracted wave number

    ' Return values in an array
    shinkai2 = Array(L, c, n, Ks, theta_r, kr)
End Function

Sub shinkai()
    Dim T As Double
    Dim L0 As Double
    Dim c0 As Double
    Dim h As Double
    Dim theta As Double

    T = 2 ' 適切な値に置き換えてください
    L0 = 5 ' 適切な値に置き換えてください
    c0 = 20 ' 適切な値に置き換えてください
    h = 10 ' 適切な値に置き換えてください
    theta = 30 ' 適切な値に置き換えてください
    
    Dim shinkai_result As Variant
    shinkai_result = shinkai2(T, L0, c0, h, theta)
    
    Debug.Print "Wavelength (m): " & shinkai_result(0)
    Debug.Print "Wave speed (m/s): " & shinkai_result(1)
    Debug.Print "Refractive index: " & shinkai_result(2)
    Debug.Print "Shallow water coefficient: " & shinkai_result(3)
    Debug.Print "Refracted angle (deg): " & shinkai_result(4)
    Debug.Print "Refracted wave number: " & shinkai_result(5)
    
End Sub



'これは、"WaveDemo" という Microsoft Excel ワークシート内の Ruiseki という名前の Microsoft VBA サブルーチンです。
'サブルーチンは、ワークシートのセルから値を取得し、Smax、Deg1、および Deg2 の値を使用していくつかの計算を実行し、結果をワークシートのセルに書き込みます。
'p1 の計算は、CUMULERGY 関数と Smax および Deg1 値を入力パラメーターとして使用して行われます。
'p2 の計算も同様に行われますが、Deg1 の代わりに Deg2 が使用されます。
'absp は、p1 と p2 の絶対差です。 次に、absp の平方根が計算され、ワークシートに書き込まれます。

'Sub Ruiseki()
'
'  ' Macro1 Macro
'  ' マクロ記録日 : 2001/6/4  ユーザー名 : 石原幸男
'  ' MOD Start 2023/2/4　H.Murakami
'    Dim objMyClass As New waveDLL.MyClass1
'    'Dim Smax As Integer
'    Dim Smax As Double
'    Dim Deg1 As Double
'    Dim P1 As Double
'    Dim Deg2 As Double
'    Dim P2 As Double
'    Dim absp As Double
'   ' MOD End 2023/2/4　H.Murakami
'
''   ' MOD Start 2023/3/18　H.Murakami
'
'    '3回目
'    Smax = Sheets("WaveDemo").Cells(46, 1)
'    Deg1 = Sheets("WaveDemo").Cells(46, 2)
'    P1 = objMyClass.CUMULERGY(Smax, Deg1)
'    Sheets("WaveDemo").Cells(46, 3) = P1
'    Deg2 = Sheets("WaveDemo").Cells(46, 4)
'    ' MOD Start 2023/2/4　H.Murakami
'    P2 = objMyClass.CUMULERGY(Smax, Deg2)
'    ' MOD End 2023/2/4　H.Murakami
'    Sheets("WaveDemo").Cells(46, 5) = P2
'    absp = Abs(P1 - P2)
'    Sheets("WaveDemo").Cells(46, 6) = absp
'    Sheets("WaveDemo").Cells(46, 7) = Sqr(absp / Smax)
'
'End Sub

'Sub Ruiseki(Smax As Double, angle1 As Double, angle2 As Double)
'
'    '定数
'    Const rho As Double = 1025    '密度(kg/m^3)
'    Const g As Double = 9.81      '重力加速度(m/s^2)
'
'    '変数
'    Dim P1 As Double
'    Dim P2 As Double
'    Dim deltaP As Double
'    Dim Hrms As Double
'    Dim i As Integer
'    Dim h As Double
'    Dim T As Double
'    Dim c As Double
'    Dim omega As Double
'    Dim k As Double
'    Dim theta As Double
'
'    '入射角1に対する累積エネルギーを計算
'    P1 = 0
'    For i = 1 To 1000
'        '波高さをランダムに決定
'        h = Smax * WorksheetFunction.RandBetween(0, 1000) / 1000
'
'        '波周期を決定
'        T = 7.1 * h ^ 0.546
'
'        '波速度を計算
'        c = 1.56 * T ^ 0.5
'
'        '角周波数を計算
'        omega = 2 * WorksheetFunction.Pi / T
'
'        '波数を計算
'        k = omega ^ 2 / g
'
'        '波の進行方向を決定
'        theta = WorksheetFunction.RandBetween(angle1 - 1, angle1 + 1) * WorksheetFunction.Pi / 180
'
'        '累積エネルギーを計算
'        P1 = P1 + 0.5 * rho * g ^ 2 * h ^ 2 * c * WorksheetFunction.Cos(theta) / k
'    Next i
'
'    '入射角2に対する累積エネルギーを計算
'    P2 = 0
'    For i = 1 To 1000
'        '波高さをランダムに決定
'        h = Smax * WorksheetFunction.RandBetween(0, 1000) / 1000
'
'        '波周期を決定
'        T = 7.1 * h ^ 0.546
'
'        '波速度を計算
'        c = 1.56 * T ^ 0.5
'
'        '角周波数を計算
'        omega = 2 * WorksheetFunction.Pi / T
'
'        '波数を計算
'        k = omega ^ 2 / g
'
'        '波の進行方向を決定
'        theta = WorksheetFunction.RandBetween(angle2 - 1, angle2 + 1) * WorksheetFunction.Pi / 180
'
'        '累積エネルギーを計算
'        P2 = P2 + 0.5 * rho * g ^ 2 * h ^ 2 * c * WorksheetFunction.Cos(theta) / k
'    Next i
'
'    'P1とP2の差の絶対値を計算
'    deltaP = Abs(P1 - P2)
'
'    '波高比の平方根を計算
'    Hrms = (Abs(P1 - P2)) ^ 0.5
'
'    '結果を出力
'    Range("A1").Value = "P1"
'    Range("B1").Value = "P2"
'    Range("C1").Value = "|P1-P2|"
'    Range("D1").Value = "sqrt(|P1-P2|)"
'    Range("A2").Value = P1
'    Range("B2").Value = P2
'    Range("C2").Value = Abs(P1 - P2)
'    Range("D2").Value = Sqr(Abs(P1 - P2))
'End Sub

Sub Ruiseki(Smax As Double, theta1 As Double, theta2 As Double)
    Const rho As Double = 1025 'kg/m^3
    Const g As Double = 9.81 'm/s^2

    '波のパラメーターの設定
    Dim Tp As Double
    Tp = 1.6 * Smax ^ 0.5

    '深さの設定
    Dim h As Double
    h = 10

    '波のパラメーターの計算
    Dim k As Double
    Dim c As Double
    k = 2 * 3.14 / (Tp ^ 2 * g)
    c = Tp / k

    '角度をラジアンに変換
    Dim theta As Double
    theta = theta1 * 3.14 / 180

    'P1を計算
    Dim P1 As Double
    P1 = 0

    Do Until theta > 180 Step 0.1
        P1 = P1 + 0.5 * rho * g ^ 2 * h ^ 2 * c * Cos(theta) / k
        theta = theta + 0.1
    Loop

    'P2を計算
    Dim P2 As Double
    P2 = 0

    theta = theta2 * 3.14 / 180

    Do Until theta > 180 Step 0.1
        P2 = P2 + 0.5 * rho * g ^ 2 * h ^ 2 * c * Cos(theta) / k
        theta = theta + 0.1
    Loop

    '結果を出力
    Range("A1").Value = "P1"
    Range("B1").Value = "P2"
    Range("C1").Value = "|P1-P2|"
    Range("D1").Value = "波高比(|P1-P2|)1/2"

    Dim PDiff As Double
    PDiff = Abs(P1 - P2)
    Range("A2").Value = P1
    Range("B2").Value = P2
    Range("C2").Value = PDiff
    Range("D2").Value = (PDiff) ^ 0.5
End Sub

' サブルーチンのテスト
Sub Test_Ruiseki()
    Ruiseki 1.5, 45, 30
End Sub


Public Function SHALWAVL(ByVal h As Double, ByVal T As Double) As Double
    Const Pi As Double = 3.14159265358979
    Const g As Double = 9.8
    SHALWAVL = Sqr(g * T ^ 2 / (2 * Pi))
End Function


