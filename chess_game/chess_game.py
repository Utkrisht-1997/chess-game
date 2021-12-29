import re
import copy
from colorama import Fore, Back

WHITE = 1
BLACK = -1

squares_in_board = [
    'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8',
    'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7',
    'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6',
    'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5',
    'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4',
    'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3',
    'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
    'A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1'
]


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
        for r in range(rank_start + diff, rank_end + diff, 1 if rank_end > rank_start else -1):
            squares.append(chr(file) + str(r))
    elif rank_start == rank_end:
        rank = rank_start
        diff = 1 if file_end > file_start else -1
        for f in range(file_start + diff, file_end + diff, 1 if file_end > file_start else -1):
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
    return 8 * rank_num + file_num


def get_square_from(i: int, j: int):
    ind = i * 8 + j
    return squares_in_board[ind]


def get_piece_from_char(c: str):
    color = WHITE if c.isupper() else BLACK
    value_dict = {
        'K': 0,
        'Q': 9,
        'R': 5,
        'B': 3,
        'N': 3,
        'P': 1
    }
    value = value_dict.get(c.upper())
    return ChessPiece(color, c, value)


def fen_to_char_array(fen: str):
    fen_rows = fen.split("/")
    ch_arr = ['.'] * 64
    r = 0
    for fen_row in fen_rows:
        f = 0
        for ch in fen_row:
            if ch == '8':
                continue
            if 49 <= ord(ch) <= 55:
                f = f + ord(ch) - 48
                continue
            ind = r * 8 + f
            ch_arr[ind] = ch
            f = f + 1
        r = r + 1
    return ch_arr


def char_array_to_fen(char_board):
    fen = ""
    gap = 0
    for i in range(64):
        ch = char_board[i]
        if ch == '.':
            gap = gap + 1
        else:
            fen = fen + (str(gap) if gap != 0 else "") + ch
            gap = 0
        if (i + 1) % 8 == 0:
            fen = fen + (str(gap) if gap != 0 else "") + ("/" if i != 63 else "")
            gap = 0
    return fen


def are_squares_adjacent(square1, square2):
    file1 = ord(square1[0])
    rank1 = ord(square1[1]) - 48
    file2 = ord(square2[0])
    rank2 = ord(square2[1]) - 48
    if rank1 - rank2 >= 2 or rank2 - rank1 >= 2:
        return False
    if file1 - file2 >= 2 or file2 - file1 >= 2:
        return False
    return True


class InvalidMove(Exception):
    pass


class InvalidFen(Exception):
    pass


class InvalidBoard(Exception):
    pass


