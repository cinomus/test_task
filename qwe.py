python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Set up the figure and axis
fig = plt.figure()
ax = fig.add_subplot(111)

# Define the size of the grid
N = 100

# Define the initial state of the grid
grid = np.zeros((N, N))
grid[50, 50] = 1
grid[51, 51] = 1
grid[52, 49:52] = 1


# Define the update function for each frame of the animation
def update(frame_number, grid, N):
    # Copy the current state of the grid to a new array
    new_grid = grid.copy()

    # Iterate over each cell in the grid
    for i in range(N):
        for j in range(N):
            # Count the number of live neighbors for each cell
            neighbor_count = (
                    grid[(i - 1) % N, (j - 1) % N]
                    + grid[(i - 1) % N, j]
                    + grid[(i - 1) % N, (j + 1) % N]
                    + grid[i, (j - 1) % N]
                    + grid[i, (j + 1) % N]
                    + grid[(i + 1) % N, (j - 1) % N]
                    + grid[(i + 1) % N, j]
                    + grid[(i + 1) % N, (j + 1) % N]
            )

            # Apply the rules of the game to determine the new state of each cell
            if grid[i, j] == 1 and neighbor_count < 2:
                new_grid[i, j] = 0
            elif grid[i, j] == 1 and neighbor_count > 3:
                new_grid[i, j] = 0
            elif grid[i, j] == 0 and neighbor_count == 3:
                new_grid[i, j] = 1

    # Update the current state of the grid
    grid[:] = new_grid[:]

    # Clear the axis and plot the updated grid
    ax.clear()
    ax.imshow(grid, cmap="binary")


# Define the animation function
animation = animation.FuncAnimation(fig, update, fargs=(grid, N), frames=100, interval=50)

# Show the animation
plt.show()
