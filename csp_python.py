"""
The Zebra puzzle. Let's see if I can solve it with or-tools. - SK
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

# Modified from  https://developers.google.com/optimization/cp/cryptarithmetic

from ortools.sat.python import cp_model


def CPIsFun():
    # Constraint programming engine
    model = cp_model.CpModel()

    # There are five houses in the Zebra puzzle.  Each of the following variables will be assigned to one of the five houses.
    # We will model this with NewIntVar(1, 5).
    colors = "blue red green ivory yellow".split()
    nationalities = "Englishman Spaniard Ukrainian Norwegian Japanese".split()
    pets = "dog snails fox horse zebra".split()
    drinks = "coffee tea milk oj water".split()
    smokes = "Kools Chesterfield OldGold LuckyStrike Parliament".split()

    # We need to group variables in lists to be able to use
    # the global constraint AllDifferent later
    colorcons = []
    for color in colors:
        colorcons.append(model.NewIntVar(1, 5, color))

    nationcons = []
    for nation in nationalities:
        nationcons.append(model.NewIntVar(1, 5, nation))

    petcons = []
    for pet in pets:
        petcons.append(model.NewIntVar(1, 5, pet))

    drinkcons = []
    for drink in drinks:
        drinkcons.append(model.NewIntVar(1, 5, drink))

    smokecons = []
    for smoke in smokes:
        smokecons.append(model.NewIntVar(1, 5, smoke))

    # Constraints -  every category needs an assignment to distinct house numbers
    model.AddAllDifferent(colorcons)
    model.AddAllDifferent(nationcons)
    model.AddAllDifferent(petcons)
    model.AddAllDifferent(drinkcons)
    model.AddAllDifferent(smokecons)

    # Now add the constraints of the description statements
    # a. The Englishman lives in the red house.
    model.Add(nationcons[nationalities.index('Englishman')] == colorcons[
        colors.index('red')])

    # b. The Spaniard owns the dog.
    model.Add(nationcons[nationalities.index('Spaniard')] == petcons[
        pets.index('dog')])

    # c. Coffee is drunk in the green house.
    model.Add(
        drinkcons[drinks.index('coffee')] == colorcons[colors.index('green')])

    # d. The Ukrainian drinks tea.
    model.Add(drinkcons[drinks.index('tea')] == nationcons[nationalities.index(
        'Ukrainian')])

    # e. The green house is immediately to the right of the ivory house.
    model.Add(
        colorcons[colors.index('green')] == colorcons[colors.index('ivory')] +
        1)

    # f. The Old Gold smoker owns snails.
    model.Add(
        smokecons[smokes.index('OldGold')] == petcons[pets.index('snails')])

    # g. Kools are smoked in the yellow house.
    model.Add(
        smokecons[smokes.index('Kools')] == colorcons[colors.index('yellow')])

    # h. Milk is drunk in the middle house.
    model.Add(drinkcons[drinks.index('milk')] == 3)  # 3 is the middle house

    # i. The Norwegian lives in the first house.
    model.Add(nationcons[nationalities.index('Norwegian')] ==
              1)  # 1 is the first house

    # j. The man who smokes Chesterfields lives in the house next to the man with the fox.
    # Constrain the difference between the two houses to be 1 or -1.
    # We could also use the absolute value constraint, but I think this is simpler.
    diffvar1 = model.NewIntVarFromDomain(cp_model.Domain.FromValues([-1, 1]),
                                         'dist_chesterfield_fox')
    model.Add(diffvar1 == petcons[pets.index('fox')] -
              smokecons[smokes.index('Chesterfield')])

    # k. Kools are smoked in the house next to the house where the horse is kept.
    diffvar2 = model.NewIntVarFromDomain(cp_model.Domain.FromValues([-1, 1]),
                                         'dist_kools_horse')
    model.Add(diffvar2 == petcons[pets.index('horse')] -
              smokecons[smokes.index('Kools')])

    # l. The Lucky Strike smoker drinks orange juice.
    model.Add(drinkcons[drinks.index('oj')] == smokecons[smokes.index(
        'LuckyStrike')])

    # m. The Japanese smokes Parliaments.
    model.Add(nationcons[nationalities.index('Japanese')] == smokecons[
        smokes.index('Parliament')])

    # # n. The Norwegian lives next to the blue house.
    diffvar3 = model.NewIntVarFromDomain(cp_model.Domain.FromValues([-1, 1]),
                                         'dist_american_blue')
    model.Add(diffvar3 == colorcons[colors.index('blue')] -
              nationcons[nationalities.index('Norwegian')])

    # Solve model.
    solver = cp_model.CpSolver()
    solution_printer = cp_model.VarArraySolutionPrinter([
        item
        for sublist in [colorcons, nationcons, drinkcons, petcons, smokecons]
        for item in sublist
    ])
    status = solver.SearchForAllSolutions(model, solution_printer)

    print()
    print('Statistics')
    print('  - status          : %s' % solver.StatusName(status))
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f s' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())


def main():
    CPIsFun()
