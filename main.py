
import PIL
from PIL import Image

PIXELS_PER_UNIT = 8

class Pixel:
    r = None # red
    g = None # green
    b = None # blue
    a = None # alpha
    def set(self, r=0, g=0, b=0, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __init__(self, r=0, g=0, b=0, a=255):
        self.set(r,g,b,a)

class Line2D:
    p1 = None
    p2 = None
    # Point-Slope Form
    # y - y1 = m(x - x1)
    m = None

    is_vertical = False

    def __init__(self, p1, p2 ):
        self.p1 = p1
        self.p2 = p2
        if p1[0] == p2[0]:
            self.is_vertical
            self.m = 2839
        else:
            self.m = (p2[1] - p1[1]) / (p2[0] - p1[0]) # slope=(y2-y1)/(x2-x1)

    def at(self, x):
        # To avoid dividing by zero. at() doesn't matter for vertical lines anyway
        if self.is_vertical:
            return 2839 # debug number

        # Solve for y in Point-Slope Form
        # y = m(x - x1) + y1
        return ( self.m * ( x - self.p1[0] ) + self.p1[1] )

    def over_or_under(self, p):
        # Vertical edges never get rendered
        if self.is_vertical:
            return False

        between_pts_x = ( p[0] >= self.p1[0] and p[0] <= self.p2[0] )
        if not between_pts_x: # not within x bounds
            return 0
        if between_pts_x and p[1] >= self.at(p[0]): # over or on
            return 1
        if between_pts_x and p[1] <= self.at(p[0]): # under or on TODO: not sure if <= is needed
            return -1
        return 9 # debug number

class Layer:
    name = None
    width = None
    height = None
    pixels = None
    def __init__(self, name, width, height, clr):
        self.name = name
        self.width = width
        self.height = height
        self.pixels = []
        for x_pix in range(width):
            self.pixels.append([])

            for y_pix in range(height):
                if clr != None:
                    self.pixels.append( Pixel(clr[0], clr[1], clr[2], clr[3]) )
                else:
                    self.pixels.append( Pixel(0,0,0,0) )


class Canvas:
    width = None
    height = None
    layers = None
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layers = []

    def new_layer(self, name=None, fill_pixel=(0,0,0,0)):
        if name == None:
            # Auto generate new layer name based on existing layers named this way
            name = "Layer "
            highest_defaultlynamedlayer = 0
            for existing_layer in self.layers:
                if existing_layer.name[0:6] == "Layer " and existing_layer.name[6:].isdigit():
                    curr_defaultlynamedlayer = int(existing_layer.name[6:])
                    if curr_defaultlynamedlayer > highest_defaultlynamedlayer:
                        highest_defaultlynamedlayer = curr_defaultlynamedlayer
            name += str(highest_defaultlynamedlayer)
        else:
            for layer in self.layers:
                if name == layer.name:
                    name += "."

        # Create the new layer
        self.layers.append( Layer(name, self.width, self.height, fill_pixel) )
        return (len(self.layers)-1)

    # Ignores z-values to make orthographic view
    def ortho_draw_tri(self, pts, layer_index, color):
        # pts = [[p,s,r], [p,s,r], [p,s,r]]
        if not len(pts) == 3:
            print("ortho_draw-tri() was passed a non-triangle")
            return

        # TODO: Determine angle to determine fill color
        # Currently fill color is hardcoded to max brightness

        # Make lines from points
        lines = []
        lines.append( Line2D(pts[0], pts[1]) )
        lines.append( Line2D(pts[1], pts[2]) )
        lines.append( Line2D(pts[2], pts[0]) )

        for y_pix in range(0, self.height):
            y = y_pix / PIXELS_PER_UNIT # TODO? correct?
            for x_pix in range(0, self.width):
                x = x_pix / PIXELS_PER_UNIT # TODO? correct?
                over_under_results = []
                for line in lines:
                    # TODO: This is always coming back False
                    over_under_results.append( line.over_or_under( [ x, y ] ) )
                # I think if there is a -1, a 1, and a 0, then the point is within the shape
                if(-1 in over_under_results and 1 in over_under_results): #and 0 in over_under_results):
                    self.layers[layer_index].pixels[x_pix][y_pix].set(color[0], color[1], color[2], color[3])
                else:
                    self.layers[layer_index].pixels[x_pix][y_pix].set(0,0,0,0) #TODO index out of range

    def avg_face_z(self, face, all_obj_points):
        sum = 0
        for point_id in face:
            sum += all_obj_points[point_id][2]
        return ( sum / len(face) )

    def ortho_draw_obj(self, obj, layer_index):
        # points = [[p,s,r], [p,s,r], [p,s,r]]
        # faces = [[pid1, pid2, pid3], [pid2, pid3, pid4],..]

        faces_temp = obj.faces
        faces_sorted = []
        while len(faces_sorted) != len(obj.faces):
            frontmost_face = faces_temp[0]
            for face in faces_temp:
                if self.avg_face_z(face, obj.points) > self.avg_face_z(frontmost_face, obj.points):
                    frontmost_face = face
            faces_sorted.append( frontmost_face )
            faces_temp.remove(frontmost_face)

        for face in faces_sorted:
            curr_face_points = []
            for point_id in face:
                curr_face_points.append(obj.points[point_id])
            self.ortho_draw_tri( curr_face_points, layer_index, obj.color )

        print("Rendered " + obj.name)
        return

    def render(self, objects):
        # Sort objects
        objs_sorted_z = sorted(objects, key=lambda obj: obj.psr[0][2]) # sort by z pos

        for obj in range(len(objs_sorted_z)):
            self.new_layer();
            self.ortho_draw_obj(object, obj_index)

        flattened = Layer(self.width, self.height, (0,0,0,255))
        for layer_index in range(0,len(self.layers)): # doesn't render background layer
            #flatten
            break

        # Initialize/overwrite self.pixels_tuples to a new list
        self.pixels_tuples = [[] for _ in range(0,len(self.layers[n].pixels))]
        for i in range(len(self.pixels_tuples)):
            self.pixels_tuples[i] = [[] for _ in range(0,len(self.layers[obj_index].pixels[i]))]

        # Make tuples out of the values in the lists
        for x in range(0,len(self.layers[0].pixels)):
            for y in range(0,len(self.layers[0].pixels[x])):
                with self.layers[new_layer_index].pixels[x][y] as p:
                    self.layers[new_layer_index].pixels_tuples[x][y] = ( p.r, p.g, p.b )
        return

    def display(self):
        img_mode = "RGB"
        img_size = (self.width, self.height)
        with self.bg_pixel as bg:
            img_bg = (bg.r, bg.g, bg.b)
        image = Image.new(img_mode, img_size, img_bg)
        image.putdata(self.pixels_tuples)

        img_path = "/Users/robert/myrendertests/myrendertest.jpg"
        image.save(img_path, "jpg")
        print("Saved Image with PIL to " + img_path)
        return


class Object:
    id = None # Must be initialized manually, when put into scene
    name = None
    points = None # List of the positions of all points
    faces = None # List of which points each face is made up of
    psr = None # Position Scale Rotation. Rotation in degrees
    color = None

    def __init__(self, name, points, faces, psr=[[0,0,0],[1,1,1],[0,0,0]], color=[200,200,200]):
        self.id = -1
        self.name = name
        self.points = points
        self.faces = faces
        self.psr = psr
        self.color = color

    def __init__(self, name, type_str, psr=[[0,0,0],[1,1,1],[0,0,0]], color=[200,200,200]):
        if type_str == "cube":
            points = [[-50, 50, -50], [50, 50, -50], [-50, 50, 50], [50, 50, 50],
                           [-50, -50, -50], [50, -50, -50], [-50, -50, 50], [50, -50, 50]]
            faces = [[0, 1, 2],
                          [1, 2, 3],
                          [0, 1, 4],
                          [1, 4, 5],
                          [0, 2, 4],
                          [2, 4, 6],
                          [2, 3, 6],
                          [3, 6, 7],
                          [3, 1, 7],
                          [1, 5, 7],
                          [4, 5, 6],
                          [5, 6, 7]]
        #elif type_str == "pyramid":
        else:
            self.id = -2
            print("Invalid object type_str: " + type_str)
            return

        self.__init__(name, points, faces, psr, color)

    def set_id(self, id):
        self.id = id

    def rotate(self, r_delta):
        # TODO: Do math to rotate points around psr[0]

        # Save rotation value
        self.psr[2][0] += r_delta[0]
        self.psr[2][1] += r_delta[1]
        self.psr[2][2] += r_delta[2]
        return

class Scene:
    canvas = None
    objects = None
    next_obj_id = None
    def __init__(self, canv_width, canv_height):
        self.canvas = Canvas(canv_width, canv_height)
        self.objects = []
        self.next_obj_id = 0

    def add_obj(self, object):
        object.id = self.next_obj_id
        self.next_obj_id += 1
        self.objects.append(object)

    def render(self):
        self.canvas.render(self.objects)
        self.canvas.display()

# What the user would do
def main():
    scene = Scene(1280, 720)
    cube = Object("mycube", "cube")
    scene.add_object(cube)
    print("rotating")
    cube.rotate([25,15,-5])
    print("rendering")
    scene.render()


    print("Done")
    return

if __name__ == '__main__':
    main()
