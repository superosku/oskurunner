import random


class Piece:
    def __init__(self, points):
        min_x = min([x for x, y in points])
        min_y = min([y for x, y in points])
        self.points = sorted(list(set([
            (x - min_x, y - min_y) for x, y in points
        ])), key=lambda i: i[0] * 10 + i[1])

    @property
    def len(self):
        return len(self.points)

    def get_child_pieces(self):
        if len(self.points) >= 4:
            return []
        pieces = []
        for x, y in self.points:
            pieces.append(Piece(
                [point for point in self.points] + [(x + 1, y)]
            ))
            pieces.append(Piece(
                [point for point in self.points] + [(x, y + 1)]
            ))
            pieces.append(Piece(
                [point for point in self.points] + [(x, y - 1)]
            ))
            pieces.append(Piece(
                [point for point in self.points] + [(x - 1, y)]
            ))
        return [
            piece for piece in pieces if piece != self
        ]

    def print(self):
        print(self.points)
        # print()
        for y in range(max([y for x, y in self.points]) + 1):
            for x in range(4):
                print('#' if (x, y) in self.points else ' ', end='', sep='')
            print('')

    def __eq__(self, other):
        return self.points == other.points


class PieceGenerator:
    def __init__(self):
        self.pieces = []

        piece = Piece([(0, 0)])
        self.pieces.append(piece)
        self.generate_and_add_new_pieces(piece)

    def generate_and_add_new_pieces(self, piece):
        for candidate_piece in piece.get_child_pieces():
            if candidate_piece not in self.pieces:
                self.pieces.append(candidate_piece)
                self.generate_and_add_new_pieces(candidate_piece)

    def print_pieces(self):
        for piece in self.pieces:
            piece.print()


class Board:
    def __init__(self):
        self.piece_generator = PieceGenerator()

        self.played_points = []
        self.played_points_by_player = {
            0: [],
            1: [],
            2: [],
            3: [],
        }
        self.played_pieces_by_player = {
            0: [],
            1: [],
            2: [],
            3: [],
        }
        self.turn = 0

    def print(self):
        print(' ' + '-' * 25)
        for y in range(25):
            print('|', end='', sep='')
            for x in range(25):
                letter = ' '
                for key, values in self.played_points_by_player.items():
                    if (x, y) in values:
                        letter = (
                            ['\033[94m', '\033[92m', '\033[93m', '\033[91m'][key] +
                            '#' +
                            # str(key) +
                            '\033[0m'
                        )
                print(letter, end='', sep='')
            print('|', end='', sep='')
            print('')
        print(' ' + '-' * 25)

    def possible_move_points(self):
        player_points = self.played_points_by_player[self.turn]
        if len(player_points) == 0:
            point = [(
                0 + 24 * (self.turn % 2),
                0 + 24 * int(self.turn / 2),
            )]
            # from pdb import set_trace; set_trace()
            return point
        points = []
        for point in player_points:
            points.append((point[0] + 1, point[1] + 1))
            points.append((point[0] - 1, point[1] + 1))
            points.append((point[0] - 1, point[1] - 1))
            points.append((point[0] + 1, point[1] - 1))
        return [
            point for point in points
            if point not in self.played_points
        ]

    def possible_moves(self):
        move_points = self.possible_move_points()
        possible_moves = []
        for move_x, move_y in move_points:
            for piece in self.piece_generator.pieces:
                for piece_x, piece_y in piece.points:
                    offset = (
                        move_x - piece_x,
                        move_y - piece_y
                    )
                    if self.is_possible_move(offset, piece):
                        possible_moves.append(
                            (offset, piece)
                        )
        return possible_moves

    def is_possible_move(self, offset, piece):
        # print('is_possible_move', offset, piece.points)
        offset_x, offset_y = offset
        new_points = [
            (
                x + offset_x,
                y + offset_y
            )
            for x, y in piece.points
        ]
        if min([x for x, y in new_points]) < 0:
            return False
        if min([y for x, y in new_points]) < 0:
            return False
        if min([x for x, y in new_points]) >= 25:
            return False
        if min([y for x, y in new_points]) >= 25:
            return False
        for point in new_points:
            if (
                point in self.played_points or
                (point[0] - 1, point[1]) in self.played_points or
                (point[0] + 1, point[1]) in self.played_points or
                (point[0], point[1] + 1) in self.played_points or
                (point[0], point[1] - 1) in self.played_points
            ):
                return False
        return True

    def do_move(self, offset, piece):
        offset_x, offset_y = offset
        points_played = [
            (x + offset_x, y + offset_y) for x, y in piece.points
        ]
        self.played_points += points_played
        self.played_points_by_player[self.turn] += points_played
        self.played_pieces_by_player[self.turn] += [(offset, piece)]
        self.turn = (self.turn + 1) % 4

    def print_points(self):
        print('points')
        for key, value in self.played_pieces_by_player.items():
            print(key, len(value))

if __name__ == '__main__':
    pieces = PieceGenerator()
    pieces.print_pieces()

    board = Board()
    board.print()
    print(board.possible_move_points())
    for offset, piece in board.possible_moves():
        print(offset, piece.points)

    counter = 0
    while True:
        if counter > 5:
            break
        moves = board.possible_moves()
        if not moves:
            counter += 1
            board.turn = (board.turn + 1) % 4
            continue
        offset, piece = random.choice(moves)
        board.do_move(offset, piece)
        board.print()

        board.print_points()

    board.print()
    board.print_points()

    # print(board.possible_moves())
