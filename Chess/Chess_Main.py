import pygame as pg
import Chess_Engine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''
def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

'''
The main driver for our code. This will handle user input and updating the graphics
'''
def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    gs = Chess_Engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a move is made
    load_images()
    running = True
    sqelected_square = ()  # no square is selected initially, keep track of the last click of the user (tuple: (row, col))
    player_clicks = []  # keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False

            # Mouse handler
            elif e.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()  # (x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                print(row, col)
                if sqelected_square == (row, col):  # user clicked the same square twice
                    sqelected_square = ()  # deselect
                    player_clicks = []  # clear player clicks
                else:
                    sqelected_square = (row, col)
                    player_clicks.append(sqelected_square)
                    print(player_clicks)
                if len(player_clicks) == 2:  # after second click
                    move = Chess_Engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.get_chess_notation())
                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                    sqelected_square = ()  # reset user clicks
                    player_clicks = []
            # Key handler
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:  # undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()

'''
Responsible for all the graphics within a current game state.
'''
def draw_game_state(screen, gs):
    draw_board(screen)  # draw squares on the board
    # add in piece highlighting or move suggestions (later)
    draw_pieces(screen, gs.board)   # draw pieces on top of those squares

'''
Draw the squares on the board. The top left square is always light.
'''
def draw_board(screen):
    colors = [pg.Color("white"), pg.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pg.draw.rect(screen, color, pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))



if __name__ == "__main__":
    main()