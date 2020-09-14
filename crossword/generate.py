import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # in every node, compare each possible word to the given length; remove if it doesn't match
        for node in list(self.domains.keys()): # is this the right way to delete? will it cause errors?
            for word in list(self.domains[node]):
                if len(word) != node.length:
                    self.domains[node].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Remove words from nodes if there's no word in its overlap that works (if overlapped characters are the same)
        revised = False
        if self.crossword.overlaps[x, y]:
            (i, j) = self.crossword.overlaps[x, y]

            for word_x in list(self.domains[x]):
                conflict = True
                for word_y in list(self.domains[y]):
                    if word_x[i] == word_y[j]:
                        conflict = False
                if conflict:
                    self.domains[x].remove(word_x)
                    revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # if no arcs used, do ac3 on all arcs
        if arcs == None:
            arcs = self.domains.keys()
        # else make arcs from nodes
        queue = []
        for i in arcs:
            for j in arcs:
                if i != j:
                    queue.append((i,j))

        # Use revised on every arc to make arc consistent. If node in arc is revised, all arcs with that node must be rechecked.
        while queue:
            (node_x, node_y) = queue[0]
            queue = queue [1:]
            if self.revise(node_x, node_y):
                if len(self.domains[node_x]) == 0:
                    return False
                for node in self.crossword.neighbors(node_x):
                    if node != node_y:
                        queue.append((node, node_x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # return True if all variables are filled, else return false
        nodes = list(self.domains.keys())
        for node in assignment:
            nodes.remove(node)
            if assignment[node] == None:
                return False
        if len(nodes) == 0:
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for node in assignment:
            # Checks variable words are correct length
            if len(assignment[node]) != node.length:
                return False

            # Check overlaps consitency
            node_neighbours = self.crossword.neighbors(node)
            for neighbor in node_neighbours:
                if neighbor in assignment.keys():
                    (i,j) = self.crossword.overlaps[node, neighbor]
                    if assignment[node][i] != assignment[neighbor][j]:
                        return False

            # Check if each variable unique
            for other_node in assignment:
                if other_node != node and assignment[node] == assignment[other_node]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # for each word, check how many words any overlapped var rules out.
        sorted_values = []
        node_neighbours = [node for node in self.crossword.neighbors(var) if node not in assignment.keys()]
        for word in self.domains[var]:
            removed_words = 0
            for node in node_neighbours:
                (i,j) = self.crossword.overlaps[var, node]
                for other_word in self.domains[node]:
                    if word[i] != other_word[j]:
                        removed_words += 1
            sorted_values.append((word, removed_words))
        # then sort it based on no. of words ruled out and return best value (lowest no.)
        sorted_values.sort(key=lambda word: word[1])
        sorted_values = [word for (word, count) in sorted_values]
        return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get list of nodes that aren't assigned, then pick the variable with smallest domain, then highest degree.
        unassigned_nodes = [node for node in self.domains.keys() if node not in assignment.keys()]
        node_choices = [len(self.domains[node]) for node in unassigned_nodes]
        smallest = min(node_choices)
        mrv_nodes = [node for node in unassigned_nodes if len(self.domains[node]) == smallest]
        if len(mrv_nodes)  >  1:
            node = max(mrv_nodes, key=lambda node: len(self.crossword.neighbors(node)))
            return node
        else:
            return mrv_nodes[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # check for complete assignment
        if self.assignment_complete(assignment):
            return assignment

        # if not complete, recusively call backtrack to fill each variable till assignment is complete.
        # check if all assignment is consistent on each run.    
        var = self.select_unassigned_variable(assignment)
        for value in list(self.order_domain_values(var, assignment)):
            assignment_test = assignment.copy()
            # AC3 makes things slower. Investigate?
            # arcs = [node for node in self.domains.keys() if node not in assignment.keys()]
            # self.ac3(arcs)
            assignment_test[var] = value
            if self.consistent(assignment_test):
                assignment = assignment_test
                result = self.backtrack(assignment)

                if result != None:
                    return result
            assignment.pop(var, None)


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
