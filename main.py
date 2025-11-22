import chess

# === Get board position (FEN or default start) ===
fen = input("Enter FEN (or press Enter for starting position): ")

if fen.strip():
    try:
        board = chess.Board(fen)
    except ValueError:
        print("Invalid FEN! Using default starting position.")
        board = chess.Board()
else:
    board = chess.Board()

# === Unicode chess pieces ===
UNICODE_PIECES = {
    chess.PAWN: '♙',
    chess.KNIGHT: '♘',
    chess.BISHOP: '♗',
    chess.ROOK: '♖',
    chess.QUEEN: '♕',
    chess.KING: '♔',
    "p": '♟', "n": '♞', "b": '♝', "r": '♜', "q": '♛', "k": '♚'
}

# === Print board function ===
def print_unicode_board(board):
    if board.turn == chess.WHITE:
        ranks = range(8, 0, -1)   # White at bottom
        files = range(8)          # a → h
    else:
        ranks = range(1, 9)       # Black at bottom
        files = range(7, -1, -1)  # h → a

    print("\n    a b c d e f g h")
    for rank in ranks:
        line = f"{rank}  "
        for file in files:
            square = chess.square(file, rank - 1)
            piece = board.piece_at(square)
            if piece:
                symbol = UNICODE_PIECES[piece.piece_type] if piece.color == chess.WHITE else UNICODE_PIECES[piece.symbol()]
            else:
                symbol = '·'
            line += symbol + " "
        print(line)
    print("    a b c d e f g h\n")

print_unicode_board(board)
print("Turn:", "White" if board.turn == chess.WHITE else "Black")
print("Castling rights:", board.castling_rights)
print("Full move number:", board.fullmove_number)

# === Piece values for evaluation ===
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 1000
}

# === Evaluation function (material + positional bonuses + check bonus) ===
def evaluate(board):
    score = 0
    for piece_type, value in piece_values.items():
        white_squares = board.pieces(piece_type, chess.WHITE)
        black_squares = board.pieces(piece_type, chess.BLACK)
        
        score += len(white_squares) * value
        score -= len(black_squares) * value

        # Simple positional bonus: central squares
        for sq in white_squares:
            file = chess.square_file(sq)
            rank = chess.square_rank(sq)
            if 2 <= file <= 5 and 2 <= rank <= 5:  # d4,e4,d5,e5
                score += 0.5
        for sq in black_squares:
            file = chess.square_file(sq)
            rank = chess.square_rank(sq)
            if 2 <= file <= 5 and 2 <= rank <= 5:
                score -= 0.5

    # Bonus for checks
    if board.is_check():
        if board.turn == chess.WHITE:
            score -= 0.5  # Black threatens check
        else:
            score += 0.5  # White threatens check

    return score

print("Evaluation score (positive for White, negative for Black):", evaluate(board))

# === Minimax search with basic alpha-beta pruning ===
def minimax(board, depth, is_maximizing, alpha=-9999, beta=9999):
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if is_maximizing:
        max_eval = -9999
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False, alpha, beta)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = 9999
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True, alpha, beta)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval

# === Find best move function ===
def find_best_move(board, depth):
    best_move = None
    if board.turn == chess.WHITE:
        best_score = -9999
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, False)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
    else:  # Black
        best_score = 9999
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, True)
            board.pop()
            if score < best_score:
                best_score = score
                best_move = move
    return best_move, best_score

# === Run the engine ===
depth = 3  # Depth 3 gives better tactical awareness
best_move, best_score = find_best_move(board, depth)
print("Best move:", best_move)
print("Best move evaluation score:", best_score)
