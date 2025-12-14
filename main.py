import chess
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

BOARD_SIZE = 8
explored = []

#HELPERS 
def square_to_xy(square):
    x = chess.square_file(square)
    y = chess.square_rank(square)
    return (x + 0.5, y + 0.5)

#MINIMAX TRACE 
def minimax(board, depth, alpha, beta, maximizing, path):
    if depth == 0 or board.is_game_over():
        val = evaluate(board)
        explored.append({"path": path.copy(), "value": val, "move": None, "depth": depth})
        return val

    legal_moves = list(board.legal_moves)

    if maximizing:
        max_eval = -9999
        for move in legal_moves:
            board.push(move)
            path.append((square_to_xy(move.from_square), square_to_xy(move.to_square)))
            current = minimax(board, depth-1, alpha, beta, False, path)
            board.pop()
            path.pop()
            explored.append({"path": path.copy(), "value": current, "move": move.uci(), "depth": depth})
            max_eval = max(max_eval, current)
            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 9999
        for move in legal_moves:
            board.push(move)
            path.append((square_to_xy(move.from_square), square_to_xy(move.to_square)))
            current = minimax(board, depth-1, alpha, beta, True, path)
            board.pop()
            path.pop()
            explored.append({"path": path.copy(), "value": current, "move": move.uci(), "depth": depth})
            min_eval = min(min_eval, current)
            beta = min(beta, min_eval)
            if beta <= alpha:
                break
        return min_eval

def evaluate(board):
    values = {chess.PAWN:1, chess.KNIGHT:3, chess.BISHOP:3,
              chess.ROOK:5, chess.QUEEN:9}
    score = sum(len(board.pieces(p, True))*v - len(board.pieces(p, False))*v
                for p,v in values.items())
    return score

#DRAWING 
def draw_board(ax, board):
    ax.clear()
    for x in range(8):
        for y in range(8):
            color = "#EEEED2" if (x+y)%2==0 else "#769656"
            ax.add_patch(plt.Rectangle((x,y),1,1,facecolor=color,edgecolor='black',linewidth=0.25))

    unicode_pieces = {'P':"♙",'N':"♘",'B':"♗",'R':"♖",'Q':"♕",'K':"♔",
                      'p':"♟",'n':"♞",'b':"♝",'r':"♜",'q':"♛",'k':"♚"}

    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            x,y = square_to_xy(sq)
            ax.text(x,y,unicode_pieces[piece.symbol()],fontsize=28,ha="center",va="center",zorder=5)

    ax.set_xlim(0,8)
    ax.set_ylim(0,8)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")

#ROOT MINIMAX WITH TIME TRACKING
def minimax_root(board, depth):
    legal_moves = list(board.legal_moves)
    best_move = None

    start_time = time.time()  
    if board.turn:  
        max_eval = -9999
        for move in legal_moves:
            board.push(move)
            val = minimax(board, depth-1, -9999, 9999, False, [(square_to_xy(move.from_square), square_to_xy(move.to_square))])
            board.pop()
            if val > max_eval:
                max_eval = val
                best_move = move
    else:  
        min_eval = 9999
        for move in legal_moves:
            board.push(move)
            val = minimax(board, depth-1, -9999, 9999, True, [(square_to_xy(move.from_square), square_to_xy(move.to_square))])
            board.pop()
            if val < min_eval:
                min_eval = val
                best_move = move
    end_time = time.time()  

    return best_move, end_time - start_time

# VISUALIZATION 
def visualize_decision_tree(board):
    fig, ax = plt.subplots(figsize=(6,6))
    draw_board(ax, board)

    def init():
        draw_board(ax, board)
        return []

    def update(frame):
        node = explored[frame]
        for artist in list(ax.artists):
            try:
                artist.remove()
            except Exception:
                pass

        draw_board(ax, board)
        info_text = ax.text(0.01,0.99,
                            f"Node {frame+1}/{len(explored)}\nDepth: {node.get('depth')}\nMove: {node.get('move')}\nEval: {node.get('value')}",
                            transform=ax.transAxes,fontsize=10,va="top",zorder=10,
                            bbox=dict(facecolor="white",alpha=0.8,edgecolor="none"))

        for f,t in node["path"]:
            ax.annotate("", xy=t, xytext=f, arrowprops=dict(arrowstyle="->", lw=2, color='red'), zorder=15)
        return []

    ani = animation.FuncAnimation(fig, update, frames=len(explored),
                                  init_func=init, interval=25, repeat=False)
    plt.show()

if __name__ == "__main__":
    fen = input("Enter FEN (or press Enter for starting position): ").strip()
    board = chess.Board() if fen=="" else chess.Board(fen)

    depth = int(input("Search depth (recommended 2-4): ") or "3")

    print("\nRunning search to find best move...\n")
    best_move, duration = minimax_root(board, depth)
    print(f"Best move found: {best_move.uci()}")
    print(f"Total explored nodes: {len(explored)}")
    print(f"Time taken to find best move: {duration:.4f} seconds")

    input("\nPress Enter to start visualization...")
    visualize_decision_tree(board)
