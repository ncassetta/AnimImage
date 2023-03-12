##    This file is part of
##    animimage - Simple animated Sprite extension for pygame
##    Copyright (C) 2023  Nicola Cassetta
##    See <https://github.com/ncassetta/Nictk>
##
##    This file is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This code is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this file; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import _setup
from random import randrange
import pygame
import animimage

# colors for squares
COLORS = ("red", "yellow", "blue", "orange", "green", "purple")

pygame.init()
screen = pygame.display.set_mode((800, 600))
clk = pygame.time.Clock()

all_sprites = pygame.sprite.LayeredUpdates()

# uncomment this to see debug info about sprites
#animimage.set_debug(True)

# position the 1st square
surf = pygame.Surface((60, 60))
surf.fill(COLORS[randrange(len(COLORS))])
rect = surf.get_rect()
rect.topleft = randrange(740), randrange(540)

# flag for exiting the main loop
done = False
# main loop
while not done:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            done = True
        # when you click on the square ...
        elif ev.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(ev.pos):
            # ... a VanishSprite is created from it ...
            anim = animimage.VanishSprite(all_sprites)
            anim.set_image(surf.copy())
            # ... random parameters are given ...
            rate = randrange(2, 9) / 2
            scale = randrange(11, 20) / 10
            frames = randrange(4, 11)
            direct = randrange(-4, 5), randrange(-4, 5)
            anim.set_param(rate=rate, scale=scale, frames=frames, dir=direct)
            anim.rect = rect.copy()
            # ... and another square is created
            rect.topleft = randrange(740), randrange(540)
            surf.fill(COLORS[randrange(len(COLORS))])        
    
    screen.fill("aqua")
    # make all animation progress
    all_sprites.update()
    all_sprites.draw(screen)
    screen.blit(surf, rect)
    pygame.display.flip()
    clk.tick(30)
    
pygame.quit()
            
    
