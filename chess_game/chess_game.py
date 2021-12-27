import re
import copy

WHITE = 1
BLACK = -1


def get_square_in_direction(square: str, direction, step: int):
    if square == "":
        return ""
    file = square[0]
    rank = ord(square[1]) - 48
    switcher = {
        'N': chr(ord(file)) + str(rank + step),
        'S': chr(ord(file)) + str(rank - step),
        'E': chr(ord(file) + step) + str(rank),
        'W': chr(ord(file) - step) + str(rank),
        'NE': chr(ord(file) + step) + str(rank + step),
        'NW': chr(ord(file) - step) + str(rank + step),
        'SE': chr(ord(file) + step) + str(rank - step),
        'SW': chr(ord(file) - step) + str(rank - step),
    }
    dest = switcher.get(direction)
    if 'A' <= dest[0] <= 'H' and '1' <= dest[1] <= '8':
        return dest
    else:
        return ""


def get_knight_squares(square: str):
    file = ord(square[0])
    rank = ord(square[1]) - 48
    jumps = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]
    squares = []
    for jump in jumps:
        if 65 <= file + jump[0] <= 72 and 1 <= rank + jump[1] <= 8:
            squares.append(chr(file + jump[0]) + str(rank + jump[1]))
    return squares


def get_pawn_attack_squares(current_square: str, color: int):
    moves = []
    if color == WHITE:
        directions = ['NW', 'NE']
        for direction in directions:
            square = get_square_in_direction(current_square, direction, 1)
            if square == "":
                continue
            else:
                moves.append(square)
    elif color == BLACK:
        directions = ['SW', 'SE']
        for direction in directions:
            square = get_square_in_direction(current_square, direction, 1)
            if square == "":
                continue
            else:
                moves.append(square)
    return moves


def does_square_lie_in_line(check_square, line):
    start = line[1]
    end = line[2]
    squares = get_all_squares_between(start, end)
    return check_square in squares


def get_all_squares_between(start, finish):
    file_start = ord(start[0])
    rank_start = ord(start[1]) - 48
    file_end = ord(finish[0])
    rank_end = ord(finish[1]) - 48
    squares = []
    if file_start == file_end:
        file = file_start
        diff = 1 if file_end > file_start else -1
        for r in range(rank_start+diff, rank_end+diff, 1 if rank_end > rank_start else -1):
            squares.append(chr(file) + str(r))
    elif rank_start == rank_end:
        rank = rank_start
        diff = 1 if file_end > file_start else -1
        for f in range(file_start+diff, file_end+diff, 1 if file_end > file_start else -1):
            squares.append(chr(f) + str(rank))
    else:
        file_dif = 1 if file_end > file_start else -1
        rank_dif = 1 if rank_end > rank_start else -1
        i = 1
        square = chr(file_start + (file_dif * i)) + str(rank_start + (rank_dif * i))
        while square != finish:
            squares.append(square)
            i = i + 1
            square = chr(file_start + (file_dif * i)) + str(rank_start + (rank_dif * i))
        squares.append(square)
    return squares


def is_square_in_same_line(square1, square2):
    return square1[0] == square2[0] or square1[1] == square2[1]


def is_promotion(move):
    piece = move[0]
    target_rank = ord(move[2][1]) - 48
    return (piece.color == WHITE and piece.symbol.upper() == 'P' and target_rank == 8) or \
           (piece.color == BLACK and piece.symbol.upper() == 'P' and target_rank == 1)


def is_castling_long(move):
    piece = move[0]
    init_file = move[1][0]
    end_file = move[2][0]
    return piece.symbol.upper() == 'K' and init_file == 'E' and end_file == 'C'


def is_castling_short(move):
    piece = move[0]
    init_file = move[1][0]
    end_file = move[2][0]
    return piece.symbol.upper() == 'K' and init_file == 'E' and end_file == 'G'


def get_move_indicator(move, move_list):
    file_ambig = False
    rank_ambig = False
    for m in move_list:
        if is_move_same(m, move):
            continue
        if m[0] != move[0]:
            continue
        if m[2] != move[2]:
            continue
        file_ambig, rank_ambig = get_ambig(m[1], move[1])
    if file_ambig and rank_ambig:
        return move[1].lower()
    elif file_ambig:
        return move[1][1].lower()
    elif rank_ambig:
        return move[1][0].lower()
    else:
        return ""


def is_move_same(move1, move2):
    return move1[0] == move2[0] and move1[1] == move2[1] and move1[2] == move2[2]


def get_ambig(square1, square2):
    return square1[0] == square2[0], square1[1] == square2[1]


