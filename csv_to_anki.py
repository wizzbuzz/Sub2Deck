import random
import genanki
import csv

def main():
  # Prompt user for CSV input file and open it
  file = open(input("Please enter .csv input file: ") + ".csv")
  # Prompt user for Anki deck name
  anki_file_name = input("Please enter Anki Deck name: ")
  # Read the CSV file as a dictionary
  reader = csv.DictReader(file, delimiter=",")

  # Define the Anki card model (fields and template)
  model = genanki.Model(
    1607392319,
    'Simple Model',
    fields=[
      {'name': 'Question'},
      {'name': 'Answer'},
    ],
    templates=[
      {
        'name': 'Card 1',
        'qfmt': '{{Question}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
      },
    ])

  # Create a new Anki deck with a random ID and the user-provided name
  deck = genanki.Deck(
    random.randrange(1 << 30, 1 << 31),
    anki_file_name)

  # Iterate over each row in the CSV and create a note for each word
  for row in reader:
    # Build the back side of the card with definition and example sentence
    backSide = row["definition"] + "<br>Example sentence:<br>" + row["sentence in script"]
    # Create a new note with the word as the question and the backSide as the answer
    note = genanki.Note(
        model=model,
        fields=[row["word"], backSide]
    )
    deck.add_note(note)

  # Save the deck to an .apkg file for import into Anki
  genanki.Package(deck).write_to_file(f'{anki_file_name}.apkg')
  print(f"Succesfully created {anki_file_name}.apkg")