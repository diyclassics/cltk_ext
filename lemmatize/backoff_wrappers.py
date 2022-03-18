import subprocess
import shlex
import re
import string
from typing import List, Dict, Tuple, Set, Any, Generator

from cltk.alphabet.lat import JVReplacer
from ensemble import EnsembleDictLemmatizer
from utils import cli_installed, pad_punc, remove_macrons
from pprint import pprint

replacer = JVReplacer()

class LatmorEnsembleLemmatizer(EnsembleDictLemmatizer):
    """
    This is a wrapper that allows Latmor to be used with the CLTK Ensemble
    Lemmatizer by 1. calling fst-infl and latmor using subprocess and 2. parsing
    stdout.

    The following programs need to be installed separately for this wrapper
    to work:
    - fst-infl
    - latmor

    LatMor can be found at https://www.cis.uni-muenchen.de/~schmid/tools/LatMor/

    References:
    - Springmann, U., Schmid, H., and Najock, D. 2016. “LatMor: A Latin
        Finite-State Morphology Encoding Vowel Quantity.” Open Linguistics
        2(1): 386–92. doi:10.1515/opli-2016-0019.
    """

    def __init__(self, backoff: object = None,
        fstinfl_location='/usr/local/bin/',
        latmor_location='/usr/local/bin/',
        normalize=True,
        verbose=False):

        self.fstinfl_location = fstinfl_location
        self.latmor_location = latmor_location
        self.latmor_dict = {}
        self.normalize = normalize

        if not cli_installed('fst-infl'):
            raise Exception('fst-infl is not installed')

        # Use Latmor to create dictionary for DictLemmatizer
        super().__init__(lemmas=self.latmor_dict, verbose=verbose, backoff=backoff, source='Latmor output')

    def resolve_latmor_verb(self, verb: str) -> str:
        text = f'{verb}<V><pres><ind><active><sg><1>'
        cmd1 = ['echo', text]
        cmd2 = f'{self.fstinfl_location}fst-infl {self.latmor_location}latmor/latmor-gen.a'
        p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
        result = subprocess.run(shlex.split(cmd2), stdin=p1.stdout, capture_output=True).stdout.decode().strip()
        resolved_verb = result.split('\n')[1]
        if resolved_verb.startswith('no result'):
            return None
        resolved_verb = remove_macrons(resolved_verb)
        return resolved_verb

    def build_dict(self: object, tokens: List[str]) -> None:
        """
        Builds lemmatizer-specific dictionary on demand
        :param tokens: List of tokens used to build dictionary
        """
        tokens = sorted(set(tokens))
        text = "\n".join(tokens) # Concatenate with \n for Latmor processing

        cmd1 = ['echo', text]
        cmd2 = f'{self.fstinfl_location}fst-infl {self.latmor_location}latmor/latmor-robust.a'
        p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
        result = subprocess.run(shlex.split(cmd2), stdin=p1.stdout, capture_output=True).stdout.decode()

        results = re.split(r'> ', result)[1:]
        
        tokens_ = []
        lemmas = []
        
        for result in results:
            result = result.replace('<PREF>','')
            token_ = result.strip().split('\n')[0].replace('> ', '')
            tokens_.append(token_)
            if token_ in string.punctuation:
                lemmas.append([token_])
            else:
                entries = result.strip().split('\n')[1:]            
                entries_ = []
                for entry in entries:
                    entry_ = re.match(r'^(\w+?)<', entry)
                    if entry_:
                        entry_ = entry_[1]
                        if '<V>' in entry:
                            entry_ = self.resolve_latmor_verb(entry_)
                        entries_.append(entry_)
                entries_ = sorted(list(set([entry for entry in entries_ if entry])))
                if self.normalize:
                    entries_ = [replacer.replace(entry) for entry in entries_]
                lemmas.append(entries_)

        lemma_pairs = zip(tokens_, lemmas)

        lemma_pairs = [pair for pair in lemma_pairs if pair[0] not in self.latmor_dict.keys()] # Do not update existing key
        self.latmor_dict.update(lemma_pairs)

    def choose_tag(self: object, tokens: List[str], index: int, history: List[str]):
        """
        Looks up token in ``lemmas`` dict and returns the corresponding
        value as lemma.
        :rtype: str
        :type tokens: list
        :param tokens: List of tokens to be lemmatized
        :type index: int
        :param index: Int with current token
        :type history: list
        :param history: List with tokens that have already been lemmatized; NOT USED
        """
        keys = self.lemmas.keys()
        if tokens[index] in keys:
            return self.lemmas[tokens[index]]
        else:
            return None

    def lemmatize(self: object, tokens: List[str], lemmas_only=False):
        text = pad_punc(" ".join(tokens)) # Handle punctuation
        tokens = text.split()
        self.build_dict(tokens)
        tags = self.tag(tokens)
        if lemmas_only:
            tags_flat = []
            for tag in tags:
                token = tag[0]
                values_ = []
                if tag[1]:
                    values_.extend(list(tag[1][0].values()))
                values_ = [item for subl in values_ for item in subl]
                if values_:
                    tags_flat.append((token, values_))
                else:
                    tags_flat.append((token, None))
            return tags_flat
        else:
            return tags

    def __repr__(self: object):
        if self.source:
            return f'<{type(self).__name__}: {self.source}>'
        else:
            return f'<{type(self).__name__}: {self.repr.repr(self.lemmas)}>'
