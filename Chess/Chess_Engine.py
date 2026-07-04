"""
Information about the current state of a chess game
"""

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN","wR"]
        ]

        self.move_functions = {'p': self.get_pawn_moves, 
                               'R': self.get_rook_moves, 
                               'N': self.get_knight_moves, 
                               'B': self.get_bishop_moves, 
                               'Q': self.get_queen_moves, 
                               'K': self.get_king_moves
                            }  # maps piece types to their move functions

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False  # flag for checkmate
        self.staleMate = False  # flag for stalemate

    '''
    Move the piece from the start square to the end square, and also update the board
    '''
    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"  # empty the start square
        self.board[move.endRow][move.endCol] = move.pieceMoved  # move the piece to the end square
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
        # update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        

    '''
    switch position of the pieces back to the way it was before the move was made
    '''
    def undo_move(self):
        if len(self.moveLog) != 0:  # make sure there is a move to undo
            move = self.moveLog.pop()  # get the last move from the move log
            self.board[move.startRow][move.startCol] = move.pieceMoved  # put the piece back to its original square
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # put the captured piece back on the board
            self.whiteToMove = not self.whiteToMove  # switch turns back
            # update the king's location if moved
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)


    '''
    All moves considering checks
    '''
    def get_valid_moves(self):
        # 1) generate all possible moves
        moves = self.get_all_possible_moves()
        # 2) for each move, make the move
        for i in range(len(moves) - 1, -1, -1):  # go through the list backwards when removing elements
            self.make_move(moves[i])
            # 3) generate all opponent's moves
            # 4) for each of the opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.in_check():
                moves.remove(moves[i])  # 5) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undo_move()  # 6) undo the move

        if len(moves) == 0:  # either checkmate or stalemate
            if self.in_check():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves
    
    '''
    Determine if the current player is in check
    '''
    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.square_under_attack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if a square is under attack by the opponent
    '''
    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        opp_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in opp_moves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self):
        moves = []  # list of moves
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns in given row
                turn = self.board[r][c][0]  # get the color of the piece at the square
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):  # check if it's the player's turn
                    piece = self.board[r][c][1]  # get the type of piece at the square
                    self.move_functions[piece](r, c, moves)  # call the appropriate move function based on the piece type
        return moves
    

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''
    def get_pawn_moves(self, r, c, moves):
        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][c] == "--":  # 1 square move
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square move
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # capture to the left
                if self.board[r - 1][c - 1][0] == "b":  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:  # capture to the right
                if self.board[r - 1][c + 1][0] == "b":  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        if not self.whiteToMove:  # black pawn moves
            if self.board[r + 1][c] == "--":  # 1 square move
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square move
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # capture to the left
                if self.board[r + 1][c - 1][0] == "w":  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # capture to the right
                if self.board[r + 1][c + 1][0] == "w":  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''
    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up, down, left, right
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # rook can move up to 7 squares in each direction
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # check if still on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty square, valid move
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece, capture and stop
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece, stop
                        break
                else:  # off board, stop
                    break

    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list
    '''
    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.whiteToMove else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not a friendly piece (empty or enemy)
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    '''
    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonals
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    '''
    Get all the queen moves for the queen located at row, col and add these moves to the list
    '''
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)    # straight lines
        self.get_bishop_moves(r, c, moves)  # diagonals

    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''
    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1),
                    (0, -1),           (0, 1),
                    (1, -1),  (1, 0),  (1, 1))
        ally_color = "w" if self.whiteToMove else "b"
        for m in king_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))



class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]   # piece that is being moved
        self.pieceCaptured = board[self.endRow][self.endCol]    # piece that is being captured
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        print(self.moveID)

    '''
    Override the equals method
    if piece moved, start square, and end square are the same, then the moves are equal
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.startRow == other.startRow and self.startCol == other.startCol and self.endRow == other.endRow and self.endCol == other.endCol and self.pieceMoved == other.pieceMoved and self.pieceCaptured == other.pieceCaptured
        return False
    

    def get_chess_notation(self):
        # you can make this like real chess notation later
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)
    
    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]