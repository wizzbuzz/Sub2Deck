from collections import Counter
import json
import dcl
import pandas as pd
import spacy
import genanki

nlp = spacy.load("es_core_news_md")

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
    
    if(debug == True):
        print(difficulty, difficulty_frequency, difficulty_length, difficulty_diacritic, difficulty_stop)
    
    return difficulty

debug = True
show_CSV = False
file_location = "avatar.txt"
desired_language = "es"
desired_difficulty_rating = 30

if(debug == False):
    # User inputs txt file
    file_location = input("Please enter txt file location: ")
    # Verify txt file location
    try:
        with open(file_location):
            print("Success!")
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
with open(file_location) as f:
    file_as_string = clean_string(string=f.read(), chars=".,0123456789:->¡!¿?")

# Lemmatize  
doc = nlp(file_as_string)

# Program creates a word list of txt file
c = Counter()
max_frequency = float("-inf")
word_list = {}
for token in doc:
    #Strip undesired part of speech
    if (token.pos_ not in set(["SPACE", "AUX","PROPN", "PRON", "SCONJ","ADV", "CCONJ", "DET", "ADP"])):
        # Increase frequency
        c[token.lemma_] += 1
        # Add object to wordlist
        word_list[token.lemma_] = {
            # Add lemma
            "word": token.lemma_,
            # Add frequency
            "frequency": c[token.lemma_],
            # Add length
            "length": len(token.lemma_),
            # Add diacritic count
            "diacriticCount": dcl.count_diacritics(token.lemma_),
            # Add part of speech
            "POS": token.pos_,
            # Add is stop
            "stop": token.is_stop,
        }
        
        # Update max frequency if it is higher than the old value
        if(c[token.lemma_] > max_frequency):
            max_frequency = c[token.lemma_]

word_list_difficulty_stripped = {}
for x, obj in word_list.items():
    difficulty = get_difficulty(max_frequency, obj)
    obj["difficulty"] = difficulty
    if(obj["difficulty"] >= desired_difficulty_rating):
        word_list_difficulty_stripped[x] = obj



if (show_CSV == True):
    df = pd.DataFrame.from_dict(word_list_difficulty_stripped, orient="index")
    df.to_csv("debug2.csv", encoding="utf-8", errors="replace")