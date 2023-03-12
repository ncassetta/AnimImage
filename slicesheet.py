import pygame

class SheetSlicer:
    """An object which splits a rectangular image into subframes.
    You can split a pygame Surface or a file with the slice() method,
    returning its frames as a list of pygame Surface objects. Then you
    can get them with the get_images() method or save them with the
    save_images() method.
    """    
    def __init__(self):
        """The constructor."""
        self._fname = ""
        self._images = []

    def slice(self, sheet, h, v, orig_w=None, orig_h=None):
        """Split a rectangular image into subframes and return them as a list
        of pygame Surface.
        You can get the list of images also with the get_images() method.
        \param sheet can be a pygame Surface or a string: in this case it is
        interpreted as a filename, and the method will try to load it.
        \param h, v the number of frames for horizontal and vertical side: the
        method assumes all they have the same width/height.
        \param orig_w, orig_h if you leave **None** the method uses the total
        width/height of the Surface to calculate the subframes width/height.
        The width and height of a subframe will be _orig_w_ // _h_ and 
        _orig_h_ // _v_ (where // stands for the integer division).
        In some cases you can get better results setting a different _orig_w_
        and _orig_h_ than the Surface dimensions.
        """        
        if isinstance(sheet, str):
            try:
                temp = pygame.image.load(sheet).convert_alpha()
            except:
                raise
            else:
                self._fname = sheet = temp
        else:
            self._fname = ""
        if orig_w == None:
            orig_w = sheet.get_width()
        if orig_h == None:
            orig_h = sheet.get_height()
        self._images = []
        width, height = orig_w // h, orig_h // v
        surf = pygame.Surface((width, height), flags=sheet.get_flags(), depth=sheet.get_bitsize())
        for i in range(v):
            for j in range(h):
                surf.fill((0, 0, 0, 0) if surf.get_bitsize() == 32 else (0, 0, 0))
                rect = pygame.Rect(width * j, height * i, width, height)
                surf.blit(sheet, (0, 0), area=rect)
                self._images.append(surf.copy())
        return self._images
    
    def get_images(self, first=0, last=None):
        """Return the list of images of the last sliced Surface.
        \param first the index of the first image to get.
        \param last the index of the first image **not** to get (as in the
        _range_ function); if you leave **None** you will get all images up
        to the last one."""
        if last == None:
            last = len(self._images)
        return self._images[first:last]
    
    def save_images(self, first=0, last=None, prefix=None, form="04d", ext=".png"):
        """Save the single frames of the last sliced pygame Surface into separate files.
        It appends to the file name a numeric suffix in order to get different
        names easy to load.
        \param first the index of the first image to save.
        \param last the index of the first image **not** to save (as in the
        _range_ function); if you leave **None** you will save all images up
        to the last one.
        \param prefix if you specified the Surface as a file in the slice() method you
        can leave **None** and the the method will use the same name as prefix,
        otherwise you **must** specify the prefix or you will get an error.
        \param form a format for the numeric suffix: this is a format specifier
        of the string format() method (without trailing :) If you leave the default
        the files will be named "prefix0001", "prefix0002", "prefix0003" etc.
        \param ext you can choose ".png", ".jpg" or ".jpeg"
        """
        if (self._images):
            if not prefix:
                if self._fname:
                    prefix = self._fname
                else:
                    raise ValueError("You must specify the prefix parameter")
            if ext not in (".png", ".jpg", "jpeg"):
                raise ValueError("Invalid extension") 
            s = prefix + "{:" + form + "}" + ext
            if last == None:
                last = len(self._images)            
            for i in range(first, last):
                fname = s.format(i)
                with open(fname, "r+b") as f:
                    pygame.image.save_extended(self._images[i], f)
        else:
            raise ValueError("Empty image list")
        
    




def viewlist(images, interval=1000):
    """Helper function which shows a list of pygame Surfaces as an animation.
    It opens a pygame screen.
    \param images an iterable containing pygame Surface objects.
    \param interval the frame rate in milliseconds."""
    was_init = pygame.get_init()
    w = max([x.get_width() for x in images])
    h = max([x.get_height() for x in images])    
    if not was_init:
        pygame.init()
    screen = pygame.display.set_mode((max(w + 20, 100), max(h + 50, 100)))
    textstart = (10, h + 20)
    fnt = pygame.font.SysFont("Arial", 12)
    for i in range(len(images)):
        pygame.event.get()
        screen.fill("white")
        screen.blit(images[i], (10, 10))
        screen.blit(fnt.render("Image " + str(i + 1), "blue", True), textstart)
        pygame.display.flip()
        pygame.time.wait(interval)
    if not was_init:
        pygame.quit()

if __name__ == "__main__":
    fname = input("File name: ")
    horiz = int(input("Horizontal frames: "))
    vert = int(input("Vertical frames: "))
    images = slicesheet(fname, horiz, vert)
    viewlist(images, 2000)