"""
3D Submarines Game implementation.
- Three layers: deep sea (submarines), sea-level (destroyers), air (jets). Unique General piece: single hit ends the game
- Random piece placement, turn-based CLI play
- Extensibilty supported via easy addition new PieceTypes and shapes in _SHAPES_2D
"""
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import Tuple, Set, Dict, List

# Alias for a 3D coordinate: (x, y, depth)
Coordinate = Tuple[int, int, int]

### Helper functions ###

def _normalize(offsets: List[Tuple[int,int]]) -> Set[Tuple[int,int]]:
    """
    Shift a list of 2D offsets so the minimum x,y becomes (0,0).
    Ensures shapes can be compared and rotated consistently.
    """
    xs = [x for x,y in offsets]
    ys = [y for x,y in offsets]
    min_x, min_y = min(xs), min(ys)
    return {(x - min_x, y - min_y) for x,y in offsets}


def _get_rotations(base: List[Tuple[int,int]]) -> List[Set[Tuple[int,int]]]:
    """
    Generate all unique 90° rotations of a base 2D shape.
    Helps place vessels in any orientation.
    """
    configs: List[Set[Tuple[int,int]]] = []
    current = base
    for _ in range(4):
        norm = _normalize(current)
        if norm not in configs:
            configs.append(norm)
        # Rotate 90° around origin: (x,y) -> (y, -x)
        current = [(y, -x) for x,y in current]
    return configs

### Define classes ###

class Signal(Enum):
    """
    Outcome of a firing action on the board.
    MISS: no piece at target
    HIT: piece was hit but not sunk
    KILL: piece is destroyed (or General hit)
    """
    MISS = auto()
    HIT  = auto()
    KILL = auto()

class PieceType(Enum):
    """
    Different vessel types in the game.
    SUBMARINE: length 3, single-hit
    DESTROYER: length 4, multi-hit
    JET: cross shape, single-hit
    GENERAL: single cell, instant game over
    """
    SUBMARINE = auto()
    DESTROYER = auto()
    JET       = auto()
    GENERAL   = auto()

# Define PieceTypes and piece shapes
_SHAPES_2D: Dict[PieceType, List[Set[Tuple[int,int]]]] = {
    PieceType.SUBMARINE: _get_rotations([(0,0), (1,0), (2,0)]),
    PieceType.DESTROYER: _get_rotations([(0,0), (1,0), (2,0), (3,0)]),
    PieceType.JET: _get_rotations([(-1,0),(0,0),(1,0),(0,-1),(0,1),(0,2)]),
    PieceType.GENERAL: [_normalize([(0,0)])]
}

@dataclass
class Piece:
    """
    Represents a single vessel on the board.
    - piece_type: type of vessel
    - coords: set of occupied 3D coordinates
    - hits: subset of coords that have been hit
    """
    piece_type: PieceType
    coords: Set[Coordinate]
    hits: Set[Coordinate]

    def register_hit(self, coord: Coordinate) -> Signal:
        """
        Process an incoming shot at coord.
        Returns Signal.MISS, Signal.HIT, or Signal.KILL.
        """
        if coord not in self.coords:
            return Signal.MISS
        self.hits.add(coord)
        if self.piece_type in (PieceType.SUBMARINE, PieceType.JET, PieceType.GENERAL):
            return Signal.KILL
        if self.hits == self.coords:
            return Signal.KILL
        return Signal.HIT

