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

        self.whiteToMove = True
        self.moveLog = []

    '''
    Move the piece from the start square to the end square, and also update the board
    '''
    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"  # empty the start square
        self.board[move.endRow][move.endCol] = move.pieceMoved  # move the piece to the end square
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players

    '''
    switch position of the pieces back to the way it was before the move was made
    '''
    def undo_move(self):
        if len(self.moveLog) != 0:  # make sure there is a move to undo
            move = self.moveLog.pop()  # get the last move from the move log
            self.board[move.startRow][move.startCol] = move.pieceMoved  # put the piece back to its original square
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # put the captured piece back on the board
            self.whiteToMove = not self.whiteToMove  # switch turns back


    '''
    All moves considering checks
    '''
    def get_valid_moves(self):
        return self.get_all_possible_moves()  # for now, we will not worry about checks

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
                    if piece == "p":  # pawn
                        self.get_pawn_moves(r, c, moves)
                    elif piece == "R":  # rook
                        self.get_rook_moves(r, c, moves)
                    self.move_functions[piece](self, r, c, moves)  # call the appropriate move function based on the piece type
        return moves
    

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''
    def get_pawn_moves(self, r, c, moves):
        pass

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''
    def get_rook_moves(self, r, c, moves):
        pass

    




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