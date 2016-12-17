from os.path import exists


def write_nurikabe(ind):
    """
    User friendly way for saving nurikabe. The description of the nurikabe is saved to 'nurikabe<ind>.txt'.
    :param ind: index of the nurikabe.
    :return: width, heigh, island stems, where island stems is a list of form [(stem_x, stem_y, island size), ...].
    """
    width = int(input("Width: "))
    height = int(input("Height: "))
    print("Enter the island stems. For a given coordinate y, enter size<space>x, for each island.")
    print("Once you are done with the current y, enter the empty string''.")
    stems = []
    for y in range(height):
        end = False
        print("y =", y)
        while not end:
            try:
                a = input("size<space>x: ")
                if a == "":
                    end = True
                else:
                    size, x = [int(t) for t in a.split(" ")]
                stems.append((x, y, size))
            except ValueError:
                print("Something went frong, the last description has no effect.")
    with open("nurikabe{}.txt".format(ind), "w") as f:
        print("width;" + str(width), file=f)
        print("height;" + str(height), file=f)
        print("stems;" + str(stems), file=f)

    return width, height, stems


def load_nurikabe(ind):
    """
    Loads nurikabe from the file 'nurikabe<ind>.txt'.
    :param ind: index of the nurikabe
    :return: Description of the nurikabe.
    """
    nuri = []
    with open("nurikabe{}.txt".format(ind)) as f:
        for x in f:
            nuri.append(eval(x[x.find(";") + 1:].strip()))
    return nuri


def write_solution(width, height, ind):
    """
    User friendly way for saving the pencil-paper solution.
    The solution is saved to the file 'nurikabe<ind>solution.txt'.
    :param width: width of the nurikabe
    :param height: height of the nurikabe
    :param ind: index of the nurikabe
    :return: The solution
    """
    a = [["" for _ in range(width)] for _ in range(height)]
    print("Enter the solution of dimensions {} x {}".format(width, height))
    print("If a line in the solution is '7 2 sea sea 3 unknown 1', enter '72003-1'.")
    print("If the size of an island is greater than 9, i.e. needs more than one place,")
    print("enter first a string s for which len(s) != width and than follow the example:")
    print("For a line '7 12 sea sea unknown 123' enter '7,12,0,0,-,123'")
    for i in range(height):
        vrsta = input("y = {}: ".format(i))
        u = vrsta.strip()
        while len(u) != width:
            print("Wrong width:", len(u), "try again, now coma-separated!")
            vrsta = input("y = {}: ".format(i))
            u = vrsta.strip().split(",")
        for j in range(width):
            a[i][j] = "" if u[j] == "-" else int(u[j])
    out = "nurikabe{}solution.txt".format(ind)
    if exists(out):
        ali = bool(input("Solution already exists. Do you want to overwrite it [true/false]? "))
    else:
        ali = True
    if ali:
        with open(out, "w") as f:
            print(a, file=f)
    return a


def load_solution(ind):
    """
    Loads solution for nurikabe with given index.
    :param ind: index of the nurikabe
    :return: solution of the nurikabe
    """
    solution = "nurikabe{}solution.txt".format(ind)
    with open(solution) as f:
        return eval(f.readline())
