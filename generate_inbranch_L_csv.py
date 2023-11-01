PURPLE = (1,0,1)
RED = (1,0,0)
BLACK = (0,0,0)
WHITE = (1,1,1)
GRAY = (0.5,0.5,0.5)

FULL = 1
HIGH = 0.75
MEDIUM = 0.5
LOW = 0.25
INVISIBLE = 0

# string to draw a module
def module(cell, color, opacity):
    assert(len(cell)==3 and len(color)==3)
    return str(cell)[1:-1] + "," + str(color)[1:-1] + "," + str(opacity) + "\n"

def modules(cells, color=BLACK, opacity=MEDIUM):
    result = ""
    for cell in cells:
        result += module(cell, color, opacity)
    return result

# segment, rectangle, or rectangular prism with given cells as opposite corners
def prism_by_corners(cell1, cell2, color=BLACK, opacity=MEDIUM):
    (x1, x2) = (cell1[0], cell2[0])
    (y1, y2) = (cell1[1], cell2[1])
    (z1, z2) = (cell1[2], cell2[2])
    result = []
    for x in range(min(x1,x2), max(x1,x2)+1):
        for y in range(min(y1,y2), max(y1,y2)+1):
            for z in range(min(z1,z2), max(z1,z2)+1):
                result.append((x,y,z))
    return result

def difference(list1, list2):
    result = []
    for item in list1:
        if not item in list2:
            result.append(item)
    return result

def empty_box(x,y,z):
    assert(x>2 and y>2 and z>2)
    outer = prism_by_corners((0,0,0), (x-1,y-1,z-1))
    inner = prism_by_corners((1,1,1), (x-2,y-2,z-2))
    return difference(outer, inner)



file = open("inbranch_L_3D.csv", 'w')
inbranch_L_3D = [(3,3,1),(4,3,1),(5,3,1),
              (3,3,2),
              (3,3,3),
              (3,3,4)] + empty_box(10,7,8)
file.write(modules(inbranch_L_3D))
file.close()

file = open("inbranch_L_2D.csv", 'w')
inbranch_L_2D = [ cube for cube in inbranch_L_3D if cube[1]==3 ]
file.write(modules(inbranch_L_2D))
file.close()