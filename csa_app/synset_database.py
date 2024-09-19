import typing
from nltk.corpus import wordnet as wn

from . import wse_models

class SynsetDatabaseWordNet:

    def get_noun_synsets(self, lemma):
        # lookup all the senses for a word from wordnet
        synset_options = []
        added_map = {}
        for wn_synset in wn.synsets(lemma, pos=wn.NOUN):
            if wn_synset._name not in added_map:
                synset_options.append(wse_models.SynsetOption(wn_synset._name, wn_synset._definition))
                added_map[wn_synset._name] = True
            else:
                1+2 # why here?!
                
        return synset_options

    def get_verb_synsets(self, lemma):
        # lookup all the senses for a word from wordnet
        synset_options = []
        added_map = {}
        for wn_synset in wn.synsets(lemma, pos=wn.VERB):
            if wn_synset._name not in added_map:
                synset_options.append(wse_models.SynsetOption(wn_synset._name, wn_synset._definition))
                added_map[wn_synset._name] = True
            else:
                1+2 # why here?!
                
        return synset_options

    def get_parent_ids(self, synset_id) -> typing.List[str]:
        p_ids = set()

        to_get = [synset_id]
        while len(to_get) > 0:
            s_id = to_get.pop()
            s = wn.synset(s_id)

            parents = s.hypernyms()
            for p in parents:
                p_id = p._name
                p_ids.add(p_id)
                to_get.append(p_id)

        return list(p_ids)
