# IPython test script for 3D Submarines Game

# Assuming the main game script is saved as 'hw6.py' in the same directory.

from main import (
    _normalize, _get_rotations,
    PieceType, Signal, Piece,
    Board3D, Game
)

### Helper function tests ###

# Test normalization
offsets = [(2,5), (3,7), (4,5)]
normed = _normalize(offsets)
assert normed == {(0,0), (1,2), (2,0)}, f"_normalize failed: {normed}"

# Test rotations
base_line = [(0,0), (1,0)]
rots = _get_rotations(base_line)
assert len(rots) == 2, f"Expected 2 unique rotations, got {len(rots)}"

### Board3D placement and firing tests ###

# Create a small board and place exactly one of each piece
counts = {PieceType.SUBMARINE:1, PieceType.DESTROYER:1, PieceType.JET:1, PieceType.GENERAL:1}
board = Board3D(depth=3, rows=5, cols=5)
board.place_all(counts)
# Ensure four pieces placed
assert len(board.pieces) == 4, f"Expected 4 pieces, got {len(board.pieces)}"
# Fire at each piece's first coordinate to test signals
for piece in board.pieces:
    coord = next(iter(piece.coords))
    sig = board.receive_fire(coord)
    if piece.piece_type == PieceType.DESTROYER:
        # First hit on destroyer is HIT
        assert sig == Signal.HIT, f"Destroyer hit should return HIT, got {sig_last} insted"
        # Hit remaining segments
        for c in (piece.coords - {coord}):
            sig_last = board.receive_fire(c)
        assert sig_last == Signal.KILL, f"Destroyer last hit should return KILL, got {sig_last} insted"
    else:
        # All other pieces kill on first hit
        assert sig == Signal.KILL, f"{piece.piece_type} should kill on first hit, got {sig_last} insted"

# Test non-general win condition
# Sink all non-general pieces on board2
board2 = Board3D(depth=3, rows=5, cols=5)
board2.place_all(counts)
# Sink subs, destroyer, jet
for p in board2.pieces:
    if p.piece_type != PieceType.GENERAL:
        for c in p.coords:
            board2.receive_fire(c)
assert board2.all_non_general_sunk(), "Not all non-general pieces are recognized as sunk"

### Main flow test ###

# Simulate minimal game ending by killing General
game = Game(depth=3, rows=5, cols=5, counts=counts)
# Force place a General at known position
gen_piece = next(p for p in game.boards[1].pieces if p.piece_type == PieceType.GENERAL)
gen_coord = next(iter(gen_piece.coords))
# Player 1 fires on General
sig = game.boards[1].receive_fire(gen_coord)
assert sig == Signal.KILL, f"Killing General should return KILL, got {sig} insted"

print("All tests passed successfully!")
