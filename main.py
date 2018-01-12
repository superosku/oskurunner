import random

import sys


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


class Ai:
    def __init__(self, board, number):
        self.piece_generator = PieceGenerator()

        self.board = board
        self.number = number

        self.played_points = []

    def make_move(self):
        moves = self.possible_moves()
        if not moves:
            self.board.increment_turn()
            return False

        offset, piece = random.choice(moves)

        for point in piece.points:
            self.played_points.append((
                point[0] + offset[0],
                point[1] + offset[1]
            ))

        self.board.do_move(offset, piece)

        return True

    def possible_move_points(self):
        if len(self.played_points) == 0:
            return [
                (0, 0),
                (24, 0),
                (0, 24),
                (24, 24)
            ]
        points = []
        for point in self.played_points:
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
        if max([x for x, y in new_points]) >= 25:
            return False
        if max([y for x, y in new_points]) >= 25:
            return False
        for point in new_points:
            if (
                self.board.is_taken(point) or
                self.board.is_taken((point[0] - 1, point[1])) or
                self.board.is_taken((point[0] + 1, point[1])) or
                self.board.is_taken((point[0], point[1] + 1)) or
                self.board.is_taken((point[0], point[1] - 1))
            ):
                return False
        return True


class Board:
    def __init__(self):
        self.piece_generator = PieceGenerator()

        self.played_points = {}
        self.played_points_by_player = {
            0: [],
            1: [],
            2: [],
            3: [],
        }
        self.played_pieces_by_player = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
        }
        self.turn = 0

    def is_taken(self, point):
        return point in self.played_points

    def print(self):
        print(' ' + '-' * 25, file=sys.stderr)
        for y in range(25):
            print('|', end='', sep='', file=sys.stderr)
            for x in range(25):
                letter = ' '
                for key, values in self.played_points_by_player.items():
                    if (x, y) in values:
                        letter = (
                            ['\033[94m', '\033[92m', '\033[93m', '\033[91m'][key] +
                            # '\u2588' +
                            '#' +
                            # str(key) +
                            '\033[0m'
                        )
                print(letter, end='', sep='', file=sys.stderr)
            print('|', end='', sep='', file=sys.stderr)
            print('', file=sys.stderr)
        print(' ' + '-' * 25, file=sys.stderr)

    def do_move(self, offset, piece):
        offset_x, offset_y = offset
        points_played = [
            (x + offset_x, y + offset_y) for x, y in piece.points
        ]
        self.add_played_points(points_played)

    def add_played_points(self, points_played):
        for point in points_played:
            self.played_points[point] = True
        self.played_points_by_player[self.turn] += points_played
        self.played_pieces_by_player[self.turn] += 1
        self.increment_turn()

    def increment_turn(self):
        self.turn = (self.turn + 1) % 4

    def print_points(self):
        print('points')
        for key, value in self.played_pieces_by_player.items():
            print(key, value)


class GameRunner:
    def __init__(self):
        self.pieces = PieceGenerator()
        self.board = Board()

    def read_input(self):
        return list(map(int, input().split()))

    def read_opponent_move(self):
        input = self.read_input()
        if input[0] == -1:
            sys.exit()
        moves = [i - 1 for i in input[1:]]
        points = []
        while moves:
            points.append((
                moves.pop(0),
                moves.pop(0)
            ))
        return points

    def run(self):
        print('oskurunner')
        board_size, player_count, player_number = self.read_input()

        # assert board_size == 25
        # assert player_count == 4
        # assert player_number == 1

        for i in range(player_number - 1):
            opponent_moves = self.read_opponent_move()
            self.board.add_played_points(opponent_moves)
            self.board.print()

        while True:
            possible_moves = self.board.possible_moves()
            if not possible_moves:
                sys.exit()
            else:
                offset, piece = random.choice(possible_moves)
                self.board.do_move(offset, piece)
                print(
                    piece.len,
                    ' '.join(['{} {}'.format(x + 1 + offset[0], y + 1 + offset[1]) for x, y in piece.points])
                )
            sys.stdout.flush()

            self.board.print()

            for i in range(3):
                opponent_moves = self.read_opponent_move()
                self.board.add_played_points(opponent_moves)
                self.board.print()


class DebugRunner:
    def __init__(self):
        pass

    def run(self):
        board = Board()
        ais = {
            Ai(board, i): True
            for i in range(4)
        }

        while all(ais.values()):
            for ai in ais:
                if not ai.make_move():
                    ais[ai] = False
                board.print()

        board.print()
        board.print_points()

if __name__ == '__main__':
    # GameRunner().run()
    DebugRunner().run()