def get_piece_from_possibles(pieces, identifier):
    for piece in pieces:
        if identifier in [piece.currentSquare.lower(), piece.currentSquare[0].lower(), piece.currentSquare[1].lower()]:
            return piece
    return pieces[0]


def get_pos_from_square(square: str):
    file_num = ord(square[0]) - 65
    rank_num = 8 - (ord(square[1]) - 48)
    return 8*rank_num + file_num


class InValidMove(Exception):
    pass


class Piece:

    def __init__(self, color: int, symbol: str, value: int):
        self.color = color
        self.symbol = symbol
        self.value = value
        self.attackingSquares = []
        self.currentSquare = ""
        self.available_moves = []
        self.validSquareMoves = []
        self.pinned = False
        self.removed = False
        self.attack_computed = False
        self.move_computed = False

    @classmethod
    def WHITE_ROOK(cls):
        return Piece(WHITE, 'R', 5)

    @classmethod
    def WHITE_BISHOP(cls):
        return Piece(WHITE, 'B', 3)

    @classmethod
    def WHITE_QUEEN(cls):
        return Piece(WHITE, 'Q', 9)

    @classmethod
    def WHITE_KING(cls):
        return Piece(WHITE, 'K', 0)

    @classmethod
    def WHITE_KNIGHT(cls):
        return Piece(WHITE, 'N', 3)

    @classmethod
    def WHITE_PAWN(cls):
        return Piece(WHITE, 'P', 1)

    @classmethod
    def BLACK_ROOK(cls):
        return Piece(BLACK, 'r', 5)

    @classmethod
    def BLACK_BISHOP(cls):
        return Piece(BLACK, 'b', 3)

    @classmethod
    def BLACK_QUEEN(cls):
        return Piece(BLACK, 'q', 9)

    @classmethod
    def BLACK_KING(cls):
        return Piece(BLACK, 'k', 0)

    @classmethod
    def BLACK_KNIGHT(cls):
        return Piece(BLACK, 'n', 3)

    @classmethod
    def BLACK_PAWN(cls):
        return Piece(BLACK, 'p', 1)

    @classmethod
    def EMPTY(cls):
        return Piece(0, '.', 0)

    def add_attacking_square(self, square):
        self.attackingSquares.append(square)

    def clear_attacking_square(self):
        self.attackingSquares.clear()

    def place_at(self, square):
        self.currentSquare = square

    def compute_attacking_squares(self, board):
        self.attackingSquares = self.get_attacks(board)
        self.attack_computed = True
        return self.attackingSquares

    def compute_valid_moves(self, board, in_check, attacking_line, checking_squares, castle_long, castle_short):
        self.available_moves = self.get_moves(board)
        self.filter_moves(in_check, attacking_line, checking_squares, castle_long, castle_short, board)
        return self.validSquareMoves

    def is_dead_or_empty(self):
        return self.symbol == '.' or self.removed or self.currentSquare == ""

    def __get_rook_moves(self, board):
        directions = ['N', 'S', 'E', 'W']
        moves = []
        for direction in directions:
            i = 1
            square = get_square_in_direction(self.currentSquare, direction, i)
            while square != "":
                piece = board.get_piece_at(square)
                if piece.is_dead_or_empty():
                    moves.append(square)
                    i = i + 1
                    square = get_square_in_direction(self.currentSquare, direction, i)
                    continue
                elif piece.color != self.color:
                    moves.append(square)
                    break
                else:
                    break
        return moves

    def __get_bishop_moves(self, board):
        directions = ['NW', 'SE', 'NE', 'SW']
        moves = []
        for direction in directions:
            i = 1
            square = get_square_in_direction(self.currentSquare, direction, i)
            while square != "":
                piece = board.get_piece_at(square)
                if piece.is_dead_or_empty():
                    moves.append(square)
                    i = i + 1
                    square = get_square_in_direction(self.currentSquare, direction, i)
                    continue
                elif piece.color != self.color:
                    moves.append(square)
                    break
                else:
                    break
        return moves

    def __get_queen_moves(self, board):
        rook = self.__get_rook_moves(board)
        bishop = self.__get_bishop_moves(board)
        moves = rook + bishop
        return moves

    def __get_king_moves(self, board):
        directions = ['NW', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W']
        moves = []
        for direction in directions:
            square = get_square_in_direction(self.currentSquare, direction, 1)
            if square != "":
                piece = board.get_piece_at(square)
                if piece.is_dead_or_empty() or piece.color != self.color:
                    moves.append(square)
        file = ord(self.currentSquare[0])
        rank = self.currentSquare[1]
        moves.append(chr(file - 2) + rank)
        file = ord(self.currentSquare[0])
        rank = self.currentSquare[1]
        moves.append(chr(file + 2) + rank)
        return moves

    def __get_knight_moves(self, board):
        jumps = get_knight_squares(self.currentSquare)
        move = []
        for square in jumps:
            piece = board.get_piece_at(square)
            if piece.is_dead_or_empty() or piece.color != self.color:
                move.append(square)
        return move

    def __get_pawn_moves(self, board):
        moves = []
        if self.color == WHITE:
            square = get_square_in_direction(self.currentSquare, 'N', 1)
            if square == "":
                pass
            else:
                piece = board.get_piece_at(square)
                if piece.is_dead_or_empty():
                    moves.append(square)
        elif self.color == BLACK:
            square = get_square_in_direction(self.currentSquare, 'S', 1)
            if square == "":
                pass
            else:
                piece = board.get_piece_at(square)
                if piece.is_dead_or_empty():
                    moves.append(square)
        if self.color == WHITE and self.currentSquare[1] == '2':
            square = get_square_in_direction(self.currentSquare, 'N', 2)
            piece = board.get_piece_at(square)
            if piece.is_dead_or_empty():
                moves.append(square)
        elif self.color == BLACK and self.currentSquare[1] == '7':
            square = get_square_in_direction(self.currentSquare, 'S', 2)
            piece = board.get_piece_at(square)
            if piece.is_dead_or_empty():
                moves.append(square)
        if self.color == WHITE:
            directions = ['NW', 'NE']
            for direction in directions:
                square = get_square_in_direction(self.currentSquare, direction, 1)
                if square == "":
                    continue
                piece = board.get_piece_at(square)
                if (not piece.is_dead_or_empty() and piece.color != self.color) or board.is_en_passant(square):
                    moves.append(square)
        elif self.color == BLACK:
            directions = ['SW', 'SE']
            for direction in directions:
                square = get_square_in_direction(self.currentSquare, direction, 1)
                if square == "":
                    continue
                piece = board.get_piece_at(square)
                if (not piece.is_dead_or_empty() and piece.color != self.color) or board.is_en_passant(square):
                    moves.append(square)
        return moves

    def __get_pawn_attacks(self):
        return get_pawn_attack_squares(self.currentSquare, self.color)

    def __filter_non_king_moves(self, in_check, attacking_line, checking_squares):
        if self.pinned:
            self.validSquareMoves.clear()
            return
        elif in_check and attacking_line is None and len(checking_squares) > 1:
            self.validSquareMoves.clear()
            return
        else:
            self.validSquareMoves.clear()
            for move in self.available_moves:
                if not in_check and not self.pinned:
                    self.validSquareMoves.append(move)
                elif self.pinned:
                    continue
                elif in_check and len(checking_squares) == 1 and move.upper() == checking_squares[0].upper():
                    self.validSquareMoves.append(move)
                elif in_check and attacking_line is not None and does_square_lie_in_line(move, attacking_line):
                    self.validSquareMoves.append(move)

    def __filter_king_moves(self, castle_long, castle_short, board):
        self.validSquareMoves.clear()
        castle_long_allowed, castle_long_square = castle_long
        castle_short_allowed, castle_short_square = castle_short
        for move in self.available_moves:
            if self.symbol.upper() != 'K':
                continue
            else:
                if not castle_long_allowed and move.upper() == castle_long_square.upper():
                    continue
                if not castle_short_allowed and move.upper() == castle_short_square.upper():
                    continue
                if board.is_square_being_attacked(move, self):
                    continue
                self.validSquareMoves.append(move)

    def get_moves(self, board):
        switcher = {
            'P': self.__get_pawn_moves,
            'K': self.__get_king_moves,
            'N': self.__get_knight_moves,
            'B': self.__get_bishop_moves,
            'R': self.__get_rook_moves,
            'Q': self.__get_queen_moves,
        }
        return switcher[self.symbol.upper()](board)

    def get_attacks(self, board):
        switcher = {
            'P': self.__get_pawn_attacks,
            'K': self.__get_king_moves,
            'N': self.__get_knight_moves,
            'B': self.__get_bishop_moves,
            'R': self.__get_rook_moves,
            'Q': self.__get_queen_moves,
        }
        func = switcher[self.symbol.upper()]
        if self.symbol.upper() == 'P':
            return func()
        else:
            return func(board)

    def filter_moves(self, in_check, attacking_line, checking_squares, castle_long, castle_short, board):
        if self.symbol.upper() != 'K':
            self.__filter_non_king_moves(in_check, attacking_line, checking_squares)
        else:
            self.__filter_king_moves(castle_long, castle_short, board)

    def pin(self):
        self.pinned = True

    def unpin(self):
        self.pinned = False

    def get_attacking_squares(self, board):
        if self.attack_computed:
            return self.attackingSquares
        else:
            return self.compute_attacking_squares(board)

    def get_valid_moves(self, board, in_check, attacking_line, checking_squares, castle_long, castle_short):
        if self.move_computed:
            return self.validSquareMoves
        else:
            return self.compute_valid_moves(board, in_check, attacking_line, checking_squares, castle_long,
                                            castle_short)

    def refresh(self):
        self.pinned = False
        self.removed = False
        self.attack_computed = False
        self.move_computed = False
        self.attackingSquares.clear()
        self.available_moves.clear()
        self.validSquareMoves.clear()

    def remove(self):
        self.refresh()

    def get_precomputed_moves(self):
        return self.validSquareMoves

    def __str__(self):
        clrs = ['Undefined', 'White', 'Black']
        switcher = {
            'K': 'King',
            'Q': 'Queen',
            'R': 'Rook',
            'B': 'Bishop',
            'N': 'Knight',
            'P': 'Pawn'
        }
        return clrs[self.color] + ' ' + switcher.get(self.symbol.upper()) + " at " + self.currentSquare

    def __eq__(self, other):
        if isinstance(other, Piece):
            return other.symbol == self.symbol and other.color == self.color
        else:
            return False


class Move:

    def __init__(self, move, capture=False):
        self.piece = move[0]
        self.start = move[1]
        self.target = move[2]
        self.capture = capture
        self.promoted = move[3]

    @classmethod
    def from_notation(cls, notation: str, board):
        regex = r"^(([KQRBN]?)([a-h])?([1-8]?)(x?)([a-h][1-8])(=([QRBN]))?)|(O-O-O)|(O-O)"
        matches = re.findall(regex, notation)
        if len(matches) == 0:
            raise InValidMove(notation + " move is not possible or valid")
        pc = matches[0][1] if matches[0][1] != '' else 'P'
        id1 = matches[0][2]
        id2 = matches[0][3]
        cp = matches[0][4]
        tg = matches[0][5]
        pr = matches[0][7]
        cl = matches[0][8]
        cs = matches[0][9]
        p = board.get_piece(pc, id1 + id2, tg, notation)
        if (p.symbol == '.' or p is None) and cl == '' and cs == '':
            raise InValidMove(notation + " move is not possible or valid")
        else:
            if cl != '':
                moves = board.get_moves()
                for move in moves:
                    if is_castling_long(move):
                        return Move(move, False)
                raise InValidMove("Castling long not possible now")
            elif cs != '':
                moves = board.get_moves()
                for move in moves:
                    if is_castling_short(move):
                        return Move(move, False)
                raise InValidMove("Castling short not possible now")
            else:
                return Move((p, p.currentSquare, tg.upper(), pr), cp == 'x')

    def to_notation(self, board):
        pc = self.piece.symbol.upper() if self.piece.symbol.upper() != 'P' else ''
        cp = self.capture
        if pc == '' and cp:
            identifier = self.start[0]
        else:
            identifier = get_move_indicator(self.get_move(), board.get_moves())
        tg = self.target
        pr = self.promoted
        cl = is_castling_long(self.get_move())
        cs = is_castling_short(self.get_move())
        if cl:
            return 'O-O-O'
        if cs:
            return 'O-O'
        move_notation = pc + identifier + ('x' if cp else '') + tg.lower() + ('=' if pr != '' else '') + pr
        return move_notation

    def get_move(self):
        return self.piece, self.start, self.target, self.promoted

    def __str__(self):
        return str(self.piece) + " will move to " + self.target


class Player:

    def __init__(self, color):
        self.color = color
        self.castle_long = True
        self.castle_short = True
        self.in_check = False
        self.check_by_pawn = False
        self.check_by_knight = False
        self.checker_square = []
        self.checking_lines = ('', '', '')
        self.pins_computed = False
        self.checking_lines_computed = False
        self.moves = []
        self.attacks = []
        self.move_computed = False
        self.attack_computed = False
        self.check_computed = False
        if color == WHITE:
            self.king_rook = Piece.WHITE_ROOK()
            self.king_knight = Piece.WHITE_KNIGHT()
            self.king_bishop = Piece.WHITE_BISHOP()
            self.king = Piece.WHITE_KING()
            self.queen = Piece.WHITE_QUEEN()
            self.queen_bishop = Piece.WHITE_BISHOP()
            self.queen_knight = Piece.WHITE_KNIGHT()
            self.queen_rook = Piece.WHITE_ROOK()
            self.a_pawn = Piece.WHITE_PAWN()
            self.b_pawn = Piece.WHITE_PAWN()
            self.c_pawn = Piece.WHITE_PAWN()
            self.d_pawn = Piece.WHITE_PAWN()
            self.e_pawn = Piece.WHITE_PAWN()
            self.f_pawn = Piece.WHITE_PAWN()
            self.g_pawn = Piece.WHITE_PAWN()
            self.h_pawn = Piece.WHITE_PAWN()
        elif color == BLACK:
            self.king_rook = Piece.BLACK_ROOK()
            self.king_knight = Piece.BLACK_KNIGHT()
            self.king_bishop = Piece.BLACK_BISHOP()
            self.king = Piece.BLACK_KING()
            self.queen = Piece.BLACK_QUEEN()
            self.queen_bishop = Piece.BLACK_BISHOP()
            self.queen_knight = Piece.BLACK_KNIGHT()
            self.queen_rook = Piece.BLACK_ROOK()
            self.a_pawn = Piece.BLACK_PAWN()
            self.b_pawn = Piece.BLACK_PAWN()
            self.c_pawn = Piece.BLACK_PAWN()
            self.d_pawn = Piece.BLACK_PAWN()
            self.e_pawn = Piece.BLACK_PAWN()
            self.f_pawn = Piece.BLACK_PAWN()
            self.g_pawn = Piece.BLACK_PAWN()
            self.h_pawn = Piece.BLACK_PAWN()

    def setup_pieces(self, board):
        if self.color == WHITE:
            board.place_piece_at(self.queen_rook, 'A1')
            board.place_piece_at(self.queen_knight, 'B1')
            board.place_piece_at(self.queen_bishop, 'C1')
            board.place_piece_at(self.queen, 'D1')
            board.place_piece_at(self.king, 'E1')
            board.place_piece_at(self.king_bishop, 'F1')
            board.place_piece_at(self.king_knight, 'G1')
            board.place_piece_at(self.king_rook, 'H1')
            board.place_piece_at(self.a_pawn, 'A2')
            board.place_piece_at(self.b_pawn, 'B2')
            board.place_piece_at(self.c_pawn, 'C2')
            board.place_piece_at(self.d_pawn, 'D2')
            board.place_piece_at(self.e_pawn, 'E2')
            board.place_piece_at(self.f_pawn, 'F2')
            board.place_piece_at(self.g_pawn, 'G2')
            board.place_piece_at(self.h_pawn, 'H2')
        elif self.color == BLACK:
            board.place_piece_at(self.queen_rook, 'A8')
            board.place_piece_at(self.queen_knight, 'B8')
            board.place_piece_at(self.queen_bishop, 'C8')
            board.place_piece_at(self.queen, 'D8')
            board.place_piece_at(self.king, 'E8')
            board.place_piece_at(self.king_bishop, 'F8')
            board.place_piece_at(self.king_knight, 'G8')
            board.place_piece_at(self.king_rook, 'H8')
            board.place_piece_at(self.a_pawn, 'A7')
            board.place_piece_at(self.b_pawn, 'B7')
            board.place_piece_at(self.c_pawn, 'C7')
            board.place_piece_at(self.d_pawn, 'D7')
            board.place_piece_at(self.e_pawn, 'E7')
            board.place_piece_at(self.f_pawn, 'F7')
            board.place_piece_at(self.g_pawn, 'G7')
            board.place_piece_at(self.h_pawn, 'H7')

    def get_pieces(self):
        pieces = [self.queen_rook, self.queen_knight, self.queen_bishop, self.queen,
                  self.king, self.king_bishop, self.king_knight, self.king_rook,
                  self.a_pawn, self.b_pawn, self.c_pawn, self.d_pawn,
                  self.e_pawn, self.f_pawn, self.g_pawn, self.h_pawn]
        active_pieces = []
        for piece in pieces:
            if not piece.is_dead_or_empty():
                active_pieces.append(piece)
        return active_pieces

    def compute_attacking_squares(self, board):
        if self.attack_computed:
            return self.attacks
        else:
            self.attacks.clear()
            for piece in self.get_pieces():
                attacks = piece.get_attacking_squares(board)
                for sq in attacks:
                    self.attacks.append(sq)
            self.attack_computed = True
            return self.attacks

    def compute_valid_moves(self, board):
        if self.move_computed:
            return self.moves
        else:
            self.is_in_check(board)
            castle_long = self.can_castle_long(board, self.in_check)
            castle_short = self.can_castle_short(board, self.in_check)
            self.moves.clear()
            for piece in self.get_pieces():
                moves = piece.get_valid_moves(board, self.in_check, self.checking_lines, self.checker_square,
                                              castle_long, castle_short)
                for move in moves:
                    m = (piece, piece.currentSquare, move)
                    if not is_promotion(m):
                        self.moves.append((piece, piece.currentSquare, move, ''))
                    else:
                        self.moves.append((piece, piece.currentSquare, move, 'Q'))
                        self.moves.append((piece, piece.currentSquare, move, 'R'))
                        self.moves.append((piece, piece.currentSquare, move, 'B'))
                        self.moves.append((piece, piece.currentSquare, move, 'N'))
            return self.moves

    def has_insufficient_material(self):
        pieces = self.get_pieces()
        bishop1 = False
        bishop2 = False
        knight1 = False
        knight2 = False
        for piece in pieces:
            if piece.symbol.upper() == 'Q':
                return False
            elif piece.symbol.upper() == 'R':
                return False
            elif piece.symbol.upper() == 'P':
                return False
            elif piece.symbol.upper() == 'B':
                if bishop1:
                    bishop2 = True
                else:
                    bishop1 = True
            elif piece.symbol.upper() == 'N':
                if knight1:
                    knight2 = True
                else:
                    knight1 = True
        if bishop2:
            return False
        if bishop1 and knight2:
            return False
        if bishop1 and knight1:
            return False
        else:
            return True

    def check_for_pinned_pieces(self, board):
        if self.pins_computed:
            return
        directions = ['NW', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W']
        for direction in directions:
            i = 1
            piece_found = Piece.EMPTY()
            piece_found_flag = False
            square = get_square_in_direction(self.king.currentSquare, direction, 1)
            while square != "":
                piece = board.get_piece_at(square)
                if not piece_found_flag and piece.color == self.color:
                    piece_found = piece
                    piece_found_flag = True
                elif piece_found_flag and piece.color == self.color:
                    break
                elif piece_found_flag:
                    if piece.color != self.color and piece.symbol.upper() == 'Q':
                        piece_found.pin()
                        break
                    elif piece.color != self.color and direction in ['N', 'S', 'E', 'W'] and \
                            piece.symbol.upper() == 'R':
                        piece_found.pin()
                        break
                    elif piece.color != self.color and direction in ['NW', 'SE', 'NE', 'SW'] and \
                            piece.symbol.upper() == 'B':
                        piece_found.pin()
                        break
                    else:
                        break
                i = i + 1
                square = get_square_in_direction(self.king.currentSquare, direction, i)
        self.pins_computed = True

    def check_for_checking_lines(self, board):
        if self.checking_lines_computed:
            return self.checking_lines
        directions = ['NW', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W']
        number_of_attacking_lines = 0
        self.checking_lines = ('', '', '')
        for direction in directions:
            i = 1
            square = get_square_in_direction(self.king.currentSquare, direction, i)
            while square != "":
                piece = board.get_piece_at(square)
                if piece.symbol == '.':
                    i = i + 1
                    square = get_square_in_direction(self.king.currentSquare, direction, i)
                    continue
                if piece.color == self.color:
                    break
                if direction in ['N', 'S', 'E', 'W'] and piece.symbol.upper() not in ['R', 'Q']:
                    break
                if direction in ['NW', 'NE', 'SW', 'SE'] and piece.symbol.upper() not in ['B', 'Q']:
                    break
                number_of_attacking_lines = number_of_attacking_lines + 1
                self.checker_square.append(square)
                self.checking_lines = (direction, self.king.currentSquare, square)
                break
        if number_of_attacking_lines > 0:
            self.in_check = True
        if number_of_attacking_lines != 1:
            self.checking_lines = None
        self.checking_lines_computed = True
        return self.checking_lines

    def can_castle_long(self, board, in_check):
        king_rank = self.king.currentSquare[1]
        king_file = ord(self.king.currentSquare[0])
        king_target = chr(king_file - 2) + king_rank

        if not self.castle_long or in_check:
            return False, king_target

        if board.is_between_empty_safe_straight(self.king.currentSquare, self.queen_rook.currentSquare, self):
            return True, king_target
        else:
            return False, king_target

    def can_castle_short(self, board, in_check):
        king_rank = self.king.currentSquare[1]
        king_file = ord(self.king.currentSquare[0])
        king_target = chr(king_file + 2) + king_rank

        if not self.castle_long or in_check:
            return False, king_target

        if board.is_between_empty_safe_straight(self.king.currentSquare, self.king_rook.currentSquare, self):
            return True, king_target
        else:
            return False, king_target

    def refresh_pieces(self):
        pieces = self.get_pieces()
        for piece in pieces:
            piece.refresh()

    def is_in_check(self, board):
        if self.check_computed:
            return self.in_check
        self.in_check = False
        self.checker_square.clear()
        self.checking_lines = self.check_for_checking_lines(board)
        pawn = get_pawn_attack_squares(self.king.currentSquare, self.color)
        for sq in pawn:
            piece = board.get_piece_at(sq)
            if piece.color != self.color and piece.symbol.upper() == 'P':
                self.check_by_pawn = True
                self.checker_square.append(sq)
        knights = get_knight_squares(self.king.currentSquare)
        for sq in knights:
            piece = board.get_piece_at(sq)
            if piece.color != self.color and piece.symbol.upper() == 'N':
                self.check_by_knight = True
                self.checker_square.append(sq)
        self.in_check = self.check_by_pawn or self.check_by_knight or self.in_check
        self.check_computed = True
        return self.in_check

    def __str__(self):
        clrs = ['UNDEFINED', 'WHITE', 'BLACK']
        return clrs[self.color]

    def filter_king_moves(self, board, moves, in_check):
        king_moves = []
        castle_long_allowed, castle_long_square = self.can_castle_long(board, in_check)
        castle_short_allowed, castle_short_square = self.can_castle_short(board, in_check)
        for move in moves:
            if move[0].symbol.upper() != 'K':
                continue
            else:
                if not castle_long_allowed and move[2] == castle_long_square:
                    continue
                if not castle_short_allowed and move[2] == castle_short_square:
                    continue
                if board.is_square_being_attacked(move[2], self):
                    continue
                king_moves.append(move)
        return king_moves

    def get_moves(self, board):
        if self.move_computed:
            return self.moves
        else:
            return self.compute_valid_moves(board)

    def get_attacks(self, board):
        if self.attack_computed:
            return self.attacks
        else:
            return self.compute_attacking_squares(board)

    def refresh(self):
        self.pins_computed = False
        self.checking_lines_computed = False
        self.move_computed = False
        self.attack_computed = False
        self.in_check = False
        self.check_by_pawn = False
        self.check_by_knight = False
        self.check_computed = False
        self.checking_lines = ('', '', '')
        self.attacks.clear()
        self.moves.clear()
        self.refresh_pieces()

    def recompute(self, board):
        self.check_for_pinned_pieces(board)
        self.check_for_checking_lines(board)
        self.is_in_check(board)
        self.compute_attacking_squares(board)
        self.compute_valid_moves(board)

    def disable_long_castling(self):
        self.castle_long = False

    def disable_short_castling(self):
        self.castle_short = False


class Board:

    board_history = []

    def __init__(self, player1: Player, player2: Player):
        self.piece_board = [Piece.EMPTY()] * 64
        self.char_board = ['.'] * 64
        self.currentPlayer = player1
        self.currentOpponent = player2
        self.moveCounter = 0
        self.moveCounter75 = 0
        self.enPassant = ""

    def show(self):
        for i in range(64):
            print(self.char_board[i], end="  ")
            if i != 0 and (i + 1) % 8 == 0:
                print()

    def place_piece_at(self, piece: Piece, pos: str):
        ind = get_pos_from_square(pos)
        self.piece_board[ind] = piece
        self.char_board[ind] = piece.symbol
        piece.place_at(pos)

    def setup_board(self):
        self.currentPlayer.setup_pieces(self)
        self.currentOpponent.setup_pieces(self)

    def get_piece_at(self, pos: str):
        ind = get_pos_from_square(pos)
        return self.piece_board[ind]

    def is_square_being_attacked(self, square, player):
        attacks = []
        if player.color == self.currentPlayer.color:
            attacks = self.currentOpponent.get_attacks(self)
        elif player.color == self.currentOpponent.color:
            attacks = self.currentPlayer.get_attacks(self)
        return square in attacks

    def make_move(self, move_notation):
        self.enPassant = ""
        move = Move.from_notation(move_notation, self)
        is_king_rook = move.start == self.currentPlayer.king_rook.currentSquare
        is_queen_rook = move.start == self.currentPlayer.queen_rook.currentSquare
        promoted = ""
        if is_promotion((move.piece, move.start, move.target)):
            promoted = move.promoted
            if promoted == '':
                raise InValidMove("Promoted piece not decided")
        if move is None:
            return
        moving_piece = self.remove_piece_at(move.start)
        self.remove_piece_at(move.target)
        self.place_piece_at(moving_piece, move.target)
        if move_notation == 'O-O':
            king_rook = self.remove_piece_at(self.currentPlayer.king_rook.currentSquare)
            king_left = get_square_in_direction(move.target, 'W', 1)
            self.remove_piece_at(king_left)
            self.place_piece_at(king_rook, king_left)
        elif move_notation == 'O-O-O':
            queen_rook = self.remove_piece_at(self.currentPlayer.queen_rook.currentSquare)
            king_right = get_square_in_direction(move.target, 'E', 1)
            self.remove_piece_at(king_right)
            self.place_piece_at(queen_rook, king_right)
        if moving_piece.symbol.upper() == 'K':
            self.currentPlayer.disable_long_castling()
            self.currentPlayer.disable_short_castling()
        elif is_king_rook:
            self.currentPlayer.disable_short_castling()
        elif is_queen_rook:
            self.currentPlayer.disable_long_castling()
        if promoted:
            symbol = promoted.lower() if moving_piece.color == BLACK else promoted.upper()
            values = {
                'Q': 9,
                'R': 5,
                'B': 3,
                'N': 3
            }
            value = values.get(promoted.upper())
            new_piece = Piece(moving_piece.color, symbol, value)
            self.remove_piece_at(move.target)
            self.place_piece_at(new_piece, move.target)
        if moving_piece.symbol.upper() == 'P' and ((ord(move.start[1]) - ord(move.target[1])) in [2, -2]):
            self.enPassant = move.start[0] + chr((ord(move.start[1]) + ord(move.target[1]))//2)
        self.refresh()
        self.switch_turn()

    def simulate_move(self, move):
        simulated_board = copy.deepcopy(self)
        simulated_board.make_move(move)
        return simulated_board

    def is_draw_by_insufficient_material(self):
        return self.currentPlayer.has_insufficient_material() and \
               self.currentOpponent.has_insufficient_material()

    def is_draw_by_75_move_rule(self):
        return self.moveCounter75 >= 75

    def hash_state(self):
        hsh = 0
        for i in range(63):
            hsh = hsh + hash(ord(self.char_board[i]) * (37 + i)) + hash(i)
        hsh = hsh + hash(self.currentPlayer)
        return hsh

    def is_draw_by_five_fold_repetition(self):
        hash_value = self.hash_state()
        return Board.board_history.count(hash_value) >= 5

    def is_stalemate(self, player):
        pass

    def is_checkmate(self, player):
        pass

    def is_check(self, player):
        attacks = []
        king_pos = ""
        if player.color == self.currentPlayer.color:
            attacks = self.currentOpponent.get_attacks(self)
            king_pos = self.currentPlayer.king.currentSquare
        elif player.color == self.currentOpponent.color:
            attacks = self.currentPlayer.get_attacks(self)
            king_pos = self.currentOpponent.king.currentSquare
        return king_pos in attacks

    def get_opponent(self, player):
        return self.currentOpponent if player.color == self.currentPlayer.color else self.currentPlayer

    def is_between_empty_safe_straight(self, square1, square2, player):
        if not is_square_in_same_line(square1, square2):
            return False
        betweens = get_all_squares_between(square1, square2)
        i = 1
        for square in betweens:
            if square == square2:
                return True
            piece = self.get_piece_at(square)
            if not piece.symbol == '.' or (i <= 2 and self.is_square_being_attacked(square, player)):
                return False
            i = i + 1
        return True

    def get_moves(self):
        return self.currentPlayer.get_moves(self)

    def is_capture(self, move):
        target = self.get_piece_at(move[2])
        return not target.is_dead_or_empty()

    def get_piece(self, pc, identifier, target, move=""):
        possible_pieces = self.get_possible_pieces(pc, target)
        if len(possible_pieces) == 0:
            return Piece.EMPTY()
        elif len(possible_pieces) == 1:
            return possible_pieces[0]
        elif identifier == '':
            raise InValidMove(move + ' move is ambiguous')
        else:
            return get_piece_from_possibles(possible_pieces, identifier)

    def get_possible_pieces(self, pc, target):
        move_list = self.get_moves()
        pieces = []
        for move in move_list:
            if move[0].symbol.upper() == pc.upper() and move[2] == target.upper():
                pieces.append(move[0])
        return pieces

    def get_all_move_notations(self):
        move_list = self.get_moves()
        notations = []
        for move in move_list:
            capture = self.is_capture(move)
            m = Move(move, capture)
            notations.append(m.to_notation(self))
        return notations

    def remove_piece_at(self, square):
        piece = self.get_piece_at(square)
        pos = get_pos_from_square(square)
        self.piece_board[pos] = Piece.EMPTY()
        self.char_board[pos] = '.'
        piece.removed = True
        piece.currentSquare = ""
        piece.refresh()
        return piece

    def refresh(self):
        self.currentPlayer.refresh()
        self.currentOpponent.refresh()

    def switch_turn(self):
        self.currentPlayer, self.currentOpponent = self.currentOpponent, self.currentPlayer

    def get_moves_for_square(self, square):
        piece = self.get_piece_at(square)
        if piece.color == self.currentPlayer.color:
            self.currentPlayer.get_moves(self)
            return piece.get_precomputed_moves()
        else:
            return []

    def is_en_passant(self, square):
        return self.enPassant.upper() == square.upper()