class ChessPiece:

    def __init__(self, color: int, symbol: str, value: int):
        self.color = color
        self.symbol = symbol
        self.value = value
        self.attackingSquares = []
        self.currentSquare = ""
        self.available_moves = []
        self.validSquareMoves = []
        self.pinned = False
        self.pinned_line = ('', '', '')
        self.removed = False
        self.attack_computed = False
        self.move_computed = False

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

    def __get_rook_attacks(self, board):
        directions = ['N', 'S', 'E', 'W']
        attacks = []
        for direction in directions:
            i = 1
            square = get_square_in_direction(self.currentSquare, direction, i)
            while square != "":
                piece = board.get_piece_at(square)
                if piece.symbol != '.':
                    attacks.append(square)
                    break
                else:
                    attacks.append(square)
                    i = i + 1
                    square = get_square_in_direction(self.currentSquare, direction, i)
        return attacks

    def __get_bishop_attacks(self, board):
        directions = ['NW', 'SE', 'NE', 'SW']
        attacks = []
        for direction in directions:
            i = 1
            square = get_square_in_direction(self.currentSquare, direction, i)
            while square != "":
                piece = board.get_piece_at(square)
                if piece.symbol != '.':
                    attacks.append(square)
                    break
                else:
                    attacks.append(square)
                    i = i + 1
                    square = get_square_in_direction(self.currentSquare, direction, i)
        return attacks

    def __get_queen_attacks(self, board):
        rook = self.__get_rook_attacks(board)
        bishop = self.__get_bishop_attacks(board)
        moves = rook + bishop
        return moves

    def __get_king_attacks(self):
        directions = ['NW', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W']
        attacks = []
        for direction in directions:
            square = get_square_in_direction(self.currentSquare, direction, 1)
            if square != "":
                attacks.append(square)
        return attacks

    def __filter_non_king_moves(self, in_check, attacking_line, checking_squares):
        if self.pinned:
            self.validSquareMoves.clear()
            for move in self.available_moves:
                if does_square_lie_in_line(move, self.pinned_line):
                    self.validSquareMoves.append(move)
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
            'K': self.__get_king_attacks,
            'N': self.__get_knight_moves,
            'B': self.__get_bishop_attacks,
            'R': self.__get_rook_attacks,
            'Q': self.__get_queen_attacks,
        }
        func = switcher[self.symbol.upper()]
        if self.symbol.upper() == 'P' or self.symbol.upper() == 'K':
            return func()
        else:
            return func(board)

    def filter_moves(self, in_check, attacking_line, checking_squares, castle_long, castle_short, board):
        if self.symbol.upper() != 'K':
            self.__filter_non_king_moves(in_check, attacking_line, checking_squares)
        else:
            self.__filter_king_moves(castle_long, castle_short, board)

    def pin(self, pinned_line):
        self.pinned = True
        self.pinned_line = pinned_line

    def unpin(self):
        self.pinned = False
        self.pinned_line = ('', '', '')

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
        return clrs[self.color] + ' ' + switcher.get(self.symbol.upper()) + " at " + self.currentSquare + (" is Pinned "
                                                                                                           if
                                                                                                           self.pinned
                                                                                                           else "")

    def __eq__(self, other):
        if isinstance(other, ChessPiece):
            return other.symbol == self.symbol and other.color == self.color
        else:
            return False


class Piece:
    WHITE_KING = "WHITE KING"
    WHITE_QUEEN = "WHITE_QUEEN"
    WHITE_ROOK = "WHITE_ROOK"
    WHITE_BISHOP = "WHITE_BISHOP"
    WHITE_KNIGHT = "WHITE_KNIGHT"
    WHITE_PAWN = "WHITE_PAWN"
    BLACK_KING = "BLACK KING"
    BLACK_QUEEN = "BLACK_QUEEN"
    BLACK_ROOK = "BLACK_ROOK"
    BLACK_BISHOP = "BLACK_BISHOP"
    BLACK_KNIGHT = "BLACK_KNIGHT"
    BLACK_PAWN = "BLACK_PAWN"
    EMPTY = "EMPTY"

    @classmethod
    def generate(cls, pc):
        generator = {
            cls.WHITE_KING: (WHITE, 'K', 0),
            cls.WHITE_QUEEN: (WHITE, 'Q', 9),
            cls.WHITE_ROOK: (WHITE, 'R', 5),
            cls.WHITE_BISHOP: (WHITE, 'B', 3),
            cls.WHITE_KNIGHT: (WHITE, 'N', 3),
            cls.WHITE_PAWN: (WHITE, 'P', 1),
            cls.BLACK_KING: (BLACK, 'k', 0),
            cls.BLACK_QUEEN: (BLACK, 'q', 9),
            cls.BLACK_ROOK: (BLACK, 'r', 5),
            cls.BLACK_BISHOP: (BLACK, 'b', 3),
            cls.BLACK_KNIGHT: (BLACK, 'n', 3),
            cls.BLACK_PAWN: (BLACK, 'p', 1),
            cls.EMPTY: (0, '.', 0)
        }
        color, symbol, value = generator.get(pc)
        return ChessPiece(color, symbol, value)


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
            raise InvalidMove(notation + " move is not possible or valid")
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
            raise InvalidMove(notation + " move is not possible or valid")
        else:
            if cl != '':
                moves = board.get_moves()
                for move in moves:
                    if is_castling_long(move):
                        return Move(move, False)
                raise InvalidMove("Castling long not possible now")
            elif cs != '':
                moves = board.get_moves()
                for move in moves:
                    if is_castling_short(move):
                        return Move(move, False)
                raise InvalidMove("Castling short not possible now")
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
        check_or_mate = ""
        if board.is_checkmate():
            check_or_mate = "#"
        elif board.is_check():
            check_or_mate = "+"
        move_notation = pc + identifier.lower() + ('x' if cp else '') + tg.lower() + ('=' if pr != '' else '') + pr + \
                        check_or_mate
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
        self.pieces = []
        self.king = Piece.generate(Piece.EMPTY)
        self.queen_rook = Piece.generate(Piece.EMPTY)
        self.king_rook = Piece.generate(Piece.EMPTY)

    def get_pieces(self):
        return self.pieces

    def add_piece(self, piece, is_king=False, is_king_rook=False, is_queen_rook=False):
        self.pieces.append(piece)
        if is_king:
            self.king = piece
        elif is_king_rook:
            self.king_rook = piece
        elif is_queen_rook:
            self.queen_rook = piece

    def remove_piece(self, piece):
        for i in range(len(self.pieces)):
            if piece == self.pieces[i] and piece.currentSquare == self.pieces[i].currentSquare:
                self.pieces.pop(i)
                break

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
            self.check_for_pinned_pieces(board)
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
            piece_found = Piece.generate(Piece.EMPTY)
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
                        piece_found.pin((direction, self.king.currentSquare, square))
                        break
                    elif piece.color != self.color and direction in ['N', 'S', 'E', 'W'] and \
                            piece.symbol.upper() == 'R':
                        piece_found.pin((direction, self.king.currentSquare, square))
                        break
                    elif piece.color != self.color and direction in ['NW', 'SE', 'NE', 'SW'] and \
                            piece.symbol.upper() == 'B':
                        piece_found.pin((direction, self.king.currentSquare, square))
                        break
                    elif piece.symbol != '.':
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

        if not self.castle_long or in_check or self.king_rook.symbol == '.' or self.queen_rook.symbol == '.':
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

    def has_king(self):
        return self.king.symbol != '.' and self.king.currentSquare != ""

    def get_valid_move_count(self, board):
        return len(self.get_moves(board))


