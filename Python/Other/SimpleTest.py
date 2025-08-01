import requests
import cowsay
from http import HTTPStatus as status
import os
import re
import yt_dlp
import csv
import pandas as pd


def HTTP():
    while True:
        que = input("Do you want to display status values? (y/n): ").lower()
        if que == "y" or que == "yes":
            try:
                re = int(input("\nWhich status number? "))
                if re in status._value2member_map_:
                    print(f'Status Description of {re} is: "{status(re).phrase}"')
                else:
                    print("There is no such key!")
            except ValueError:
                print("Please enter an integer!\n")
        elif que == "n" or que == "no":
            break
        else:
            print("Wrong input, please answer with 'y' or 'n'\n")


    print("\n\n\n")
    url = 'https://jsonplaceholder.typicode.com/albums'

    response = requests.get(url) 
       
    if response.status_code == 200:
        albums = response.json()
        for album in albums[:3]:
            print(f"userId: {album['userId']}")
            print(f"id: {album['id']}")
            print(f"title: {album['title']}\n")
    else:
        print(f"Failed with status code {response.status_code}")

def animal():
    while True:
        try:
            n = int(input("\n\nHow much? "))
            cowsay.cow(f"Your Number is {n}\n")
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            
def print_square(n):
    for i in range(n):
        for j in range(n):
            print("#", end="")
        print()
       
def print_square2(n):
    for i in range(n):
        print("#" *n)

def VD():
    path = r"C:\Users\hp OMEN\Downloads\Video"
    url = input("URL: ")
    os.makedirs(path, exist_ok=True)

    options = {
        'format': 'best[height<=1080]/best',
            'outtmpl': f"{path}\\%(title)s.%(ext)s",
        'ignoreerrors': True,
        'concurrent_fragments': 4,  
        'http_chunk_size': 10485760,  
        'retries': 3,
        'fragment_retries': 3,
        'writeinfojson': False, 
        'writesubtitles': False,  
        'writeautomaticsub': False,
        'extract_flat': False,   
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        print(f"Download completed successfully, \npath:{path}.")
    except Exception as e:
        print(f"An error has occurred ({e})")
        
class DrinkCSV:
    def __init__(self, file):
        self.file = file
            
    def read(self):
        drinks = []
        with open(self.file) as file:
            reader = csv.DictReader(file)
            for row in reader:
                drinks.append({
                    "country": row["country"],
                    "beer_servings": int(row["beer_servings"]),
                    "spirit_servings": int(row["spirit_servings"]),
                    "wine_servings": int(row["wine_servings"]),
                    "total_litres_of_pure_alcohol": float(row["total_litres_of_pure_alcohol"])
                })
        return drinks

    def write(self, data):
        with open(self.file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def info(self, drinks):
        for drink in sorted(drinks, key=lambda drink: drink["country"]):
            print(f"\n\033[1mCountry: {drink['country']}\033[0m")
            print(f"beer_servings: {drink['beer_servings']}")
            print(f"spirit_servings: {drink['spirit_servings']}")
            print(f"wine_servings: {drink['wine_servings']}")
            print(f"total_litres_of_pure_alcohol: {drink['total_litres_of_pure_alcohol']}")

    def optional_info(self, drinks):
        for drink in sorted(drinks, key=lambda drink: drink["beer_servings"], reverse=True):
            if drink['beer_servings'] >= 100:
                print(f"\n\033[1mCountry: {drink['country']}\033[0m")
                print(f"Beer servings: {drink['beer_servings']}")
                
    @staticmethod
    def main():
        file = DrinkCSV("drinks.csv")
        drinks = file.read()

        print("\n\033[1mAll Drinks Information:\033[0m")
        file.info(drinks)

        print("\n\033[1mOptional Information (Beer Servings >= 100):\033[0m")
        file.optional_info(drinks)

def Pandas_csv():
    drinks = pd.read_csv("drinks.csv")
    filtered = drinks[drinks["beer_servings"] >= 100].copy()
    ratios = (filtered["beer_servings"] / filtered["total_litres_of_pure_alcohol"]).sort_values(ascending=False)

    print("\033[1mCountries with High Beer Consumption:\033[0m\n")
    for i in ratios.index:
        print(f"Country: {filtered.loc[i, 'country']}")
        print(f"Beer Consumption: {ratios[i]:.2f}\n")

def EmailValid():
    email = input("Enter your email: ").strip()
    pattern = r"^[^\s@#$%.^&*()]+@[^\s@#$%^&*()]+\.(com|edu)$"
    print("Valid email address." if re.fullmatch(pattern, email) else "Invalid email address.")

if __name__ == "__main__":
    
    print("\n\n\033[1mWelcome Muwahhid To The Tests Program!\033[0m\n")
    print("0. Exit")
    print("1. HTTP Info")
    print("2. CowSay")
    print("3. Print Square")
    print("4. Download Video")
    print("5. CSV (Raw)")
    print("6. CSV (Pandas)")
    print("7. Email Validation")

    while True:
        choice = input("\n\nPick an option: ").strip()
        print("\n\n")
        match choice:
            case "0": exit()
            case "1": HTTP()
            case "2": animal()
            case "3": print_square2(5)
            case "4": VD()
            case "5": DrinkCSV.main()
            case "6": Pandas_csv()
            case "7": EmailValid()
            case _: print("\nInvalid choice.\n")