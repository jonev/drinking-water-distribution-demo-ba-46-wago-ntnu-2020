# Base - from a source online
base = [
    8,
    6,
    5,
    5,
    5,
    5,
    5,
    6,
    7,
    7,
    8,
    9,
    9,
    9,
    9,
    10,
    11,
    12,
    12,
    12,
    11,
    11,
    10,
    8,
]


# print("Base: " + str(base))
l = base.__len__()
# print("Lenght base: " + str(l))

wantedLength = 48 * 2


if wantedLength % l != 0:
    raise Exception("Wanted length must be a multiplum of 24")

if wantedLength <= l:
    steps = l // wantedLength
    result = []
    for i in range(wantedLength):
        result.append(base[i * steps])
else:
    stepSize = l / wantedLength
    samplesPrSample = wantedLength // l
    result = []
    for b in range(l):  # 0-23
        releation = base[(b + 1) % l] - base[b]
        for s in range(samplesPrSample):  # 0-1
            sample = base[b] + (releation * (s * stepSize))
            print(sample)
            result.append(sample)
            # print("B: " + str(b) + " s: " + str(s))


# print("Result: " + str(result))
