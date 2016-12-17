from constants import *


class Island:
    def __init__(self, fields, final_size, component):
        """
        Constructor for this class.
        :param fields: A set of fields (of type Field), for which we know they are part of the island. Typically,
        len(fields) would be 1 (proper island) or 0 (sea).
        :param final_size: For a proper island, this is the final size of the island, for sea, this is constants.SEA.
        :param component: ID-like positive integer (proper island) or SEA (sea).
        :return: An Island object.
        """
        self.fields = fields
        self.final_size = final_size
        self.component = component

    def __repr__(self):
        island_type = "Island" if self.component != SEA else "Sea"
        return "{}({};{})".format(island_type, self.final_size, self.fields)

    def size(self):
        """
        Computes the current size of the island.
        Meaingless in the case when the island actually represents sea.
        :return: The number of fields in the island.
        """
        assert self.component != SEA
        return len(self.fields)

    def possible_expansion(self):
        """
        Computes the number of missing fields of the island.
        Meaingless in the case when the island actually represents sea.
        :return: The number of missing fields in the island.
        """
        assert self.component != SEA
        return self.final_size - self.size()

    def has_final_size(self):
        """
        Tells us, whether the island is already of its final size.
        Meaingless in the case when the island actually represents sea.
        :return: True (False) if the island is (not) of its final size.
        """
        assert self.component != SEA
        return self.possible_expansion() == 0
