# 3D Submarines Game

A 3D variant of the classic Battleship game, where two players face off on a three-layer battlefield:

* **Deep Sea (Layer 0):** Submarines
* **Sea Level (Layer 1):** Destroyers
* **Air (Layer 2):** Jets

Each fleet also has a single **General** piece (placed on any layer), whose destruction grants an instant victory.

---

## Overview

Players take turns firing at coordinates on the opponent’s hidden 3D board. Each target yields one of three outcomes:

* **Miss (O)**: no vessel at that location
* **Hit (X)**: vessel damaged but still afloat (only applies to multi-segment ships)
* **Kill (!)**: vessel destroyed (or General hit)

The game ends when either:

1. The **General** of one side is destroyed (instant win), or
2. **All other vessels** (submarines, destroyers, jets) have been sunk.

---

## Rules of the Game

1. **Setup**

   * Board dimensions: configurable (depth × rows × columns)
   * Vessel counts: configurable, but exactly one **General** per player
   * Pieces are placed **randomly** with no overlaps or out-of-bounds placements

2. **Vessels**

   * **Submarine** (Layer 0): 3 cells in a straight line; destroyed by a single hit
   * **Destroyer** (Layer 1): 4 cells in a straight line; requires hits on all segments
   * **Jet** (Layer 2): asymmetric cross (3‑cell & 4‑cell lines intersecting); destroyed by a single hit
   * **General** (Any Layer): single cell; destroyed by a single hit → instant game over

3. **Turn Sequence**

   1. Current player enters a coordinate in `z,y,x` format (depth,row,column).
   2. The board reveals **O**, **X**, or **!** at that location.
   3. **Miss** → turn passes to opponent.
   4. **Hit/Kill** → same player may fire again (unless game-ending condition).

4. **Win Conditions**

   * **General down**: the moment a player’s General is hit, the attacker wins.
   * **Fleet elimination**: when all non-General vessels of one side are destroyed, the attacker wins.

5. **Commands**

   * `show`: reveal your own board (for debugging or concession)
   * `quit`: abort the current game

---

## Main Implementation Features

* **Object-Oriented Design**: clear separation of concerns with classes:

  * `Piece` tracks type, occupied coordinates, and hit status
  * `Board3D` manages placement, occupancy, and shot resolution
  * `Game` handles turn-taking, input parsing, and win logic

* **Enums for Safety & Clarity**:

  * `Signal` (`MISS`, `HIT`, `KILL`)
  * `PieceType` (`SUBMARINE`, `DESTROYER`, `JET`, `GENERAL`)

* **Dynamic Shape Rotation**:

  * `_normalize` & `_get_rotations` generate and standardize all 90° orientations of any vessel footprint
  * Extensible: add new `PieceType` entries and 2D offset lists in `_SHAPES_2D` without altering core logic

* **Random Non-Overlapping Placement**:

  * Up to 1000 placement attempts per piece, with boundary and overlap checks
  * Layer assignment based on piece type, with `GENERAL` allowed on any depth

* **Command-Line Interface**:

  * Simple turn-based loop with visual text grid per layer
  * Intuitive symbols: `.` (unknown), `O` (miss), `X` (hit), `!` (kill)

* **Testing**:

  * IPython script (`test_submarines.ipy`) verifies utilities, placement, hit logic, and win conditions

---

## Running the Game

1. **Install requirements** (if any).
2. **Launch**:

   ```bash
   python submarines_game.py
   ```
3. Enter coordinates as prompted, or use `show` / `quit` commands.

Enjoy sinking—and avoiding—the General!
