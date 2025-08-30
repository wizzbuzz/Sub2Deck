from collections import Counter
import os
from time import sleep
import pick
import dcl
import pandas as pd
import spacy
import requests
from bs4 import BeautifulSoup

languages = [
    {"prompt": "[English]", "code": "en", "package": "en_core_news_md", "encoding": "latin-1"},
    {"prompt": "[Spanish]", "code": "es", "package": "es_core_news_md", "encoding": "latin-1"},
    {"prompt": "[Japanese]", "code": "ja", "package": "ja_core_news_md", "encoding": "UTF-8"},

]
def extract_definition(response):
    """
    Extract the definition from the Wiktionary API response.
    Returns the first line of the definition found in the HTML.
    """
    data = response["query"]["pages"][str(next(iter(response["query"]["pages"])))]["extract"]
    soup = BeautifulSoup(data, features="html.parser")
    return soup.dd.get_text().splitlines()[0]


def get_definition(word, desired_language):
    """
    Get the definition of a word from Wiktionary for the specified language.
    Returns the definition string, or raises an exception if not found.
    """
    #Spanish, English
    if(desired_language["code"] in ["en", "es"]):
        api_url = f"https://{desired_language['code']}.wiktionary.org/w/api.php?action=query&format=json&prop=extracts&titles={word}"
        response = requests.get(api_url)
        # Check if the word has an entry in Wiktionary
        success = False
        try:
            response.json()["query"]["pages"]["-1"] == None
        except:
            success = True
        if not success:
            raise Exception("No definition found")
        data = response.json()["query"]["pages"][str(next(iter(response.json()["query"]["pages"])))]["extract"]
        soup = BeautifulSoup(data, features="html.parser")
        return soup.dd.get_text().splitlines()[0]
    elif(desired_language["code"] in ["ja"]):
        api_url = f"https://jisho.org/api/v1/search/words?keyword={word}"
        response = requests.get(api_url)
        try:
            definition = response.json()["data"][0]["senses"][0]["english_definitions"][0]
        except:
            raise Exception("No definition found")
        return definition



def clean_string(string, chars):
    """
    Clean a string by removing specified characters, normalizing whitespace,
    converting to lowercase, and trimming spaces.
    """
    for c in chars:
        string = string.replace(c, "")
    string = string.replace("  ", " ")
    string = string.replace("\n", " ")
    string = string.lower()
    string = string.strip()
    return string


def get_difficulty(maxFrequency, word):
    """
    Calculate a custom difficulty score for a word based on:
    - Frequency (rarer words are harder)
    - Length (longer words are harder)
    - Diacritics (words with diacritics are harder)
    - Stopword status (non-stopwords are harder)
    Returns the word dict with difficulty fields added.
    """
    difficulty_frequency = round(((maxFrequency - word["frequency"]) / (maxFrequency - 1)) * 25)
    difficulty_length = round((word["length"] / 23) * 25)
    difficulty_diacritic = 0 if word["diacriticCount"] == 0 else 25
    difficulty_stop = 0 if word["stop"] == True else 25
    difficulty = difficulty_frequency + difficulty_length + difficulty_diacritic + difficulty_stop
    word["difficulty"] = difficulty
    word["difficulty_frequency"] = difficulty_frequency
    word["difficulty_length"] = difficulty_length
    word["difficulty_diacritic"] = difficulty_diacritic
    word["difficulty_stop"] = difficulty_stop
    return word
def reconstruct_sentences(lines):
    """
    Reconstruct sentences from subtitle lines, ignoring timestamps and numbers.
    Returns a list of full sentences for example lookup.
    """
    lines = list(filter(lambda x: "-->" not in x and x != "" and not x.isdigit(), lines))
    reconstructed = []
    temp = ""
    for x in lines:
        temp += " " + x
        if x.endswith("?") or x.endswith("!") or x.endswith("."):
            reconstructed.append(temp.strip())
            temp = ""
    return [s.replace("  ", " ").replace("   ", " ") for s in reconstructed]


