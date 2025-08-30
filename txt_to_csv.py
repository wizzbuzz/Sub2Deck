from collections import Counter
import os
from time import sleep
import dcl
import pandas as pd
import spacy
import requests
from bs4 import BeautifulSoup

def extract_definition(response):
    # Extract the definition from the Wiktionary API response
    data = response["query"]["pages"][str(next(iter(response["query"]["pages"])))]["extract"]
    soup = BeautifulSoup(data, features="html.parser")
    print(soup.dd.span[-1])
    input()
    # Return the first line of the definition
    return(soup.dd.get_text().splitlines()[0])

def get_definition(word, desired_language):
    # Build the Wiktionary API URL for the word and language
    api_url = f"https://{desired_language}.wiktionary.org/w/api.php?action=query&format=json&prop=extracts&titles={word}"
    response = requests.get(api_url)
    # Check if the word has an entry in Wiktionary
    success = False
    try:
        response.json()["query"]["pages"]["-1"] == None
    except:
        success = True
    # If entry is missing, raise an exception
    if(success == False):
        raise Exception("No definition found")
    # Extract the definition from the response
    definition = extract_definition(response.json())
    return definition

def clean_string(string, chars):
    # Remove specified characters from the string
    for c in chars:
        string = string.replace(c, "")
    # Remove double spaces
    string = string.replace("  ", " ")
    # Replace new lines with spaces
    string = string.replace("\n", " ")
    # Convert to lowercase
    string = string.lower()
    # Remove leading/trailing spaces
    string = string.strip()
    return string

def get_difficulty(maxFrequency, word):
    # Calculate difficulty based on frequency, length, diacritics, and stopword status
    difficulty_frequency = round(((maxFrequency - word["frequency"]) / (maxFrequency - 1)) * 25)
    difficulty_length = round((word["length"] / 23) * 25)
    difficulty_diacritic = 0 if word["diacriticCount"] == 0 else 25
    difficulty_stop = 0 if word["stop"] == True else 25
    # Sum up difficulty components
    difficulty = difficulty_frequency + difficulty_length + difficulty_diacritic + difficulty_stop
    # Store difficulty breakdown in the word object
    word["difficulty"] = difficulty
    word["difficulty_frequency"] = difficulty_frequency
    word["difficulty_length"] = difficulty_length
    word["difficulty_diacritic"] = difficulty_diacritic
    word["difficulty_stop"] = difficulty_stop
    return word

def main():

    # Set debug mode and default values
    debug = False
    file_location = "input.txt"
    output_file_location = "output.csv"
    desired_language = "es"
    desired_difficulty_rating = 30

    # Load the spaCy language model
    nlp = spacy.load("es_core_news_md")

    # Prompt user for subtitle file location
    file_location = (input("Please enter subtitle .txt file location (without extension): ", ) or "input") + ".txt"
    # Verify that the file exists
    try:
        with open(file_location):
            print(f"File {file_location} found!")
    except:
        file_location = input(f"File {file_location} not found, please enter txt file location (without extension): ")  + ".txt"
    # Prompt for output CSV file name
    output_file_location = (input("Please enter .csv output file name (without extension): ", ) or "output") + ".csv"
    # Prompt for desired language
    desired_language = input("Please enter desired language (es, en): ") or "es"
    # Prompt for difficulty rating
    desired_difficulty_rating = int(input("Please enter desired difficulty rating (1-100) (if unsure, try 75): ") or "75")
    # Prompt for spaCy package name
    nlp = spacy.load(input("Please insert the name of the spacy package you downloaded: ") or "es_core_news_md")

    # Debug output if enabled
    if(debug == True):
        print(file_location, desired_language, desired_difficulty_rating)

    # Read the subtitle file and clean the text
    file_as_string = ""
    with open(file_location, encoding="latin-1") as f:
        file_as_string = clean_string(string=f.read(), chars=".,0123456789:->¡!¿?½")

    # Debug override string
    # file_as_string = "harás dejarás encontrarás enseñe subestimaré"
    # Lemmatize the cleaned text using spaCy
    doc = nlp(file_as_string.replace("\n", " "))

    # Read sentences from the subtitle file for example sentence lookup
    sentences_in_script = ""
    with open(file_location, encoding="latin-1") as f:
        sentences_in_script = f.read().splitlines()
        
    sentences_in_script = list(filter(lambda x: "-->" not in x and x != "" and x.isdigit() == False, sentences_in_script))
    reconstructed_sentences = []
    temp_sentence = ""
    for x in sentences_in_script:
        # Add the sentence to the end of the placeholder
        temp_sentence += " " + x
        # If it doesnt end with a sentence ending character
        if(x.endswith("?") or x.endswith("!") or x.endswith(".")):
            # Add it to the reconstructed sentence list
            reconstructed_sentences.append(temp_sentence)
            # Reset the placeholder
            temp_sentence = ""
    
    for s in reconstructed_sentences:
        s = s.replace("  ", " ").replace("   ", " ")
        

    # Create a word list from the lemmatized tokens
    c = Counter()
    max_frequency = float("-inf")
    word_list = {}
    for token in doc:
        # Filter out undesired parts of speech
        if (token.pos_ not in set(["SPACE", "AUX","PROPN", "PRON", "SCONJ","ADV", "CCONJ", "DET", "ADP"])):
            # Count frequency of each lemma
            c[token.lemma_] += 1

            example_sentence = ""
            # Try to find an example sentence containing the token
            try: 
                example_sentence = next(sentence for sentence in reconstructed_sentences if token.text in sentence)
            except:
                example_sentence = ""

            # Add word details to the word list
            word_list[token.lemma_.split(" ")[0]] = {
                "word": token.lemma_.split(" ")[0],
                "frequency": c[token.lemma_.split(" ")[0]],
                "length": len(token.lemma_.split(" ")[0]),
                "diacriticCount": dcl.count_diacritics(token.lemma_.split(" ")[0]),
                "POS": token.pos_,
                "stop": token.is_stop,
                "sentence in script": example_sentence
            }

            # Update max frequency if needed
            if(c[token.lemma_] > max_frequency):
                max_frequency = c[token.lemma_]

    # Filter words by difficulty rating
    word_list_difficulty_stripped = {}
    for x, obj in word_list.items():
        obj_with_difficulty = get_difficulty(max_frequency, obj)
        obj = obj_with_difficulty
        if(obj["difficulty"] >= desired_difficulty_rating):
            word_list_difficulty_stripped[x] = obj

    # Fetch definitions for each word from Wiktionary
    word_list_with_definition = {}
    i = 0
    for x, obj in word_list_difficulty_stripped.items():
        i += 1
        sleep(1)  # Sleep to avoid rate-limiting
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal for progress

        try: 
            print(f"Getting definition of {obj['word']}")
            obj["definition"] = get_definition(obj["word"], desired_language)
            word_list_with_definition[obj["word"]] = obj
            print(f"{i} out of {len(word_list_difficulty_stripped.items())} done...")
        except:
            print("There is no definition!")
            continue

    # Save the final word list with definitions to a CSV file
    df = pd.DataFrame.from_dict(word_list_with_definition, orient="index")
    df.to_csv(f"{output_file_location}", encoding="latin-1", errors="replace")

    print(f"{output_file_location} created succesfully.")