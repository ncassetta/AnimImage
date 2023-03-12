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

# slice a sheet of images into its components
slicer = animimage.SheetSlicer()
all_images = slicer.slice(join("..", "carro.png"), 10, 4, 2380)
# make from them four lists of animations:
# images[0] yellow car   images[1] blue car   images[2] red car    images[3] purple car 
images = (all_images[0:10], all_images[10:20], all_images[20:30], all_images[30:40])
all_sprites = pygame.sprite.Group()

# uncomment this to see debug info about sprites
#animimage.set_debug(True)

# the speed of the cars in pixel per 30th of sec. It can vary from 1.0 to 4.0 at
# steps of 0.5 
speed = 2.0
# the speed of animations in 30th of sec per frame (see animimage.set_rate())
anim_rate = 4 / speed
# internal variable (see below)
offset = 0.0
print("speed = {:2.1f}   anim_rate = {:4.2f}".format(speed, anim_rate))

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
            # pressing left and right arrows increments or decrements car speed
            elif ev.key in (pygame.K_LEFT, pygame.K_RIGHT):
                # set the new speed
                speed = max(1.0, speed - 0.5) if ev.key == pygame.K_LEFT else min(4.0, speed + 0.5)
                # update animation speed
                anim_rate = 4 / speed
                # reset offset
                offset = 0.0
                for spr in all_sprites:
                    spr.set_rate(anim_rate)
                print("speed = {:2.1f}   anim_rate = {:4.2f}".format(speed, anim_rate))
        # triggers a new car
        elif ev.type == CUSTOM_EV:
            # new AnimSprite
            anim = animimage.AnimSprite()
            # choose a random car (four different colours)
            anim.set_images(images[randrange(4)], True)
            # choose a random height for the car
            anim.rect.topleft = (-anim.rect.width, randrange(100, 400))
            # check if the car overlaps another animation
            if not pygame.sprite.spritecollide(anim, all_sprites, False):
                # if not add the animation to the main Group, so it can be drawn
                all_sprites.add(anim)
                # set the animation rate
                anim.set_rate(anim_rate)
            # if animations are stopped stops the new car
            if paused:
                anim.anim_stop()
            pygame.time.set_timer(CUSTOM_EV, randrange(2000, 6000))
            
    # if you have a non-integer speed you must alternate between speed - 0.5 and
    # speed + 0.5. So we need the variable offset tp get this
    offset += (speed % 1)
    for sp in all_sprites:
        sp.rect.x += (speed + (0.5 if offset == 1 else -0.5 if offset == 0.5 else 0.0))
        if sp.rect.x > screen.get_width():
            sp.kill()
    if offset == 1.0:
        offset = 0.0    
    
    screen.fill("aqua")
    # make all animation progress
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clk.tick(30)
    
pygame.quit()
            
    
