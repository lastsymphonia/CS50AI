from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
Line_A_zero = And(AKnight, AKnave)
knowledge0 = And(
    Not(Biconditional(AKnight, AKnave)),
    Biconditional(AKnight, Line_A_zero),
    Biconditional(AKnave, Not(Line_A_zero))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
Line_A_one = And(AKnave, BKnave)
knowledge1 = And(
    Not(Biconditional(AKnight, AKnave)),
    Not(Biconditional(BKnight, BKnave)),
    Biconditional(AKnight, Line_A_one),
    Biconditional(AKnave, Not(Line_A_one)),
)



# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
Line_A_two = Biconditional(AKnight, BKnight)
Line_B_two = Biconditional(AKnight, BKnave)
knowledge2 = And(
    Not(Biconditional(AKnight, AKnave)),
    Not(Biconditional(BKnight, BKnave)),
    Biconditional(AKnight, Line_A_two),
    Biconditional(AKnave, Not(Line_A_two)),
    Biconditional(BKnight, Line_B_two),
    Biconditional(BKnave, Not(Line_B_two)),

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
"""
Biconditionals will not work, since none of the sentence crossreferences another
characters (self-contained) and model checking is not holistic (i.e. checking
Character A ignores the assignment of Characters B and C.)
"""
Line_A_three_either = AKnight
Line_A_three_or = AKnave

Line_B_three = CKnave
Line_C_three = AKnight
knowledge3 = And(
    Biconditional(AKnight, Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    Biconditional(CKnight, Not(CKnave)),

    Implication(BKnave,
        And(
            Implication(AKnight, And(Line_A_three_either, Not(Line_A_three_or))),
            Implication(AKnave, Not(Line_A_three_either)),
            Not(Line_B_three)
        )
    ),
    Implication(BKnight,
        And(
            Implication(AKnight, And(Line_A_three_or, Not(Line_A_three_either))),
            Implication(AKnave, Line_A_three_either),
            Line_B_three
        )
    ),
    Implication(CKnight, Line_C_three),
    Implication(CKnave, Not(Line_C_three))
)




def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
