import pygame

def slicesheet(sheet, h, v, orig_w=None, orig_h=None):
    if isinstance(sheet, str):
        sheet = pygame.image.load(sheet)
    if orig_w == None:
        orig_w = sheet.get_width()
    if orig_h == None:
        orig_h = sheet.get_height()
    images = []
    # w, h = sheet.get_width(), sheet.get_height()
    width, height = orig_w // h, orig_h // v
    surf = pygame.Surface((width, height), flags=sheet.get_flags(), depth=sheet.get_bitsize())
    for i in range(v):
        for j in range(h):
            #if trans:
            #    surf.fill(trans)
            surf.fill((0, 0, 0, 0) if surf.get_bitsize() == 32 else (0, 0, 0))
            rect = pygame.Rect(width * j, height * i, width, height)
            surf.blit(sheet, (0, 0), area=rect)
            images.append(surf.copy())
    return images

def viewlist(images, interval=1000):
    pygame.init()
    w = max([x.get_width() for x in images])
    h = max([x.get_height() for x in images])
    screen = pygame.display.set_mode((max(w + 20, 100), h + 50))
    textstart = (10, h + 20)
    fnt = pygame.font.SysFont("Arial", 12)
    for i in range(len(images)):
        pygame.event.get()
        screen.fill("white")
        screen.blit(images[i], (10, 10))
        screen.blit(fnt.render("Image " + str(i + 1), "blue", True), textstart)
        pygame.display.flip()
        pygame.time.wait(interval)


#fname = input("File name: ")
#images = slicesheet(fname, 10, 4)
#viewlist(images, 2000)