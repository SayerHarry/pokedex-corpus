# Fetch pokedex entries and misc information for every pokemon and create a set of text files representing them
import requests
from bs4 import BeautifulSoup
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk import download
from nltk.corpus import stopwords
download('punkt')
download('punkt_tab')
download('stopwords')

class PokedexFetcher:
    def __init__(self):
        self.base_url = "https://pokemondb.net/pokedex/"
        self.stop_words = set(stopwords.words('english') + ["greek", "suffix"])  # Add specific words to remove
        self.rep_words = set(["it", "its",  "itself"])
        
    def fetch_pokemon(self, pokemon: str):
        url = self.base_url + pokemon
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            print(f"Failed to fetch data for {pokemon}. Status code: {response.status_code}")
            return None
        
    def extract_data(self, soup: BeautifulSoup):
        name = soup.find('h1').text.strip().lower() #get the name of the pokemon
        species = soup.find("th", string="Species").find_next("td").text.strip().lower() #get the species of the pokemon
        
        try:
            entries = soup.find("h2", string="Pokédex entries").find_next("table").find_all('td') # get all entries from the pokedex table
        except IndexError:
            entries = None
        
        try:
            etymology = soup.find("dl", class_="etymology").find_all(recursive=False) #get all etymology information
        except AttributeError:
            etymology = None

        return name, species, entries, etymology
    
    def clean_data(self, data):
        name, species, entries, etymology = data
        cleaned_entries = [name + " " +species]  # Start with the species as the first entry
        
        for entry in entries or []:
            text = entry.text.strip().lower()
            tokens = word_tokenize(text)
            filtered_tokens = []
            for word in tokens:
                if word in self.rep_words:
                    filtered_tokens.append(name)
                else:
                    filtered_tokens.append(word)
            cleaned_entries.append(" ".join(filtered_tokens))
        
        for entry in etymology or []:
            #print(entry.text)
            text = entry.text.strip().lower()
            text = text.replace("-", "")
            tokens = [name] + word_tokenize(text)
            cleaned_entries.append(" ".join(tokens))

        return list(dict.fromkeys(cleaned_entries))

if __name__ == "__main__":
    fetch = PokedexFetcher()
    for i in range(1, 1009): #1025 pokemon entries, but for testing purposes, we will limit it to 3
        id = str(i)
        soup = fetch.fetch_pokemon(id)
        if soup:
            extracted_data = fetch.extract_data(soup)
            cleaned_data = fetch.clean_data(extracted_data)
            with open(f"pokedex_entries/{id} {extracted_data[0]}.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(cleaned_data))