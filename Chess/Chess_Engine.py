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
        self.inCheck = False  # flag for check
        self.pins = []  # list of pinned pieces
        self.checks = []  # list of checks

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
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            king_row = self.whiteKingLocation[0]
            king_col = self.whiteKingLocation[1]
        else:
            king_row = self.blackKingLocation[0]
            king_col = self.blackKingLocation[1]
        
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block or move king
                moves = self.get_all_possible_moves()
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]  # enemy piece causing the check
                valid_squares = []  # squares that pieces can move to block the check
                # if knight, must capture knight or move king, other pieces can be blocked
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]  # knight can only be blocked by capturing it
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)  # check[2] and check[3] are the directions of the check
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:  # once you reach the piece and add it, stop checking further squares in this direction
                            break

                # get rid of any moves that don't block the check or move the king
                for i in range(len(moves) - 1, -1, -1):  # go through the list backwards when removing elements
                    if moves[i].pieceMoved[1] != 'K':  # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in valid_squares:  # move doesn't block or capture
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in check so all moves are valid
            moves = self.get_all_possible_moves()
        
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
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):  # iterate through the list of pins backwards
            if self.pins[i][0] == r and self.pins[i][1] == c:  # square is pinned
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])  # save the direction of the pin
                self.pins.remove(self.pins[i])  # remove the pin from the list to avoid double counting
                break

        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][c] == "--":  # 1 square move
                if not piece_pinned or pin_direction == (-1, 0):
                    if r == 6 and self.board[r - 2][c] == "--":  # 2 square move
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # capture to the left
                if self.board[r - 1][c - 1][0] == "b":  # enemy piece to capture
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:  # capture to the right
                if self.board[r - 1][c + 1][0] == "b":  # enemy piece to capture
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))

        if not self.whiteToMove:  # black pawn moves
            if self.board[r + 1][c] == "--":  # 1 square move
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # 2 square move
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # capture to the left
                if self.board[r + 1][c - 1][0] == "w":  # enemy piece to capture
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # capture to the right
                if self.board[r + 1][c + 1][0] == "w":  # enemy piece to capture
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''
    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):  # iterate through the list of pins backwards
            if self.pins[i][0] == r and self.pins[i][1] == c:  # square is pinned
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])  # save the direction of the pin
                if self.board[r][c][1] != 'Q':  # can't remove queen from pin list, only rooks and bishops can be pinned
                    self.pins.remove(self.pins[i])  # remove the pin from the list to avoid double counting
                break

        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up, down, left, right
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # rook can move up to 7 squares in each direction
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # check if still on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):  # check if the piece is pinned and if the move is in the direction of the pin
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
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):  # iterate through the list of pins backwards
            if self.pins[i][0] == r and self.pins[i][1] == c:  # square is pinned
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])  # save the direction of the pin
                self.pins.remove(self.pins[i])  # remove the pin from the list to avoid double counting
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.whiteToMove else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:  # knight can move regardless of pin direction
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

    def check_for_pins_and_checks(self):
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row, start_col = self.whiteKingLocation
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row, start_col = self.blackKingLocation

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # second allied piece, no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        # 5 possibilities here in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction one square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type == 'B') or (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break  # stop looking in this direction
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':  # enemy knight attacking king
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks



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