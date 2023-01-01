##    animimage - Simple animated Sprite extension for pygame
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
##
##    Nicola Cassetta
##    ncassetta@tiscali.it

import _setup
from os.path import join
import animimage, slicesheet
import pygame, random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clk = pygame.time.Clock()
GHOST_EV = pygame.event.custom_type()

all_images = slicesheet.slicesheet(join("..", "carro.png"), 10, 4, 2380)
images = (all_images[0:10], all_images[10:20], all_images[20:30], all_images[30:40])
all_sprites = pygame.sprite.LayeredUpdates()

pygame.time.set_timer(NEWCAR_EV, random.randrange(500, 2000))
done = False
while not done:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            done = True
        elif ev.type == NEWCAR_EV:
            anim = animimage.AnimSprite()
            anim.set_images(images[random.randrange(4)], True)
            anim.rect.topleft = (-anim.rect.width, random.randrange(150, 400))
            if not pygame.sprite.spritecollide(anim, all_sprites, False):
                all_sprites.add(anim)
                anim.set_rate(2.5)
            pygame.time.set_timer(NEWCAR_EV, random.randrange(2000, 6000))
            
    for sp in all_sprites:
        sp.rect.x += 2
        if sp.rect.x > screen.get_width():
            sp.kill()
    
    screen.fill("aqua")
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clk.tick(30)
    
pygame.quit()
            
    
