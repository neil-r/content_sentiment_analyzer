import typing
from pydantic import BaseModel

from csa_app.model import Content
from csa_app.wse_models import WordSenseEvaluation, DefaultWsePrompt

class MultipleChoiceResponse(BaseModel):
    letter:str


def extract_synset_id(multiple_choice_process_func, content:Content, lemma:str, synset_database, consider_nouns:bool = True, consider_verbs:bool = True) -> typing.Tuple[typing.Optional[str],float, dict|str]:

    synset_options = []
    if consider_nouns:
        synset_options = synset_database.get_noun_synsets(lemma)
    if consider_verbs:
        if len(synset_options) == 0:
            synset_options = synset_database.get_verb_synsets(lemma)
    if len(synset_options) == 1:
        return (synset_options[0].id, 0, "Only 1 synset applicable")
    elif len(synset_options) > 1:
        evaluation = WordSenseEvaluation(content.body,lemma,synset_options)
        prompt = DefaultWsePrompt(evaluation)
        response, duration, message = multiple_choice_process_func(prompt.content)
        return prompt.letter_option_map[response.letter].id, duration, message
    return None,0,"No matching synsets"