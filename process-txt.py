from collections import Counter
import json
from time import sleep
import dcl
import pandas as pd
import spacy
import genanki
import requests
from bs4 import BeautifulSoup

nlp = spacy.load("es_core_news_md")

def extract_definition(response):
    data = response["query"]["pages"][str(next(iter(response["query"]["pages"])))]["extract"]
    soup = BeautifulSoup(data, features="html.parser")
    return(soup.dd.get_text().splitlines()[0])

def get_definition(word):
    api_url = f"https://es.wiktionary.org/w/api.php?action=query&format=json&prop=extracts&titles={word}"
    response = requests.get(api_url)
    # Check if word has an entry
    success = False
    try:
        response.json()["query"]["pages"]["-1"] == None
    except:
        success = True
    # Break if entry is missing
    if(success == False):
        raise Exception("No definition found")
    
    definition = extract_definition(response.json())
    # extract_definition(response)
    
    return definition

def clean_string(string, chars):
    # Remove characters in chars
    for c in chars:
        string = string.replace(c, "")
        
    # Remove double spaces
    string = string.replace("  ", " ")
    
    # Replace new line as new word
    string = string.replace("\n", " ")
    
    # Lowercase all words
    string = string.lower()
    
    # Remove trailing spaces
    string = string.strip()
    return string

def get_difficulty(maxFrequency, word):
    difficulty_frequency = round((word["frequency"] / maxFrequency) * 25)
    difficulty_length = round((word["length"] / 23) * 25)
    difficulty_diacritic = 0 if word["diacriticCount"] == 0 else 25
    difficulty_stop = 0 if word["stop"] == False else 25
    difficulty = difficulty_frequency + difficulty_length + difficulty_diacritic + difficulty_stop
    
    return difficulty

debug = True
show_CSV = True
file_location = "input.txt"
desired_language = "es"
desired_difficulty_rating = 30

if(debug == False):
    # User inputs txt file
    file_location = input("Please enter txt file location: ")
    # Verify txt file location
    try:
        with open(file_location):
            print("successs!")
    except:
        file_location = input(f"File {file_location} not found, please enter txt file location: ")
    # User inputs language
    desired_language = input("Please enter desired language (es, en): ")
    # User inputs desired difficulty rating <1-100>
    desired_difficulty_rating = input("Please enter desired difficulty rating (1-100): ")

# Debug results
if(debug == True):
    print(file_location, desired_language, desired_difficulty_rating)

# Save file to string, remove non-letters
file_as_string = ""
with open(file_location, encoding="latin-1") as f:
    file_as_string = clean_string(string=f.read(), chars=".,0123456789:->¡!¿?½")

# Lemmatize  
doc = nlp(file_as_string.replace("\n", " "))

sentences_in_script = ""
with open(file_location, encoding="latin-1") as f:
    sentences_in_script = f.read().splitlines()
    
# Program creates a word list of txt file
c = Counter()
max_frequency = float("-inf")
word_list = {}
for token in doc:
    #Strip undesired part of speech
    if (token.pos_ not in set(["SPACE", "AUX","PROPN", "PRON", "SCONJ","ADV", "CCONJ", "DET", "ADP"])):
        # Increase frequency
        c[token.lemma_] += 1
        
        example_sentence = ""
        #Try getting example sentence from script
        try: 
            example_sentence = next(sentence for sentence in sentences_in_script if token.text in sentence)
        except:
            example_sentence = ""
        
        # Add object to wordlist
        word_list[token.lemma_.split(" ")[0]] = {
            # Add lemma
            "word": token.lemma_.split(" ")[0],
            # Add frequency
            "frequency": c[token.lemma_.split(" ")[0]],
            # Add length
            "length": len(token.lemma_.split(" ")[0]),
            # Add diacritic count
            "diacriticCount": dcl.count_diacritics(token.lemma_.split(" ")[0]),
            # Add part of speech
            "POS": token.pos_,
            # Add is stop
            "stop": token.is_stop,
            # Add sentence in script
            "sentence in script": example_sentence
        }
        
        # Update max frequency if it is higher than the old value
        if(c[token.lemma_] > max_frequency):
            max_frequency = c[token.lemma_]
            

# Calculate difficulty for every word
word_list_difficulty_stripped = {}
for x, obj in word_list.items():
    difficulty = get_difficulty(max_frequency, obj)
    obj["difficulty"] = difficulty
    if(obj["difficulty"] >= desired_difficulty_rating):
        word_list_difficulty_stripped[x] = obj

# Get wiktionario 
word_list_with_definition = {}
i = 0
for x, obj in word_list_difficulty_stripped.items():
    i += 1
    sleep(1)

    try: 
        print(obj["word"])
        obj["definition"] = get_definition(obj["word"])
        word_list_with_definition[obj["word"]] = obj
        # print(word_list_with_definition)
        print(f"{i} out of {len(word_list_difficulty_stripped.items())} done...")
    except:
        print("There is no definition!")
        continue

if (show_CSV == True):
    df = pd.DataFrame.from_dict(word_list_with_definition, orient="index")
    df.to_csv("debug6.csv", encoding="latin-1", errors="replace")