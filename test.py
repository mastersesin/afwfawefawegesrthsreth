a = """3.143.219.198 kalieiakxi59.pem
18.190.158.143 lottiekcxwx85.pem
3.14.80.218 cristiny8okq32.pem
18.222.73.45 chrissys819880.pem
18.118.135.171 pennymrwjd34.pem
3.21.163.133 gildapd7hp08.pem
3.22.97.118 reine28t4m78.pem
18.222.201.203 constanciagfpkw24.pem
18.219.102.49 carmelitanra2a41.pem
18.217.3.237 loreenwnmwl05.pem
18.218.156.16 minnyawqpy55.pem
3.16.107.215 arlinebz4xd23.pem
18.217.144.194 melisandradqske21.pem
18.224.95.54 carlita5uczr95.pem
3.16.46.99 elyshayc3pn10.pem
3.141.190.93 nonnahk1rpi24.pem
18.191.246.241 anatolaceo6t77.pem
3.21.128.158 aggiebl1pc75.pem
18.216.167.186 lynnaeejuo43.pem
18.117.219.11 tilliejz66m12.pem
18.188.21.117 eachellegl4ie95.pem
3.16.91.187 shannahveemt72.pem
18.191.82.2 shayne5khjq93.pem
18.216.87.145 federicantuiy55.pem
3.142.68.3 halliex42oh66.pem
3.15.169.106 chloeoyxgf70.pem
3.17.204.35 lindsayw9lzc12.pem
18.218.35.171 nollieoaksb53.pem
18.189.2.45 gelyaqkuts59.pem
3.23.132.245 loriae2pjs61.pem
3.18.112.3 kelliefyscm95.pem"""
a = a.split('\n')
count = 1
for i in a:
    print('{} {} {}'.format(count, i.split()[1], i.split()[0]))
    count += 1