def prompt_user():
    """
    Prompt user for all required input values:
    - Subtitle file location
    - Output CSV file name
    - Desired language
    - Difficulty rating
    - spaCy language model
    Returns all values for use in main.
    """
    file_location = (input("Please enter subtitle .txt file location (without extension): ") or "input") + ".txt"
    try:
        with open(file_location):
            print(f"File {file_location} found!")
    except:
        file_location = input(f"File {file_location} not found, please enter txt file location (without extension): ")  + ".txt"
    output_file_location = (input("Please enter .csv output file name (without extension): ") or "output") + ".csv"
    language_options = [lang["prompt"] for lang in languages]
    language_option, index = pick.pick(language_options, "\nPlease select an action:", indicator='=>', default_index=0)
    desired_language = languages[index]
    try:
        nlp = spacy.load(desired_language["package"])
    except:
        print(f"It seems like the {desired_language['package']} has not been installed.")
        print(f"Run python -m spacy download {desired_language['package']} and try again.")
        print("Closing...")
        exit()
    desired_difficulty_rating = int(input("Please enter desired difficulty rating (1-100) (if unsure, try 75): ") or "75")
    return file_location, output_file_location, desired_language, desired_difficulty_rating, nlp

def build_word_list(doc, sentences):
    """
    Build a word list from lemmatized tokens and example sentences.
    Filters out undesired parts of speech and finds example sentences for each word.
    Returns the word list and the maximum frequency found.
    """
    c = Counter()
    max_frequency = float("-inf")
    word_list = {}
    for token in doc:
        if (token.pos_ not in set(["SPACE", "AUX","PROPN", "PRON", "SCONJ","ADV", "CCONJ", "DET", "ADP"])):
            c[token.lemma_] += 1
            try:
                example_sentence = next(sentence for sentence in sentences if token.text in sentence)
            except:
                example_sentence = ""
            word_list[token.lemma_.split(" ")[0]] = {
                "word": token.lemma_.split(" ")[0],
                "frequency": c[token.lemma_.split(" ")[0]],
                "length": len(token.lemma_.split(" ")[0]),
                "diacriticCount": dcl.count_diacritics(token.lemma_.split(" ")[0]),
                "POS": token.pos_,
                "stop": token.is_stop,
                "sentence in script": example_sentence
            }
            if(c[token.lemma_] > max_frequency):
                max_frequency = c[token.lemma_]
    return word_list, max_frequency

def filter_by_difficulty(word_list, max_frequency, desired_difficulty_rating):
    """
    Filter words by difficulty rating using the custom difficulty function.
    Returns a dictionary of words that meet or exceed the rating.
    """
    filtered = {}
    for x, obj in word_list.items():
        obj = get_difficulty(max_frequency, obj)
        if(obj["difficulty"] >= desired_difficulty_rating):
            filtered[x] = obj
    return filtered

def fetch_definitions(word_list, desired_language):
    """
    Fetch definitions for each word from Wiktionary.
    Adds the definition to each word's dictionary entry.
    Returns a dictionary of words with definitions included.
    """
    word_list_with_definition = {}
    for i, (x, obj) in enumerate(word_list.items(), 1):
        sleep(1)  # Sleep to avoid rate-limiting
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal for progress
        try:
            print(f"Getting definition of {obj['word']}")
            obj["definition"] = get_definition(obj["word"], desired_language)
            word_list_with_definition[obj["word"]] = obj
            print(f"{i} out of {len(word_list.items())} done...")
        except:
            print("There is no definition!")
            continue
    return word_list_with_definition

def main():
    """
    Main workflow for converting subtitle text to a CSV word list with definitions and difficulty ratings.
    Steps:
    1. Prompt user for input values
    2. Read and clean subtitle file
    3. Lemmatize and reconstruct sentences
    4. Build word list and filter by difficulty
    5. Fetch definitions
    6. Save results to CSV
    """
    file_location, output_file_location, desired_language, desired_difficulty_rating, nlp = prompt_user()
    # Read and clean subtitle file
    with open(file_location, encoding=desired_language['encoding']) as f:
        file_as_string = clean_string(string=f.read(), chars=".,0123456789:->¡!¿?½")
    # Lemmatize text
    doc = nlp(file_as_string.replace("\n", " "))
    # Reconstruct sentences for example lookup
    with open(file_location, encoding="latin-1") as f:
        lines = f.read().splitlines()
    sentences = reconstruct_sentences(lines)
    # Build word list and get max frequency
    word_list, max_frequency = build_word_list(doc, sentences)
    # Filter words by difficulty
    filtered_words = filter_by_difficulty(word_list, max_frequency, desired_difficulty_rating)
    # Fetch definitions for filtered words
    word_list_with_definition = fetch_definitions(filtered_words, desired_language)
    # Save results to CSV
    df = pd.DataFrame.from_dict(word_list_with_definition, orient="index")
    df.to_csv(f"{output_file_location}", encoding="latin-1", errors="replace")
    print(f"{output_file_location} created succesfully.")