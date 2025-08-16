import random
import genanki
import csv

def main():
  file = open(input("Please enter .csv input file: "))
  anki_file_name = input("Please enter Anki Deck name: ")
  reader = csv.reader(file, delimiter=",")

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

  deck = genanki.Deck(
    random.randrange(1 << 30, 1 << 31),
    anki_file_name)

  for row in reader:
      note = genanki.Note(
          model=model,
          fields=[row[0], row[-1]]
      )
      deck.add_note(note)

  genanki.Package(deck).write_to_file(f'{anki_file_name}.apkg')
  print(f"Succesfully created {anki_file_name}.apkg")