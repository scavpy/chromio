
===================
Chromio Game Design
===================

A variant of the "Flood It" game genre (where the goal is to fill a grid of cells
with all one colour by repeated flood-fill from a fixed location, with the player
choosing the next colour to fill with.

In this variant of the game:

 * The grid is a hexagonal tiling.
 * Flooding begins at the cental tile of the grid.
 * Cells are filled with little coloured icons instead of flat colours.
 * There are buttons also labelled with coloured icons, by which the next colour is chosen.
 * There is no enforced limit on the number of button presses (i.e. you can't lose, but you
   can try to do better)

Game States
-----------

0. Initially, the grid is randomly filled, and the icon buttons are shown.

1. When an icon button is pressed, altered cells are drawn spiralling out from the centre.

2. When the grid is filled, the number of moves and average number of moves are displayed, and
   a button to start a new game.


Screen Layout
-------------

A squarish area containing the hexagon grid, a rectangular area containing a 3x2 grid of icon buttons.



