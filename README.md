# A snake AI that never dies

This project implements a snake game and an AI playing the game.
The core goal is to implement the AI such that it will never die, and grow as fast as possible.

The snake AI is based on Hamiltonian cycles, i.e., paths that traverse every tile exactly once without crossing itself and ending at the start.
The snake always follows a Hamiltonian cycle.
This means, it can always reach all other tiles, simply by following the cycle: it never dies.

[A video of the snake AI playing and winning snake](https://github.com/user-attachments/assets/9b742ae5-6cb8-4087-9752-0e26359940a7)

The basic idea of the algorithm goes as follows.
We assume that the grid has an even number of rows and columns.
Then, we restrict the snake to travel upwards only on odd numbered columns and downwards on even numbered columns.
Similarly, on odd rows, the snake travels right, on even rows the snake travels left.
This restriction prevents the snake form creating one-wide dead ends that it cannot leave anymore and helps with creating Hamiltonian paths.

The snake always follows a Hamiltonian path.
However, the algorithm can optimize the path.
This works as follows:

For each step the snake takes, there are no more than two possible fields it can move to: up or down and left or right, depending on the row and column the head is currently at.
If the snake is touching it self or is adjacent to the boundary of the board, there is only one option.
One of the fields is the next step in the currently planed path, the other skips part of the Hamiltonian cycle.
By comparing the distance from both fields to the fruit along the path, the algorithm chooses the next field. 
The most important part is ensuring that taking the shortcut restitches into a new Hamiltonian path covering the whole board.

[A video of the snake AI playing snake. The planned path of the snake is shown](https://github.com/user-attachments/assets/fb71c206-9e45-461e-8244-b89ed868a27f)

The algorithm for cutting and stitching Hamiltonian cycles is very inefficient but works flawlessly for small board sizes as shown in the video.
