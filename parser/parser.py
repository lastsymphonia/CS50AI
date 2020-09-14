import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | DP VP | S Adv | Adv S | S NP VP | S DP VP | S Conj S
AP -> Adj | Adj AP | Adv AP
NP -> N | AP NP | N PP | NP Conj NP | DP Conj NP | NP Conj DP
DP -> Det N | DP Conj DP | Det AP NP | Det N PP
PP -> P NP | P DP
VP -> V | V NP | V NP PP | V PP | VP Conj VP | Adv V | V Adv | V DP | V DP PP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # convert sentence to words
    s = nltk.word_tokenize(sentence)
    # remove any word not containing an alphabetical character
    s = [word.lower() for word in s if any(char.isalpha() for char in word)]
    return s


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # lambda function for finding NP labels and finding subtrees containing NP
    label_test = lambda tree: (tree.label() == "NP" or tree.label() == "DP")
    subtree_test = lambda tree: any(label_test(subtree) for subtree in tree.subtrees() if subtree != tree)
    # extract NP chunks following above functions
    noun_phrase = [subtree for subtree in tree.subtrees() if label_test(subtree) and not subtree_test(subtree)]
    return noun_phrase


if __name__ == "__main__":
    main()
