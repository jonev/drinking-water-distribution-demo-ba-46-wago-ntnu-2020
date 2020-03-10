from random import randint

weatherTypes = [
    ("sun", -1),
    ("partlycloudy", 0),
    ("cloudy", 0),
    ("drizzle", 2),
    ("rainy", 4),
    ("storm", 6),
]

random = int(len(weatherTypes) / 2)
random = random + randint(-1, 1)
if random >= len(weatherTypes):
    random = len(weatherTypes) - 1
elif random < 0:
    random = 0
weather = weatherTypes[4][0]
print(weather)
rain = weatherTypes[random][1]
print(rain)
randomm = randint(2, 2)
print(randomm)
