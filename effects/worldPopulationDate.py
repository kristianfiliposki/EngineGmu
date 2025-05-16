import requests


def pop_world_number():
    worldate = "https://api.worldbank.org/v2/country/WLD/indicator/SP.POP.TOTL?format=json&date=2023"
    population_world_number = requests.get(worldate)
    return population_world_number.json()[1][0]["value"]

