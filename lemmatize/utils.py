import shutil
import unicodedata
import re

def cli_installed(filename:str) -> bool:
    """Checks to see if a program is available from the command line,
    testing with a call to ```which```."""
    return True if shutil.which(filename) else False

def pad_punc(text:str) -> str:
    """
    Given a string of punctuated text, add space between punctuation and word characters,
    so that text can be split on whitespace
    
    >>> pad_punc('Dum differtur, vita transcurrit.')
    'Dum differtur , vita transcurrit .'
    """
    import string   
    text = text.translate(str.maketrans({key: " {0} ".format(key) for key in string.punctuation}))
    text = re.sub('\s{2,}', ' ', text)
    return text.strip()

def remove_macrons(text:str) -> str:
    '''Replace macrons in Latin text'''
    vowels = 'aeiouyAEIOUY'
    vowels_with_macrons = 'āēīōūȳĀĒĪŌŪȲ'
    replacement_dictionary = {k: v for k, v in zip(vowels_with_macrons, vowels)}    
    
    temp = unicodedata.normalize('NFC', text)

    for k, v in replacement_dictionary.items():
        temp = temp.replace(k, v)
    else:
        temp = temp

    return temp   

