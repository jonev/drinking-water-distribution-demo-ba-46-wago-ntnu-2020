import time
import random
import math
import matplotlib.pyplot as plt
import matplotlib as mpl

km_privat_ledning = 2
km_offentlig_ledning = 10
fast_trykk = 60
antall_bosatte = 50
antall_påkoblinger = antall_bosatte
nattforbruk_pr_bosatt = 0.6
lekkasje = 0
trykkfaktor = 30 / 50

#########
rho = 1000
P1 = 5 * 100000
r = 5 / 1000
print(r)
v2 = math.sqrt(2 * P1 / rho)
A = 3.1415 * r * r
Q = v2 * A  # [m^3/s]
Qls = Q * 1000
Qlh = Qls * 3600
Qld = Qlh * 24
print(Qls)

perdag = 200
persek = 200 / (60 * 60 * 24) * 50
print(persek)
#########

x = [2, 4, 6]
y = [1, 3, 5]
plt.plot(x, y)
plt.show()
"""
timer = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
flow = [5, 4, 4.5, 3, 2, 1, 0.6, 1.5, 7, 15, 13, 12, 11, 14, 16, 22, 20, 21, 17, 18, 14, 10, 8, 4]
print(len(timer))

summer = sum(flow)
print(summer)
print(flow)

for i in range(0, len(flow)):
    flow[i] = round(flow[i] * random.uniform(0.95, 1.05), 1)
print(flow)


for i in range(200):
    dråpetap = (
        ((antall_påkoblinger * 0.8) + (km_offentlig_ledning * 18) + (km_privat_ledning * 25))
        * fast_trykk
        / 24
    )

    dråpetap_random = dråpetap * random.uniform(0.95, 1.05)
    boligforbruk = antall_bosatte * nattforbruk_pr_bosatt
    boligforbruk_random = boligforbruk * random.uniform(0.8, 1.2)

    målt_nattforbruk = boligforbruk_random + dråpetap_random + lekkasje


    lekkasjemengde = (målt_nattforbruk - (dråpetap + boligforbruk)) * trykkfaktor
    if lekkasjemengde < 0:
        lekkasjemengde = 0
    lekkasje = 30  # lekkasje + 2
    if lekkasjemengde > 120:
        print("LEKKASJE!")
        print("Utregnet lekkasje: " + str(lekkasjemengde))
        print("Reell lekkasje: " + str(lekkasje))
        print("Målt nattforbruk"+str(målt_nattforbruk))
        print("Trykk" +str(trykk))
        break
    print("Utregnet lekkasje: " + str(lekkasjemengde))
    print("Reell lekkasje: " + str(lekkasje))
    print("")
    time.sleep(0)
"""
