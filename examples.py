from nurikabe import *
from saveAndLoad import *


ind = 23

wid, hei, stems = load_nurikabe(ind)
solution = None  # load_solution(ind)  # write_solution(wid, hei, ind)#

playground = Nurikabe(wid, hei, stems, solution)
playground.get_number_of_solutions()
