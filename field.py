from constants import *


class Field:
    def __init__(self, x, y, neighbours, id_number, island=None):
        """
        Constructor for this class.
        :param x: x-coordinate of the field
        :param y: y-coordinate of the field
        :param neighbours: list of neighbours (of type Field) of the field
        :param island: A proper island (or sea) which the field belongs to (of type Island)
        :return: A Field object
        """
        self.x = x
        self.y = y
        self.neighbours = neighbours
        self.island = island
        self.id = id_number

    def __repr__(self):
        return "F({}, {})".format(self.x, self.y)

    def island_size(self, condensed=False):
        """
        Returnes a (maybe condensed) string that is used when printing a (partial) solution.
        Assumes that the 1 <= size of the island <= 99.
        :param condensed: True or False
        :return: String that describes the current field.
        """
        if self.is_part_of_sea():
            return " X" if condensed else "( X, X)"
        elif self.has_no_island():
            return " ." if condensed else "( ?, ?)"
        else:
            return "{: >2}".format(self.island.final_size) if condensed else "({: >2},{: >2})".format(self.island.final_size, self.island.component)

    def is_part_of_proper_island(self):
        return self.island is not None and self.island.final_size != SEA

    def is_part_of_sea(self):
        return self.island is not None and self.island.final_size == SEA

    def has_no_island(self):
        return self.island is None

    def get_island_final_size(self):
        return "" if self.island is None else self.island.final_size
