 Wireless Transmitter Placement Visualizer

A GUI-based application that demonstrates the Backtracking Algorithm through a simplified wireless transmitter placement problem.

 Project Overview

This application finds valid transmitter locations on a grid while maintaining a user-defined minimum separation distance between transmitters.

It demonstrates how backtracking can solve constraint-based placement problems through systematic searching and decision reversal.

 Features

- Interactive grid-based visualization
- Configurable grid size
- Adjustable number of transmitters
- Minimum separation configuration
- First-solution and all-solutions modes
- Step-by-step backtracking visualization
- Animated accepted and rejected positions
- Live statistics and search progress
- Adjustable animation speed

 Technologies Used

- Python
- Tkinter
- Backtracking Algorithm

 How to Run

1. Clone or download this repository.
2. Open the project directory.
3. Run:

```bash
python wireless_transmitter_visualizer.py
```

 Run Tests

```bash
python wireless_transmitter_visualizer.py --test
```

 Algorithm

The application uses backtracking to explore possible transmitter locations. A candidate location is accepted only if its Euclidean distance from every previously selected transmitter is at least the configured minimum separation.

If a candidate violates the constraint, it is rejected. If a partial placement cannot be completed, the algorithm backtracks and explores another combination.

 Complexity

The search explores combinations of grid cells, pruning placements that violate the distance constraint.

For a grid containing V candidate cells and K transmitters, the worst-case search is bounded by O(V^K), with pruning reducing the actual search space.

 Note

This is an educational placement model. It does not simulate real radio-frequency propagation, signal strength, or actual wireless interference.
