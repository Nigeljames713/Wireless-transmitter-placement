# Wireless Transmitter Placement Visualizer

A GUI-based application that demonstrates the **Backtracking Algorithm** through a simplified wireless transmitter placement problem.

---

## Project Overview

The application finds valid transmitter locations on a grid while maintaining a user-defined minimum separation distance between transmitters.

It demonstrates how backtracking can solve constraint-based placement problems through systematic searching, constraint checking, and decision reversal.

## Features

- Interactive grid-based visualization
- Configurable grid size
- Adjustable number of transmitters
- Customizable minimum separation distance
- First-solution and all-solutions modes
- Step-by-step backtracking visualization
- Animated accepted and rejected positions
- Live statistics and search progress
- Adjustable animation speed

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Tkinter | Graphical user interface |
| Backtracking | Algorithm implementation |

## Application Screenshots

### 1. Application Dashboard



### 2. Wireless Transmitter Placement

![Transmitter Placement](screenshots/02-transmitter-placement.png)

### 3. Backtracking Visualization

![Backtracking Visualization](screenshots/03-backtracking-visualization.png)

### 4. Conflict Detection

![Conflict Detection](screenshots/04-conflict-detection.png)

### 5. Live Statistics

![Live Statistics](screenshots/05-live-statistics.png)

### 6. Placement Configuration

![Separation Settings](screenshots/06-separation-settings.png)

## Algorithm Explanation

The application uses the **Backtracking Algorithm** to find valid transmitter locations.

1. Start with an empty grid.
2. Select a candidate location.
3. Calculate its Euclidean distance from previously selected transmitters.
4. Accept the location if it satisfies the minimum separation constraint.
5. Reject the location if it violates the constraint.
6. If a valid configuration cannot be completed, undo the previous selection and explore another combination.
7. Continue until the requested number of transmitters is placed or all possible configurations have been explored.

## Complexity Analysis

Let:

- V = Total number of candidate grid cells.
- K = Number of transmitters to be placed.

**Time Complexity:** O(V^K) as a conservative upper bound for the search, with pruning reducing the actual search space.

**Auxiliary Space Complexity:** O(K) for the recursive search and selected transmitter locations, excluding GUI storage.

## How to Run

**Step 1:** Clone the repository.

```bash
git clone https://github.com/YOUR-USERNAME/wireless-transmitter-placement.git
```

**Step 2:** Navigate to the project directory.

```bash
cd wireless-transmitter-placement
```

**Step 3:** Run the application.

```bash
python wireless_transmitter_visualizer.py
```

## Run Tests

Execute the built-in test cases:

```bash
python wireless_transmitter_visualizer.py --test
```

## Real-World Relevance

The project demonstrates a simplified model of wireless transmitter placement, where candidate installation locations must satisfy minimum separation constraints.

The same backtracking concept can be adapted to constraint-based resource placement and scheduling problems.

**Note:** This is an educational model. It does not simulate actual radio-frequency propagation, signal strength, terrain, or wireless interference.

---

## Author
Name: Nigel James Noby
Registration number: AJC24CC025
Course: Design and Analysis of Algorithms