class Board3D:
    """
    3D game board: depth layers of rows x cols.
    Tracks piece placement and resolves incoming fire.
    """
    def __init__(self, depth: int, rows: int, cols: int):
        self.depth = depth
        self.rows = rows
        self.cols = cols
        self.occupied: Dict[Coordinate, Piece] = {}
        self.pieces: List[Piece] = []

    def place_all(self, counts: Dict[PieceType, int]):
        """
        Randomly place all vessels according to counts.
        Strictly checks for exactly one General, and that no more than
        the computable max of any other piece can fit on a single rows×cols layer.
        """
        # must have exactly one General
        if counts.get(PieceType.GENERAL, 0) != 1:
            raise ValueError("Exactly one General required")

        # for each non‐General type, check maximum packable on a single layer
        for ptype, num in counts.items():
            if ptype is PieceType.GENERAL:
                continue

            # take the “base” rotation (horizontal) to get its bounding box
            base_shape = _SHAPES_2D[ptype][0]
            xs = [x for x, y in base_shape]
            ys = [y for x, y in base_shape]
            width  = max(xs) - min(xs) + 1
            height = max(ys) - min(ys) + 1

            # estimate how many fit if laid out horizontally vs. vertically
            #   horizontal orientation → dims (height × width)
            cap_horiz = (self.rows // height) * (self.cols // width)
            #   vertical (rotated) orientation → dims (width × height)
            cap_vert  = (self.rows // width) * (self.cols // height)

            max_count = max(cap_horiz, cap_vert)
            if num > max_count:
                raise ValueError(
                    f"Cannot place {num} {ptype.name.lower()}s on a "
                    f"{self.rows}×{self.cols} layer; maximum is {max_count}"
                )

        # all checks passed → actually place them
        for ptype, num in counts.items():
            for _ in range(num):
                self._place_random(ptype)

    def _place_random(self, ptype: PieceType):
        """
        Attempt up to 1000 times to place a piece without overlap.
        Depth layer for most vessels is fixed by type; General is random.
        """
        shapes = _SHAPES_2D[ptype]
        for _ in range(1000):
            shape = random.choice(shapes)
            max_dx = max(x for x,y in shape)
            max_dy = max(y for x,y in shape)
            z = random.randrange(self.depth) if ptype is PieceType.GENERAL else ptype.value - 1
            x0 = random.randrange(self.cols - max_dx)
            y0 = random.randrange(self.rows - max_dy)
            coords = {(x0 + x, y0 + y, z) for x,y in shape}
            if any(c in self.occupied for c in coords):
                continue
            piece = Piece(ptype, coords, set())
            for c in coords:
                self.occupied[c] = piece
            self.pieces.append(piece)
            return
        raise RuntimeError(f"Cannot place piece {ptype}")

    def receive_fire(self, coord: Coordinate) -> Signal:
        """
        Called when opponent fires at coord.
        Returns the resulting Signal.
        """
        piece = self.occupied.get(coord)
        if not piece:
            return Signal.MISS
        return piece.register_hit(coord)

    def all_non_general_sunk(self) -> bool:
        """
        Check if all vessels (except the General) are sunk.
        Used to detect alternate win condition.
        """
        return all(
            (p.piece_type == PieceType.GENERAL) or (p.hits == p.coords)
            for p in self.pieces
        )

class Game:
    """
    Runs a two-player match:
    - Initializes two boards with random placement
    - Manages player's turns, input parsing and hit/miss feedback
    - Supports 'show' to reveal own board and 'quit' to abort game
    """
    def __init__(self, depth: int, rows: int, cols: int, counts: Dict[PieceType,int]):
        self.boards = [Board3D(depth, rows, cols), Board3D(depth, rows, cols)]
        for b in self.boards:
            b.place_all(counts)
        self.shots = [set(), set()]
        self.current = 0

    def _print_view(self):
        """
        Display current player's known hits/misses grid layer by layer.
        Unfired cells show '.', hits 'X', kills '!'.
        """
        opp = 1 - self.current
        print(f"Player {self.current+1}'s view (levels 0..{self.boards[0].depth-1}):")
        for z in range(self.boards[0].depth):
            print(f" Level {z}:")
            for y in range(self.boards[0].rows):
                row = []
                for x in range(self.boards[0].cols):
                    coord = (x,y,z)
                    if coord in self.shots[self.current]:
                        sig = self.boards[opp].receive_fire(coord)
                        char = {'MISS':'O','HIT':'X','KILL':'!'}[sig.name]
                        row.append(char)
                    else:
                        row.append('.')
                print(' '.join(row))
            print()

    def start(self):
        """
        Run the main game loop until quit or victory.
        Reads user input of form "z,y,x", or commands 'show'/'quit'.
        """
        print("Starting 3D Submarines Game!")
        while True:
            self._print_view()
            cmd = input(f"Player {self.current+1}, enter 'depth,row,column' ('z,y,x'), or 'show', or 'quit': ").strip().lower()
            if cmd == 'quit':
                print("Game aborted.")
                return
            if cmd == 'show':
                self._reveal_board(self.current)
                continue
            try:
                z,y,x = map(int, cmd.split(','))
                coord = (x,y,z)
            except ValueError:
                print("Invalid format. Use 'depth,row,column' (z,y,x).")
                continue
            if coord in self.shots[self.current]:
                print("Already fired at that coordinate.")
                continue
            # Record shot and resolve
            self.shots[self.current].add(coord)
            # Capture piece reference before firing
            target_board = self.boards[1-self.current]
            piece = target_board.occupied.get(coord)
            sig = target_board.receive_fire(coord)
            print({Signal.MISS: "Miss!", Signal.HIT: "Hit!", Signal.KILL: "Kill!"}[sig])
            if sig is Signal.MISS:
                self.current = 1 - self.current
            else:
                # Win if General destroyed
                if piece and piece.piece_type == PieceType.GENERAL:
                    print(f"Player {self.current+1} wins (General down)!")
                    return
                # Win if all other vessels are sunk
                if target_board.all_non_general_sunk():
                    print(f"Player {self.current+1} wins (all non-General sunk)!")
                    return
                # Otherwise, same player continues firing

    def _reveal_board(self, player: int):
        """
        Print full layout of 'player's board for debugging or concede.
        '#' marks occupied cells.
        """
        print(f"--- Player {player+1} Board Reveal ---")
        board = self.boards[player]
        for z in range(board.depth):
            print(f" Level {z}:")
            for y in range(board.rows):
                line = ' '.join('#' if (x,y,z) in board.occupied else '.'
                                 for x in range(board.cols))
                print(line)
            print()

### Main function ###

if __name__ == '__main__':
    def run_game():
        print("Welcome to 3D Battleship Game! \n\nLet's configure your match\n")
        while True:
            # Board size setup
            depth = 3 # always exactly 3 layers
            while True:
                try: 
                    rows  = int(input("Enter board ROWS per layer (e.g. 5): "))
                    cols  = int(input("Enter board COLS per layer (e.g. 5): "))
                    
                    if depth < 1 or rows < 1 or cols < 1:
                        raise ValueError
                    
                    if min(rows, cols) < 3 or max(rows, cols) < 4:
                        raise ValueError("Board must be at least 3×4 (in some orientation).")
                    
                    break
                except ValueError as e:
                    print(f"Invalid: {e}\n")

            # Piece counts setup
            counts: Dict[PieceType,int] = {}
            for ptype in (PieceType.SUBMARINE, PieceType.DESTROYER, PieceType.JET):
                while True:
                    try:
                        num = int(input(f"Enter number of {ptype.name.lower()}s: "))
                        if num < 0:
                            raise ValueError
                        counts[ptype] = num
                        break
                    except ValueError:
                        print("  → Please enter a non-negative integer.\n")
            counts[PieceType.GENERAL] = 1  # always exactly one General

            # Summary & final command
            print("\nConfiguration summary:")
            print(f"  Depth layers: {depth}")
            print(f"  Board size:   {rows}×{cols} (rows×cols per layer)")
            for ptype, num in counts.items():
                print(f"  {ptype.name.capitalize():10s}: {num}")

            # final prompt: start, reset, or quit
            while True:
                cmd = input("\nType 'start' to begin, 'reset' to reconfigure, or 'quit' to abort: ")\
                          .strip().lower()
                if cmd == 'start':
                    game = Game(depth, rows, cols, counts)
                    game.start()
                    return
                elif cmd == 'reset':
                    print("\nRestarting configuration...\n")
                    break   # breaks inner prompt loop → back to outer while → reconfigure
                elif cmd == 'quit':
                    print("Game setup aborted.")
                    return
                else:
                    print("Invalid command. Please enter 'start', 'reset', or 'quit'.")

    run_game()


