from field import *
from island import *
from constants import *
from heapq import *


class Nurikabe:
    def __init__(self, width, height, islands_stems, pencil_paper_solution):
        """
        Contructor for the class Nurikabe.
        :param width: The width of the Nurikabe. The x-coordinates of the fields should be in the interval [0, width).
        :param height: The height of Nurikabe. The y-coordinates of the fields should be in the interval [0, height).
        :param islands_stems: List of triples (x, y, size), where (x, y) denote the position of one of the fields
        that belong to an island of the final size size. Coordinate system is placed like this:

        0      x
          ------->
          |
         y|
          |
         \/
        :param pencil_paper_solution: A list of length height, where each element is a list of length width and
        pencil_paper_solution[i][j] is SEA, island's size or ''.
        :return: A Nurikabe object.
        """
        self.width = width
        self.height = height
        self.fields = [[Field(x, y, [], y * self.width + x) for x in range(self.width)] for y in range(self.height)]
        self.id_to_field = {field.id: field for line in self.fields for field in line}
        self.unknown = {field for line in self.fields for field in line}
        self.islands = []
        self.components = {}  # {id1: island1, id2: island2, ...}
        # create islands
        component_counter = 1
        for (x, y, size) in islands_stems:
            if DEBUG > 0:
                print("(x, y, size)", x, y, size)
            field = self.fields[y][x]
            island = Island({field}, size, component_counter)
            self.components[component_counter] = island
            field.island = island
            self.islands.append(island)
            self.unknown.remove(field)
            component_counter += 1

        self.number_of_steps = 0
        self.show_partial_solution("", condensed=True)
        # set neighbours
        for y in range(self.height):
            for x in range(self.width):
                if x > 0:
                    self.fields[y][x].neighbours.append(self.fields[y][x - 1])
                if x < self.width - 1:
                    self.fields[y][x].neighbours.append(self.fields[y][x + 1])
                if y > 0:
                    self.fields[y][x].neighbours.append(self.fields[y - 1][x])
                if y < self.height - 1:
                    self.fields[y][x].neighbours.append(self.fields[y + 1][x])
        # create sea
        self.sea = Island(set(), SEA, SEA)
        self.components[0] = self.sea
        self.number_feasible_solutions = 0
        # pencil and paper solution
        self.pencil_paper_solution = pencil_paper_solution
        if self.pencil_paper_solution is not None and DEBUG > 0:
            print("My solution:")
            for i, x in enumerate(self.pencil_paper_solution):
                print(x, i)

    def check_partial_solution(self):
        """
        Checks whether the pencil and paper solution equals the partial solution so far.
        :return: (True/False, x, y): the first component tells us, whether the solutions coincide, the other two are
         the coordinates of the first field where the difference between the solutions occurs (or -1, -1 if there is no
         difference).
        """
        def equality(b1, b2):
            return b1 == "" or b2 == "" or b1 == b2
        
        for y in range(self.height):
            for x in range(self.width):
                ok = equality(self.pencil_paper_solution[y][x], self.fields[y][x].get_island_final_size())
                if not ok:
                    return False, x, y
        return True, -1, -1

    def nearby_islands(self, x, y, the_island=None):
        """
        Finds the islands that the field with coordinates (x, y) could be appended to.
        :param x: x-coordinate of the field
        :param y: y-coordinate of the field
        :param the_island: None (all islands are candidates) or one particular island (the only candidate)
        :return: List of pairs (island, dist(island, (x, y))), sorted increasingly by distance. Distance is the
        minimal number of fields of the unknown colour that connect the island and the field (x, y) (>= 1).
        """
        is_candidate = (lambda o: True) if the_island is None else (lambda o: o == the_island)
        nearby = []
        distance_xy_island = {island: float("inf") for island in self.islands}
        for island in self.islands:
            island_too_far = not is_candidate(island)
            for starting_field in island.fields:
                if island_too_far:
                    break
                # simplified Dijkstra's algorithm
                is_processed = {field.id: False for line in self.fields for field in line}

                to_be_processed = []  # [[distance to the field, field id], ...]
                heappush(to_be_processed, [0, starting_field.id])

                is_processed[starting_field.id] = True

                found_xy = False
                while to_be_processed and to_be_processed[0][0] < island.possible_expansion() and not found_xy:
                    dist, field_id = heappop(to_be_processed)
                    for neighbour in self.id_to_field[field_id].neighbours:
                        if neighbour.x == x and neighbour.y == y:
                            # island remains the candidate for nearby islands
                            found_xy = True
                            distance_xy_island[island] = min(distance_xy_island[island], dist + 1)
                            break
                        elif (not is_processed[neighbour.id]) and (neighbour.has_no_island() or neighbour in island.fields):
                            heappush(to_be_processed, [dist + neighbour.has_no_island(), neighbour.id])
                            # is_precessed[neighbour.id] can be set to True: if neighbour happends to be
                            # a candidate again later on, the distance will be equal or greater to the current distance
                            is_processed[neighbour.id] = True
                    if found_xy:
                        break

                if not found_xy:
                    island_too_far = True
                    break
            if not island_too_far:
                nearby.append((island, distance_xy_island[island]))
        nearby.sort(key=lambda isl: isl[-1])
        return nearby

    def is_feasible(self):
        """
        Chechs whether the solution is feasible. The following conditions are checked:
        1. Each island has island is of the right size and is connected.
        2. The sea is connected.
        The conditions
        3. Island do not touch, and
        4. There are not 2 x 2 sea areas
        are guarateed to be fullfiled.
        :return: Logic value of the proposition 'The solution is feasible.'
        """
        for island in self.islands:
            if not island.has_final_size():
                return False
            else:  # is connected?
                for field in island.fields:
                    break
                stack = [field]
                processed = {field}
                while stack:
                    top = stack.pop()
                    for neighbour in top.neighbours:
                        if neighbour not in processed:
                            processed.add(neighbour)
                            stack.append(neighbour)
                if processed != island.fields:
                    return False
        black_fields = 0
        starting_point = None
        for x in range(self.width):
            for y in range(self.height):
                if self.fields[y][x].is_part_of_sea():
                    if black_fields == 0:
                        starting_point = self.fields[y][x]
                    black_fields += 1
        if black_fields > 0:
            seen = set()
            stack = [starting_point]
            while stack:
                field = stack.pop()
                for neighbour in field.neighbours:
                    if neighbour not in seen and neighbour.is_part_of_sea():
                        seen.add(neighbour)
                        stack.append(neighbour)
                        if len(seen) == black_fields:
                            return True
            return False
        else:
            return True

    def feasible_components(self, xx, yy, offset=""):
        """
        Computes he list of components (islands or sea) that the field with coordinates (xx, yy) could be part of.
        :param xx: x-coordinate of the field
        :param yy: y-coordinate of the field
        :param offset: string, used for nicer printing in debugging
        :return: A list [(dist, component), ...] sorted increasingly by dist, where dist is the distance between
         (xx, yy) and the component in the case of proper island, and float('inf') in the case of the sea.
        """
        feasible_comp = []
        if DEBUG > 3:
            print(offset, "Computing components for", (xx, yy))
        # First, we find proper island candidates. We must check, whether the sea (if exists) remains connected.
        # When there is only one black field and it is completely surrounded by islands, we will fail to discover
        # this already in this step.
        must_see = 0
        black_field = None
        for x in range(self.width):
            for y in range(self.height):
                if self.fields[y][x].is_part_of_sea():
                    if must_see == 0:
                        black_field = self.fields[y][x]
                    must_see += 1
        can_be_island = True
        if must_see > 0:
            if DEBUG > 3:
                print(offset, "Have to find {} black field(s).".format(must_see))
            processed_nonwhite_fields = {black_field}
            seen = 1
            stack = [black_field]
            while stack and seen < must_see:
                if DEBUG > 5:
                    print(offset, "Removing the top from the stack:", stack)
                top = stack.pop()
                for neighbour in top.neighbours:
                    if DEBUG > 5:
                        print(offset, "neighbour", neighbour)
                    if not(neighbour in processed_nonwhite_fields or neighbour.is_part_of_proper_island() or (neighbour.x == xx and neighbour.y == yy)):
                        if DEBUG > 5:
                            print(offset, "goes to stack ...")
                        stack.append(neighbour)
                        processed_nonwhite_fields.add(neighbour)
                        if neighbour.is_part_of_sea():
                            if DEBUG > 5:
                                print(offset, "is also black")
                            seen += 1
            assert must_see >= seen
            can_be_island = must_see == seen
            if can_be_island:
                if DEBUG > 3:
                    print(offset, "Can be island, found all sea fields.")
            else:
                if DEBUG > 3:
                    print(offset, "Must not be island1")
        else:
            if DEBUG > 3:
                print(offset, "No sea --> can be island.")
        if can_be_island:
            # check which islands are the candidates
            neighbouring_islands = set(neighbour.island.component for neighbour in self.fields[yy][xx].neighbours if neighbour.is_part_of_proper_island())
            if len(neighbouring_islands) > 1:
                can_be_island = False  # more than 1 neighbouring island --> (xx, yy) cannot be part of an island
                if DEBUG > 3:
                    print(offset, "Cannot be part of the island (more than 1 neighbouring island)")
            elif len(neighbouring_islands) == 1:
                if DEBUG > 3:
                    print(offset, "1 neighbouring island", end="")
                for component in neighbouring_islands:  # get x for {x} ...
                    island = self.components[component]
                    if not island.has_final_size():
                        candidate_islands = self.nearby_islands(xx, yy, island)
                        assert candidate_islands == [] or candidate_islands == [(island, 1)]
                        if DEBUG > 3:
                            print(" which is a candidate", island)
                    else:
                        can_be_island = False
                        if DEBUG > 3:
                            print(" which is not a candidate", island)
            else:  # no neighbouring islands
                candidate_islands = self.nearby_islands(xx, yy)
                if DEBUG > 3:
                    print(offset, "No neighbouring islands, candidates:", candidate_islands)
        if can_be_island:
            feasible_comp += [(dist, island.component) for (island, dist) in candidate_islands]

        # Secondly, we check, whether (xx, yy) can be part of the sea.
        # 1. Check it this would cause any 2 x 2 sea area
        #
        #  ? x or   x ? or  ? ?  or  ? ?
        #  ? ?      ? ?     x ?      ? x
        #
        can_be_sea = True
        if xx > 0:
            if yy > 0:  # 1
                if all([field.is_part_of_sea() for field in [self.fields[yy][xx - 1], self.fields[yy - 1][xx - 1], self.fields[yy - 1][xx]]]):
                    can_be_sea = False
            if yy < self.height - 1 and can_be_sea:  # 4
                if all([field.is_part_of_sea() for field in [self.fields[yy][xx - 1], self.fields[yy + 1][xx - 1], self.fields[yy + 1][xx]]]):
                    can_be_sea = False
        if xx < self.width - 1 and can_be_sea:
            if yy > 0:  # 2
                if all([field.is_part_of_sea() for field in [self.fields[yy - 1][xx], self.fields[yy - 1][xx + 1], self.fields[yy][xx + 1]]]):
                    can_be_sea = False
            if yy < self.height - 1 and can_be_sea:  # 3
                if all([field.is_part_of_sea() for field in [self.fields[yy + 1][xx], self.fields[yy + 1][xx + 1], self.fields[yy][xx + 1]]]):
                    can_be_sea = False
        # 2. Check, whether there is an island that has not reached its final size yet, and has not enough space to do
        #    that: will not do that, because we always try island components first.

        # 3. Chech, whether we would isolate an island field,
        #    so that it could not be connected to the rest of the island
        if can_be_sea:
            for neighbour in self.fields[yy][xx].neighbours:
                if neighbour.is_part_of_proper_island() and neighbour.island.final_size > 1:
                    expansion_directions = 0
                    for neigh_neighbour in neighbour.neighbours:
                        if not neigh_neighbour.is_part_of_sea():
                            expansion_directions += 1
                    if expansion_directions <= 1:  # we would close the only possible direction
                        if DEBUG:
                            print(offset, "Must not close expansion direction!")
                        can_be_sea = False
                        break
        if can_be_sea:
            feasible_comp.append((float("inf"), SEA))
            if DEBUG > 3:
                print(offset, "Can be sea")
        else:
            if DEBUG > 3:
                print(offset, "Cannot be sea")
        if DEBUG > 3:
            print(offset, "feasible components", feasible_comp)
        return feasible_comp

    def show_partial_solution(self, offset, condensed=False):
        if not condensed:
            print(offset, end="")
            for i in range(self.width):
                print("{: >4}   ".format(i), end="")
        print()
        for y in range(self.height):
            print(offset, end="")
            for x in range(self.width):
                print(self.fields[y][x].island_size(condensed), end="")
            print(" ", y)
    
    def solve(self, only_untill_first_solution, offset=""):
        if self.number_of_steps % 200 == 0:
            print(self.number_of_steps)
        if DEBUG:
            print()
            if DEBUG and self.pencil_paper_solution is not None:
                is_ok, problematic_x, problematic_y = self.check_partial_solution()
                ok_branch = "" if is_ok else "not ({}, {}) ".format(problematic_x, problematic_y)
                print(offset, "I am {}in the right branch.".format(ok_branch))
            self.show_partial_solution(offset, condensed=True)

        if not self.unknown:
            # is the solution feasible
            if self.is_feasible():
                print("Found solution:")
                self.show_partial_solution("", condensed=True)
                self.number_feasible_solutions += 1
                if self.pencil_paper_solution is not None:
                    is_ok, problematic_x, problematic_y = self.check_partial_solution()
                    print("Coincides with pencil/paper:", is_ok, problematic_x, problematic_y)
                return only_untill_first_solution
        else:
            possibilities = []
            chosen_field, components = None, None
            for field in self.unknown:
                possibilities.append((field, self.feasible_components(field.x, field.y, offset)))
                if len(possibilities[-1][1]) <= 1:  # one or zero possibilities
                    (chosen_field, components) = possibilities[-1]
                    break
            if DEBUG > 5:
                for x in possibilities:
                    print(offset, x)
            if chosen_field is None:
                (chosen_field, components) = min(possibilities, key=lambda t: (len(t[1]), t[1][0]) if len(t[1]) > 0 else (0, -float("inf")))
            assert chosen_field.has_no_island()
            if DEBUG:
                print(offset, chosen_field, components)
                if not components:
                    print(offset, "No options!", chosen_field, components)
                if len(components) > 1:
                    print(offset, "Must guess ...")
            for (dist, comp) in components:
                island = self.components[comp]

                self.unknown.remove(chosen_field)
                chosen_field.island = island
                island.fields.add(chosen_field)
                
                self.number_of_steps += 1
                
                if self.solve(offset + "  "):
                    return True

                self.unknown.add(chosen_field)
                chosen_field.island = None
                island.fields.remove(chosen_field)

            return False

    def get_number_of_solutions(self):
        self.solve(only_untill_first_solution=False)
        print("Number of solutions:", self.number_feasible_solutions)
