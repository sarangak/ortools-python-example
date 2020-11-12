"""
The Zebra puzzle.
https://en.wikipedia.org/wiki/Zebra_Puzzle

There are five houses in a row, each of a different color, that are inhabited
by five people of different nationalities, with different pets, favorite
drinks, and favorite brands of cigarettes. Use the clues below to determine who
owns the zebra and who drinks water.

Associations/Constraints:
a. The Englishman lives in the red house.
b. The Spaniard owns the dog.
c. Coffee is drunk in the green house.
d. The Ukrainian drinks tea.
e. The green house is immediately to the right of the ivory house.
f. The Old Gold smoker owns snails.
g. Kools are smoked in the yellow house.
h. Milk is drunk in the middle house.
i. The Norwegian lives in the first house.
j. The man who smokes Chesterfields lives in the house next to the man with the fox.
k. Kools are smoked in the house next to the house where the horse is kept.
l. The Lucky Strike smoker drinks orange juice.
m. The Japanese smokes Parliaments.
n. The Norwegian lives next to the blue house.
"""

# Modified from https://developers.google.com/optimization/cp/cryptarithmetic

from ortools.sat.python import cp_model


def puzzle_constraints():
    model = cp_model.CpModel()

    # There are five houses in the Zebra puzzle. We will number the houses 1
    # through 5 going from left to right. To model the assignments of color,
    # nationality, etc. each possible value is assigned a variable that is
    # constrained to be an integer from 1 to 5: `NewIntVar(1,5)`. Then the
    # solver DSL is used to further constrain these values based on the rules
    # of the puzzle.
    colors = "blue red green ivory yellow".split()
    nationalities = "Englishman Spaniard Ukrainian Norwegian Japanese".split()
    pets = "dog snails fox horse zebra".split()
    drinks = "coffee tea milk oj water".split()
    smokes = "Kools Chesterfield OldGold LuckyStrike Parliament".split()

    # We need to group variables in lists to be able to use
    # the global constraint AllDifferent later
    colorgroup = []
    for color in colors:
        colorgroup.append(model.NewIntVar(1, 5, color))

    nationgroup = []
    for nation in nationalities:
        nationgroup.append(model.NewIntVar(1, 5, nation))

    petgroup = []
    for pet in pets:
        petgroup.append(model.NewIntVar(1, 5, pet))

    drinkgroup = []
    for drink in drinks:
        drinkgroup.append(model.NewIntVar(1, 5, drink))

    smokegroup = []
    for smoke in smokes:
        smokegroup.append(model.NewIntVar(1, 5, smoke))

    variables = colorgroup + nationgroup + petgroup + drinkgroup + smokegroup

    # Initial constraint
    # Every category needs an assignment to distinct house numbers
    model.AddAllDifferent(colorgroup)
    model.AddAllDifferent(nationgroup)
    model.AddAllDifferent(petgroup)
    model.AddAllDifferent(drinkgroup)
    model.AddAllDifferent(smokegroup)

    # Now add the constraints of the description statements
    # a. The Englishman lives in the red house.
    model.Add(nationgroup[nationalities.index('Englishman')] == colorgroup[
        colors.index('red')])

    # b. The Spaniard owns the dog.
    model.Add(nationgroup[nationalities.index('Spaniard')] == petgroup[
        pets.index('dog')])

    # c. Coffee is drunk in the green house.
    model.Add(drinkgroup[drinks.index('coffee')] == colorgroup[colors.index(
        'green')])

    # d. The Ukrainian drinks tea.
    model.Add(drinkgroup[drinks.index('tea')] == nationgroup[
        nationalities.index('Ukrainian')])

    # e. The green house is immediately to the right of the ivory house.
    model.Add(colorgroup[colors.index('green')] ==
              colorgroup[colors.index('ivory')] + 1)

    # f. The Old Gold smoker owns snails.
    model.Add(
        smokegroup[smokes.index('OldGold')] == petgroup[pets.index('snails')])

    # g. Kools are smoked in the yellow house.
    model.Add(smokegroup[smokes.index('Kools')] == colorgroup[colors.index(
        'yellow')])

    # h. Milk is drunk in the middle house.
    model.Add(drinkgroup[drinks.index('milk')] == 3)  # 3 is the middle house

    # i. The Norwegian lives in the first house.
    model.Add(nationgroup[nationalities.index('Norwegian')] ==
              1)  # 1 is the first house

    # j. The man who smokes Chesterfields lives in the house next to the man with the fox.
    # Constrain the difference between the two houses to be 1 or -1.
    # We could also use the absolute value constraint, but I think this is simpler.
    diffvar1 = model.NewIntVarFromDomain(cp_model.Domain.FromValues([-1, 1]),
                                         'dist_chesterfield_fox')
    model.Add(diffvar1 == petgroup[pets.index('fox')] -
              smokegroup[smokes.index('Chesterfield')])

    # k. Kools are smoked in the house next to the house where the horse is kept.
    diffvar2 = model.NewIntVarFromDomain(cp_model.Domain.FromValues([-1, 1]),
                                         'dist_kools_horse')
    model.Add(diffvar2 == petgroup[pets.index('horse')] -
              smokegroup[smokes.index('Kools')])

    # l. The Lucky Strike smoker drinks orange juice.
    model.Add(drinkgroup[drinks.index('oj')] == smokegroup[smokes.index(
        'LuckyStrike')])

    # m. The Japanese smokes Parliaments.
    model.Add(nationgroup[nationalities.index('Japanese')] == smokegroup[
        smokes.index('Parliament')])

    # # n. The Norwegian lives next to the blue house.
    diffvar3 = model.NewIntVarFromDomain(cp_model.Domain.FromValues([-1, 1]),
                                         'dist_american_blue')
    model.Add(diffvar3 == colorgroup[colors.index('blue')] -
              nationgroup[nationalities.index('Norwegian')])

    return model, variables


def main():
    model, variables = puzzle_constraints()

    # Set up the solver
    solver = cp_model.CpSolver()
    solution_printer = cp_model.VarArraySolutionPrinter(
        [item for item in variables])

    # Solve the puzzle
    status = solver.SearchForAllSolutions(model, solution_printer)
    print()
    print('Statistics')
    print('  - status          : %s' % solver.StatusName(status))
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f s' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())
