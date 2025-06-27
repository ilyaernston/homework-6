# 3D Submarines Game

A 3D variant of the classic Battleship game, where two players face off on a three-layer battlefield:

* **Deep Sea (Layer 0):** Submarines
* **Sea Level (Layer 1):** Destroyers
* **Air (Layer 2):** Jets

Each fleet also has a single **General** piece, whose destruction grants an instant victory.

---

## Overview

Players take turns firing at coordinates on the opponent’s hidden 3D board. Each target yields one of three outcomes:

* **Miss (O)**: no vessel at that location.
* **Hit (X)**: vessel damaged but still afloat (only applies to multi-segment ships).
* **Kill (!)**: vessel destroyed (or General hit).

The game ends when either:

1. The **General** of one side is destroyed (instant win).
2. **All other vessels** (submarines, destroyers, jets) have been sunk.

---

## Rules

1. **Setup**

   * Board dimensions: configurable (depth × rows × columns).
   * Vessel counts: configurable, but exactly one **General** per player is mandatory.
   * Pieces are placed **randomly** with no overlaps or out-of-bounds placements.

2. **Vessels**

   * **Submarine** (Layer 0): 3 cells in a straight line; destroyed by a single hit
   ```
    .  .  .         #
    #  #  #     or  #
    .  .  .         #
    ```
   * **Destroyer** (Layer 1): 4 cells in a straight line; requires hits on all segments
   ```
    .  .  .  .          #
    #  #  #  #     or   #
    .  .  .  .          #
    .  .  .  .          #
    ```
   * **Jet** (Layer 2): asymmetric cross (3‑cell & 4‑cell lines intersecting); destroyed by a single hit
   ```
    . # .        .  .  #  .
    # # #   or   #  #  #  #
    . # .        .  .  #  .
    . # .
    ```
   * **General** (Any Layer): single cell; destroyed by a single hit, resulting in instant game over.

3. **Turn Sequence**

   1. Current player enters a coordinate in `z,y,x` format (depth,row,column).
   2. The board reveals **O**, **X**, or **!** at that location.
   3. If player **Miss**, turn is passes to opponent.
   4. If the player **Hit/Kill**, same player may fires again (if that was not a winning strike).

4. **Win Conditions**

   * **General down**: the moment a player’s General is hit, the attacker wins.
   * **Fleet elimination**: when all non-General vessels are destroyed, the attacker wins.

5. **Commands**

   * `show`: reveal your own board.
   * `quit`: abort the current game.

---

## Main Implementation Features

* **Objects Used**:

    * `Coordinate`: A type alias for a 3-tuple (x, y, z) representing a board cell in 3D.
    * `Signal` (Enum): Shot outcome constants: MISS, HIT or KILL.
    * `PieceType` (Enum): Vessel kinds: SUBMARINE, DESTROYER, JET and GENERAL.
    * `_normalize(offsets)` (function): Translates a set of 2D (x,y) offsets so their minimum becomes (0,0).
    * `_get_rotations(base)` (function): Generates all unique 90° rotations of a given 2D shape.
    * `_SHAPES_2D` (dict): Maps each PieceType to its list of normalized, rotated 2D shapes.
    * `Piece` (dataclass): Tracks vessel type, occupied 3D coordinates, which cells have been hit, ensures per-piece hit logic.
    * `Board3D` (class): Manages a depth×rows×cols grid: places pieces randomly (no overlaps), records occupancy, and resolves incoming shots.
    * `Game` (class): Orchestrates two Board3D instances, handles the turn-based CLI loop, input parsing, shot boards, and win conditions.

* **Extensibility**:

  * New vessel types can be addad via new `PieceType` entries and 2D offset lists in `_SHAPES_2D` without altering core game logic.

* **Checks for Non-Overlapping Placement**:

  * Up to 1000 placement attempts performed per piece, with boundary and overlap checks.
  * Layer assignment executed based on piece type, with `GENERAL` allowed on any depth.

* **Testing**:

  * IPython script (`test_hw6.ipy`) performs tests of utilities, placement, hit logic and game flow.

---

## Running the Game

1. **Launch**:

   ```bash
   python submarines_game.py
   ```
2. Enter coordinates in suggested format, or use `show` / `quit` commands.
