import typing
import json


class SynsetOption:

    def __init__(self, id:str, gloss:str):
        self.id = id
        self.gloss = gloss


class WordSenseEvaluation:

    def __init__(self,
                 sentence,
                 word,
                 synset_options:typing.List[SynsetOption],
                 ):
        self.sentence = sentence
        self.word = word
        self.synset_options = synset_options 

    @property
    def content(self):
        return f"What is the meaning of the word {self.word} in '{self.sentence}'?"


class DefaultWsePrompt:

    def __init__(self,
            topic:WordSenseEvaluation,
        ):
        self.topic = topic
        self.letter_option_map = None

    @property
    def content(self) -> str:
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

        if len(self.topic.synset_options) > len(letters):
            raise ValueError("Not enough letters to support this prompt") 
        options = [
            f"{letter}) {t.gloss}" for letter, t in zip(letters, self.topic.synset_options)
        ]

        if self.letter_option_map is None:
            self.letter_option_map = {}
            for letter, t in zip(letters, self.topic.synset_options):
                self.letter_option_map[letter] = t

        options_str = "\n".join(options)

        return f'''
What is the meaning of the concept "{self.topic.word}" in "{self.topic.sentence}"?

Options:
{options_str}
'''
