import random

import sys

import math

MAX_PIECE_SIZE = 4


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f'P({self.x}, {self.y})'

    def __gt__(self, other):
        '''
        Gives us something that can be used to sort points
        :param other:
        :return:
        '''
        return self.__hash__() > other.__hash__()

    def __hash__(self):
        return self.x + self.y * 1000

    def manhattan_dist(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euqlidean_dist(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


assert (Point(1, 2) + Point(1, 2)).x == 2
assert (Point(1, 2) + Point(1, 2)).y == 4
assert str(Point(1, 2)) == 'P(1, 2)'
assert Point(1, 1) == Point(1, 1)
assert Point(1, 1) != Point(1, 2)
assert Point(1, 1) != Point(2, 1)
# assert Point(11, 123).dist(Point(1, 5)) == 1180


class Piece:
    def __init__(self, points):
        '''
        Gets list of points as a parameter and normalizes and sorts them to
        create a piece
        :param points:
        '''
        min_x = min([point.x for point in points])
        min_y = min([point.y for point in points])
        sorted(points)
        self.points = sorted(list(set([
            point - Point(min_x, min_y) for point in points
        ])))

    @property
    def len(self):
        return len(self.points)

    def get_child_pieces(self):
        '''
        Returns all pieces that can be get from this piece by extending this
        piece from any possible direction
        :return:
        '''
        if len(self.points) >= MAX_PIECE_SIZE:
            return []
        pieces = []
        for point in self.points:
            pieces.append(Piece(
                [point for point in self.points] + [point + Point(1, 0)]
            ))
            pieces.append(Piece(
                [point for point in self.points] + [point + Point(0, 1)]
            ))
            pieces.append(Piece(
                [point for point in self.points] + [point - Point(1, 0)]
            ))
            pieces.append(Piece(
                [point for point in self.points] + [point - Point(0, 1)]
            ))
        return [
            piece for piece in pieces if piece != self
        ]

    def print(self):
        print(self.points)
        for y in range(max([point.y for point in self.points]) + 1):
            for x in range(4):
                print('#' if Point(x, y) in self.points else ' ', end='', sep='')
            print('')

    def __eq__(self, other):
        return self.points == other.points


class PieceGenerator:
    def __init__(self):
        self.pieces = []

        piece = Piece([Point(0, 0)])
        self.pieces.append(piece)
        self.generate_and_add_new_pieces(piece)

    def generate_and_add_new_pieces(self, piece):
        for candidate_piece in piece.get_child_pieces():
            if candidate_piece not in self.pieces:
                self.pieces.append(candidate_piece)
                self.generate_and_add_new_pieces(candidate_piece)

    def print_pieces(self):
        for i, piece in enumerate(self.pieces):
            print('Piece nro', i)
            piece.print()


# PieceGenerator().print_pieces()


class AiBase:
    def __init__(self, board, number):
        self.piece_generator = PieceGenerator()

        self.board = board
        self.number = number

        self.played_points = []

        self._possible_move_point_cache = []
        self.first_move_point = None

    def rate_move(self, offset, piece):
        raise NotImplementedError()

    def make_move(self):
        moves = self.possible_moves()
        if not moves:
            self.board.increment_turn()
            return False

        offset, piece = sorted(
            [(offset, piece) for offset, piece in moves],
            key=lambda x: -self.rate_move(x[0], x[1])
        )[0]

        if not self.first_move_point:
            self.first_move_point = [
                point + offset
                for point in piece.points
                if point + offset in self.possible_move_points
            ][0]

        for point in piece.points:
            self.played_points.append(point + offset)
            self.update_move_point_cache(point + offset)

        self.board.do_move(offset, piece)

        return piece, offset

    def update_move_point_cache(self, point):
        self._possible_move_point_cache.append(point + Point(1, 1))
        self._possible_move_point_cache.append(point + Point(-1, 1))
        self._possible_move_point_cache.append(point + Point(1, -1))
        self._possible_move_point_cache.append(point + Point(-1, -1))

        self._possible_move_point_cache = list(set(
            self._possible_move_point_cache
        ))

        self._possible_move_point_cache = [
            point for point in self._possible_move_point_cache if
            not self.board.is_taken_or_next_is_taken(point)
        ]

    @property
    def possible_move_points(self):
        if len(self.played_points) == 0:
            return [
                Point(0, 0),
                Point(24, 0),
                Point(0, 24),
                Point(24, 24)
            ]
        return self._possible_move_point_cache

    def possible_moves(self):
        possible_moves = []
        for posible_point in self.possible_move_points:
            for piece in self.piece_generator.pieces:
                for piece_point in piece.points:
                    offset = posible_point - piece_point
                    if self.is_possible_move(offset, piece):
                        possible_moves.append(
                            (offset, piece)
                        )
        return possible_moves

    def is_possible_move(self, offset, piece):
        new_points = [
            point + offset for point in piece.points
        ]
        if min([point.x for point in new_points]) < 0:
            return False
        if min([point.y for point in new_points]) < 0:
            return False
        if max([point.x for point in new_points]) >= 25:
            return False
        if max([point.y for point in new_points]) >= 25:
            return False
        for point in new_points:
            if self.board.is_taken_or_next_is_taken(point):
                return False
        return True


class RandomAi(AiBase):
    def rate_move(self, offset, piece):
        return random.random()


class PointAi(AiBase):
    def rate_move(self, offset, piece):
        return 10 - piece.len + random.random()


class DistanceAi(AiBase):
    def rate_move(self, offset, piece):
        if self.first_move_point:
            return max([
                self.first_move_point.euqlidean_dist(offset + piece_point)
                for piece_point in piece.points]
            ) + 1 if piece in [
                self.board.piece_generator.pieces[17],
                self.board.piece_generator.pieces[9],
                self.board.piece_generator.pieces[7],
                self.board.piece_generator.pieces[19],
            ] else 0
        return 0



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

    def is_taken_or_next_is_taken(self, point):
        return (
            self.is_taken(point) or
            self.is_taken(point + Point(1, 0)) or
            self.is_taken(point + Point(0, 1)) or
            self.is_taken(point - Point(1, 0)) or
            self.is_taken(point - Point(0, 1))
        )

    def print(self):
        print(' ' + '-' * 25, file=sys.stderr)
        for y in range(25):
            print('|', end='', sep='', file=sys.stderr)
            for x in range(25):
                letter = ' '
                for key, points in self.played_points_by_player.items():
                    if Point(x, y) in points:
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
        points_played = [
            point + offset for point in piece.points
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
            print(
                ['\033[94m', '\033[92m', '\033[93m', '\033[91m'][key] +
                str(key) +
                '\033[0m',
                value
            )


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
            points.append(Point(
                moves.pop(0),
                moves.pop(0)
            ))
        return points

    def run(self, ai_class):
        print('oskuruner')
        board_size, player_count, player_number = self.read_input()

        # assert board_size == 25
        # assert player_count == 4
        # assert player_number == 1

        for i in range(player_number - 1):
            opponent_moves = self.read_opponent_move()
            self.board.add_played_points(opponent_moves)
            self.board.print()

        ai = ai_class(self.board, 0)

        while True:
            move = ai.make_move()
            if not move:
                sys.exit()

            piece, offset = move

            # possible_moves = self.board.possible_moves()
            # if not possible_moves:
            #     sys.exit()
            # else:
            #     offset, piece = random.choice(possible_moves)
            #     self.board.do_move(offset, piece)
            print(
                piece.len,
                # ' '.join(['{} {}'.format(x + 1 + offset[0], y + 1 + offset[1]) for x, y in piece.points])
                ' '.join(['{} {}'.format(
                    (point + offset).x + 1,
                    (point + offset).y + 1,
                ) for point in piece.points])
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
            c(board, i): True
            for i, c in enumerate([
                RandomAi,
                RandomAi,
                # RandomAi,
                DistanceAi,
                # RandomAi,
                PointAi,
                # PointAi,
                # PointAi,
                # PointAi,
            ])
        }

        while any(ais.values()):
            for ai in ais:
                if not ai.make_move():
                    ais[ai] = False
            board.print()

        board.print()
        board.print_points()


if __name__ == '__main__':
    random.seed(0)
    GameRunner().run(RandomAi)
    # GameRunner().run(random.choice([
    #     RandomAi,
    #     DistanceAi,
    #     # PointAi
    # ]))
    # # DebugRunner().run()


