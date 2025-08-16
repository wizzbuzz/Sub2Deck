# Sub2Deck

Sub2Deck is a Python tool for converting subtitle text files into CSV word lists and then generating Anki decks for language learning. It uses NLP to analyze subtitles, extract vocabulary, and fetch definitions, making it ideal for learners who want to build custom flashcards from real-world content.

## Features

- Convert subtitle `.txt` files to CSV word lists with frequency, difficulty, and definitions
- Generate Anki decks (`.apkg`) from CSV word lists
- Supports Spanish and English definitions via Wiktionary
- Customizable difficulty rating for vocabulary selection

## Installation

1. **Clone the repository:**

   ```powershell
   git clone https://github.com/wizzbuzz/Sub2Deck.git
   cd Sub2Deck
   ```

2. **Set up a Python virtual environment (recommended):**

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
   Then download the spacy language package you require:
   https://spacy.io/usage/models

## Usage

Run the main script:

```powershell
python run.py
```

You will be prompted to:

1. Convert subtitles to a CSV word list
   - Enter the path to your subtitle `.txt` file
   - Choose output CSV name
   - Select language (`es` for Spanish, `en` for English)
   - Set desired difficulty rating (1-100)
2. Convert a CSV word list to an Anki deck
   - Enter the path to your CSV file
   - Choose a name for your Anki deck

The generated `.apkg` file can be imported into Anki.

## Example Workflow

1. Download a subtitle file (e.g. from opensubtitles)
2. Unpack the file, change the .SRT extension to .TXT
3. Run the tool and select "Convert subtitles to csv word list".
4. Run the tool again, select "Convert csv word list to anki deck" and input the freshly generated .CSV file.

## Uses

- Language learners building custom vocabulary decks from movies, series, or other subtitle sources
- Teachers creating targeted flashcards for students
- Anyone wanting to automate Anki deck creation from real-world text

## Notes

- Large language models and NLP are used for lemmatization and part-of-speech tagging
- Definitions are fetched from Wiktionary; internet connection required
- Only words above the chosen difficulty rating are included

## To-do

- Collecting ideas

## Bugs, issues, suggestions
- Capitalization
- Improve the example sentences. Right now only part of the sentences are used.

- Please contact me, I am open to all suggestions.

NOTE: I AM PRETTY NEW TO THIS WHOLE GITHUB/ OPEN-SOURCE THING
If I did anything wrong, please let me know.

## License

MIT, credits are appreciated