class Board:
    board_history = []

    def __init__(self, player1: Player = Player(WHITE), player2: Player = Player(BLACK)):
        self.piece_board = [Piece.generate(Piece.EMPTY)] * 64
        self.char_board = ['.'] * 64
        self.currentPlayer = player1
        self.currentOpponent = player2
        self.moveCounter = 1
        self.moveCounter75 = 0
        self.enPassant = ""
        self.en_target = ""
        self.record_file = ""
        Board.board_history.append(self.hash_state())

    @classmethod
    def from_fen(cls, fen: str):
        reg_fen = r"^(([1-8rnbqkpRNBQKP]+/){7}[1-8rnbqkpRNBQKP]+) ([wb]) ([KQkq]{1,4}|-) ([a-h][1-8]|-) (\d+) (\d+)$"
        matches = re.findall(reg_fen, fen)
        if len(matches) == 0:
            raise InvalidFen("Fen provided is not valid")
        else:
            fen_board = matches[0][0]
            player = matches[0][2]
            castlings = matches[0][3]
            current_player = Player(WHITE) if player.lower() == 'w' else Player(BLACK)
            opponent = Player(BLACK) if player.lower() == 'w' else Player(WHITE)
            b = Board(current_player, opponent)
            b.char_board = fen_to_char_array(fen_board)
            if 'K' in castlings:
                b.get_white_player().castle_short = True
            if 'Q' in castlings:
                b.get_white_player().castle_long = True
            if 'k' in castlings:
                b.get_black_player().castle_long = True
            if 'q' in castlings:
                b.get_black_player().castle_short = True
            for i in range(63):
                ch = b.char_board[i]
                if ch == '.':
                    continue
                piece = get_piece_from_char(ch)
                pos = squares_in_board[i]
                b.place_piece_at(piece, pos, True)
            b.enPassant = matches[0][4] if matches[0][4] != '-' else ''
            b.moveCounter75 = int(matches[0][4])
            b.moveCounter = int(matches[0][5])
        return b

    def to_fen(self):
        fen_board = char_array_to_fen(self.char_board)
        player_turn = 'w' if self.currentPlayer.color == WHITE else 'b'
        castles = ""
        castles = castles + ("K" if self.get_white_player().castle_short else "")
        castles = castles + ("Q" if self.get_white_player().castle_long else "")
        castles = castles + ("k" if self.get_black_player().castle_short else "")
        castles = castles + ("q" if self.get_black_player().castle_long else "")
        if castles == "":
            castles = '-'
        en_pass = "-" if self.enPassant == "" else self.enPassant
        half_move = self.moveCounter75
        full_move = self.moveCounter
        return fen_board + " " + player_turn + " " + castles + " " + en_pass + " " + str(half_move) + " " + \
            str(full_move)

    def print_ascii(self):
        for i in range(64):
            print(self.char_board[i], end="  ")
            if i != 0 and (i + 1) % 8 == 0:
                print()

    def print_colored(self):
        color_dark = Back.LIGHTBLUE_EX
        color_light = Back.LIGHTWHITE_EX
        for r in range(8):
            for f in range(8):
                ind = 8 * r + f
                ch = self.char_board[ind]
                if ch == '.':
                    ch = " "
                fore_color = Fore.BLACK if ch.islower() else Fore.MAGENTA
                if r % 2 == f % 2:
                    print(color_light + fore_color + " " + ch + " ", end="")
                else:
                    print(color_dark + fore_color + " " + ch + " ", end="")
            print(Back.RESET + Fore.RESET + "")

    def place_piece_at(self, piece: ChessPiece, pos: str, setup=False):
        if setup:
            if piece.color == WHITE:
                is_king_rook = piece.symbol == 'R' and pos[0] == 'H'
                is_queen_rook = piece.symbol == 'R' and pos[0] == 'A'
                self.get_white_player().add_piece(piece, piece.symbol == 'K', is_king_rook, is_queen_rook)
            elif piece.color == BLACK:
                is_king_rook = piece.symbol == 'r' and pos[0] == 'H'
                is_queen_rook = piece.symbol == 'r' and pos[0] == 'A'
                self.get_black_player().add_piece(piece, piece.symbol == 'k', is_king_rook, is_queen_rook)
        ind = get_pos_from_square(pos)
        self.piece_board[ind] = piece
        self.char_board[ind] = piece.symbol
        piece.place_at(pos)

    def setup_board(self):
        self.place_piece_at(Piece.generate(Piece.WHITE_ROOK), 'A1', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_KNIGHT), 'B1', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_BISHOP), 'C1', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_QUEEN), 'D1', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_KING), 'E1', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_BISHOP), 'F1', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_KNIGHT), 'G1', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_ROOK), 'H1', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_PAWN), 'A2', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_PAWN), 'B2', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_PAWN), 'C2', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_PAWN), 'D2', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_PAWN), 'E2', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_PAWN), 'F2', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_PAWN), 'G2', True)
        self.place_piece_at(Piece.generate(Piece.WHITE_PAWN), 'H2', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_ROOK), 'A8', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_KNIGHT), 'B8', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_BISHOP), 'C8', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_QUEEN), 'D8', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_KING), 'E8', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_BISHOP), 'F8', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_KNIGHT), 'G8', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_ROOK), 'H8', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_PAWN), 'A7', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_PAWN), 'B7', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_PAWN), 'C7', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_PAWN), 'D7', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_PAWN), 'E7', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_PAWN), 'F7', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_PAWN), 'G7', True)
        self.place_piece_at(Piece.generate(Piece.BLACK_PAWN), 'H7', True)

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
        self.check_valid()
        move = Move.from_notation(move_notation, self)
        is_en_pass = self.enPassant != "" and move.target.upper() == self.enPassant.upper()
        self.enPassant = ""
        is_king_rook = move.start == self.currentPlayer.king_rook.currentSquare
        is_queen_rook = move.start == self.currentPlayer.queen_rook.currentSquare
        promoted = ""
        if is_promotion((move.piece, move.start, move.target)):
            promoted = move.promoted
            if promoted == '':
                raise InvalidMove("Promoted piece not decided")
        if move is None:
            return
        moving_piece = self.remove_piece_at(move.start)
        captured_piece = self.remove_piece_at(move.target, True)
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
            new_piece = ChessPiece(moving_piece.color, symbol, value)
            self.remove_piece_at(move.target, True)
            self.place_piece_at(new_piece, move.target, True)
        if is_en_pass:
            self.remove_piece_at(self.en_target, True)
        self.en_target = ""
        if moving_piece.symbol.upper() == 'P' and ((ord(move.start[1]) - ord(move.target[1])) in [2, -2]):
            self.enPassant = move.start[0] + chr((ord(move.start[1]) + ord(move.target[1])) // 2)
            self.en_target = move.target
        if moving_piece.symbol.upper() == 'P' or captured_piece.symbol != '.':
            self.moveCounter75 = 0
        else:
            self.moveCounter75 = self.moveCounter75 + 1
        self.refresh()
        self.switch_turn()
        if moving_piece.color == WHITE:
            self.record_file = self.record_file + str(self.moveCounter) + ". " + move.to_notation(self)
        else:
            self.record_file = self.record_file + " " + move.to_notation(self) + " "
            self.moveCounter = self.moveCounter + 1
        Board.board_history.append(self.hash_state())

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

    def is_stalemate(self, player=None):
        if player is None:
            player = self.currentPlayer
        return (not self.is_check(player)) and player.get_valid_move_count(self) == 0

    def is_checkmate(self, player=None):
        if player is None:
            player = self.currentPlayer
        return self.is_check(player) and player.get_valid_move_count(self) == 0

    def is_check(self, player=None):
        if player is None:
            player = self.currentPlayer
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
        if square2 == "" or square1 == "":
            return False
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
            return Piece.generate(Piece.EMPTY)
        elif len(possible_pieces) == 1:
            return possible_pieces[0]
        elif len(possible_pieces) == 4 and pc.upper() == 'P':
            return possible_pieces[0]
        elif identifier == '':
            raise InvalidMove(move + ' move is ambiguous')
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

    def remove_piece_at(self, square, permanent=False):
        if square == "":
            return
        piece = self.get_piece_at(square)
        if permanent and piece.color == WHITE:
            self.get_white_player().remove_piece(piece)
        elif permanent and piece.color == BLACK:
            self.get_black_player().remove_piece(piece)
        pos = get_pos_from_square(square)
        self.piece_board[pos] = Piece.generate(Piece.EMPTY)
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

    def get_white_player(self):
        if self.currentPlayer.color == WHITE:
            return self.currentPlayer
        else:
            return self.currentOpponent

    def get_black_player(self):
        if self.currentPlayer.color == WHITE:
            return self.currentOpponent
        else:
            return self.currentPlayer

    def check_valid(self):
        if not self.currentPlayer.has_king() or not self.currentOpponent.has_king():
            raise InvalidBoard("Both player must have king on board")
        if are_squares_adjacent(self.currentPlayer.king.currentSquare, self.currentOpponent.king.currentSquare):
            raise InvalidBoard("King cannot be placed adjacent to each other")

    def is_game_over(self):
        return self.is_stalemate() or \
               self.is_checkmate() or self.is_draw_by_insufficient_material() or \
               self.is_draw_by_75_move_rule() or self.is_draw_by_five_fold_repetition()

    def get_info(self):
        info = BoardInfo()
        info.check = self.is_check()
        info.check_mate = self.is_checkmate()
        info.stale_mate = self.is_stalemate()
        info.move_count = self.moveCounter
        info.game_over = self.is_game_over()
        return info


class BoardInfo:

    def __init__(self):
        self.check = False
        self.check_mate = False
        self.stale_mate = False
        self.move_count = False
        self.game_over = False

    def __str__(self):
        return "{ check: " + str(self.check) + ", check_mate: " + str(self.check_mate) + ", stale_mate: " + \
               str(self.stale_mate) + ", move_count: " + str(self.move_count) + ", game_over: " + str(self.game_over) +\
               "}"
