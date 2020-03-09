from yr.libyr import Yr
import json

weather = Yr(location_name="Norge/Telemark/Skien/Skien")
now = weather.now(as_json=True)
forecast = json.loads(now)
print(forecast)
periode = int(forecast["@period"])
from_time = forecast["@from"]
to_time = forecast["@to"]
symbol = forecast["symbol"]["@name"]
temp = forecast["temperature"]["@value"]
rain = forecast["precipitation"]["@value"]
print(periode)
print(from_time)
print(to_time)
print(symbol)
print(temp)
print(rain)
