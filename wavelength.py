########### math.sysモジュールのインポート ###########

import math
import sys
print('')
print('***** 微小振幅波の波長を求めます *****')

########### 条件の入力 ###########
h0=float(input('設計波高(m)を入力してください\n'))
t0=float(input('設計周期(s)を入力してください\n'))
tdl=float(input('潮位(m)を入力してください\n'))
sbl=float(input'(海底地盤高(m)を入力してください\n'))
dwl = tdl - sbl
print(f'設計水深  :{dwl:12.2f} m'.format(dwl))
if t0 <= 0:
    print('周期が負の値です。計算を終了します')
    sys.exit()
if dwl <= 0:
    print('設計水深が負の値です。計算を終了します')
    sys.exit()

########### 波長の繰り返し計算 ############

l0=9.8/2.0/math.pi*t0*t0
a=2.0*math.pi*dwl
x0=a/10
if x0>50:
    wlg=l0
else:
    x1=x0
    for i in range(100):
        th=math.tanh(x1)
        sh=math.sinh(x1)
        x2=x1-(x1-x0/th)/(1+x0/sh/sh)
        if math.fabs(1-x1/x2)<=0.001:
            break
        x1=x2
    wlg=a/x2

print(f'波　　長　　:{wlg:12.2f} m'.format(wlg))
print('')
print('***** 計算を終了します *****')
print('')
