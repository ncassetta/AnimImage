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
from os.path import join
from random import randrange
import pygame
import animimage

pygame.init()
screen = pygame.display.set_mode((800, 600))
clk = pygame.time.Clock()
CUSTOM_EV = pygame.event.custom_type()

images = []
dec = animimage.GIFDecoder()
images = dec.decode(join("..", "firework1.gif")).copy()
for img in images:
    img.set_colorkey(images[0].get_at((1, 0)))

all_sprites = pygame.sprite.Group()

# uncomment this to see debug info about sprites
#animimage.set_debug(True)

# set timer for triggering the 1st car
pygame.time.set_timer(CUSTOM_EV, randrange(500, 2000))

# flag for paused mode
paused = False
# flag for exiting the main loop
done = False
# main loop
while not done:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            done = True
        elif ev.type == pygame.KEYDOWN:
            # pressing SPACE toggles paused mode
            if ev.key == pygame.K_SPACE:
                if not paused:
                    # stop all animations
                    for spr in all_sprites:
                        spr.anim_stop()
                else:
                    # restart all stopped animations
                    for spr in all_sprites:
                        spr.anim_start()
                paused = not paused
        # trigger a new firework
        elif ev.type == CUSTOM_EV:
            # new AnimSprite
            anim = animimage.AnimSprite(all_sprites)
            # choose a random image (between two)
            anim.set_images(images)
            # choose a random height for the car
            anim.rect.topleft = (randrange(screen.get_width() - anim.rect.width),
                                 randrange(screen.get_height() - anim.rect.height))
            # check if the car overlaps another animation
            #if not pygame.sprite.spritecollide(anim, all_sprites, False):
                # if not add the animation to the main Group, so it can be drawn
                #all_sprites.add(anim)
                # set the animation rate
            anim.set_rate(randrange(6, 10) / 2)
            pygame.time.set_timer(CUSTOM_EV, randrange(2000, 6000))
    
    # make all animation progress
    all_sprites.update()
    screen.fill("black")
    all_sprites.draw(screen)
    pygame.display.flip()
    clk.tick(30)
    
pygame.quit()
            
    
