from z3 import Solver, Bool, And, Or, Not, Implies, sat, unsat
class SudokuSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.solver = None
        self.variables = None

    def create_variables(self):
        """
        Set self.variables as a 3D list containing the Z3 variables. 
        self.variables[i][j][k] is true if cell i,j contains the value k+1.
        """
        self.variables = [[[Bool(f"x_{i}_{j}_{k}") for k in range(9)] for j in range(9)] for i in range(9)]

    def encode_rules(self):
        """
        Encode the rules of Sudoku into the solver.
        """
        # Each cell must contain exactly one value
        for i in range(9):
            for j in range(9):
                # At least one value
                self.solver.add(Or([self.variables[i][j][k] for k in range(9)]))
                # At most one value
                for k1 in range(9):
                    for k2 in range(k1 + 1, 9):
                        self.solver.add(Not(And(self.variables[i][j][k1], self.variables[i][j][k2])))
        
        # Each row must contain each value exactly once
        for i in range(9):
            for k in range(9):
                # At least one occurrence in each row
                self.solver.add(Or([self.variables[i][j][k] for j in range(9)]))
                # At most one occurrence in each row (already handled by cell constraints)
        
        # Each column must contain each value exactly once
        for j in range(9):
            for k in range(9):
                # At least one occurrence in each column
                self.solver.add(Or([self.variables[i][j][k] for i in range(9)]))
                # At most one occurrence in each column (already handled by cell constraints)
        
        # Each 3x3 subgrid must contain each value exactly once
        for box_i in range(3):
            for box_j in range(3):
                for k in range(9):
                    # At least one occurrence in each box
                    self.solver.add(Or([
                        self.variables[box_i * 3 + i][box_j * 3 + j][k] 
                        for i in range(3) for j in range(3)
                    ]))
                    # At most one occurrence in each box (already handled by cell constraints)

    def encode_puzzle(self):
        """
        Encode the initial puzzle into the solver.
        """
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] != 0:
                    self.solver.add(self.variables[i][j][self.puzzle[i][j] - 1])

    def extract_solution(self, model):
        """
        Extract the solution from the model.
        """
        solution = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                for k in range(9):
                    if model.evaluate(self.variables[i][j][k]):
                        solution[i][j] = k + 1
        return solution
    
    def solve(self):
        """
        Solve the Sudoku puzzle.
        """
        self.solver = Solver()
        self.create_variables()
        self.encode_rules()
        self.encode_puzzle()
        
        if self.solver.check() == sat:
            model = self.solver.model()
            return self.extract_solution(model)
        return None

    def solve_with_precluded_solution(self, solution):
        """
        Find a second, third, or another solution to the Sudoku puzzle.
        """
        self.solver = Solver()
        self.create_variables()
        self.encode_rules()
        self.encode_puzzle()
        
        # Add constraint to exclude the precluded solution
        exclusion = Or([
            Not(self.variables[i][j][solution[i][j] - 1])
            for i in range(9) for j in range(9)
        ])
        
        self.solver.add(exclusion)
        
        if self.solver.check() == sat:
            model = self.solver.model()
            return self.extract_solution(model)
        return None

def main():
    puzzles = [
        # World's hardest puzzle
        [
            [8, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 6, 0, 0, 0, 0, 0],
            [0, 7, 0, 0, 9, 0, 2, 0, 0],
            [0, 5, 0, 0, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 4, 5, 7, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 3, 0],
            [0, 0, 1, 0, 0, 0, 0, 6, 8],
            [0, 0, 8, 5, 0, 0, 0, 1, 0],
            [0, 9, 0, 0, 0, 0, 4, 0, 0]
        ]
    ]

    for index, puzzle in enumerate(puzzles):
        print(f"\nAttempting to solve puzzle {index + 1}:")
        
        for row in puzzle:
            print(row)

        solver = SudokuSolver(puzzle)
        solution = solver.solve()

        if solution:
            print(f"Solution for puzzle {index + 1}:")
            
            for row in solution:
                print(row)
            
            # Check for another solution
            another_solution = solver.solve_with_precluded_solution(solution)
            
            if another_solution:
                print(f"Another solution for puzzle {index + 1}:")
                for row in another_solution:
                    print(row)
            else:
                print(f"Solution for puzzle {index + 1} is unique.")
        else:
            print(f"Puzzle {index + 1} has no solution.")

if __name__ == "__main__":
    main()
