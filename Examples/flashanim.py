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

# data for flashing writings
TEXTS = ("Bonus", "Big win", "Next level", "Game over")
FONTS = ("Arial", "Courier", "Times", "Verdana") 
SIZES = (36, 48, 60, 72)
COLORS = ("yellow", "red", "dark green", "blue")

pygame.init()
screen = pygame.display.set_mode((800, 600))
clk = pygame.time.Clock()
CUSTOM_EV = pygame.event.custom_type()

all_sprites = pygame.sprite.Group()

# uncomment this to see debug info about sprites
#animimage.set_debug(True)

# set timer for triggering the 1st writing
pygame.time.set_timer(CUSTOM_EV, randrange(500, 2000))

# flags for paused and persistent mode
paused, persistent = False, False
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
                    # stop all animations, turning them on if invisible
                    # at this moment
                    for spr in all_sprites:
                        spr.anim_stop(visible=True)
                else:
                    # restart all stopped animations
                    for spr in all_sprites:
                        spr.anim_start()
                paused = not paused
            # pressing ALT toggles persistent mode
            elif ev.key == pygame.K_LALT:
                if not persistent:
                    for spr in all_sprites:
                        # turn all animations into persistent FlashSprite
                        spr.hold=True 
                else:
                    # delete all sprites
                    all_sprites.empty()
                persistent = not persistent
        # triggers a new writing
        elif ev.type == CUSTOM_EV:
            if not paused:
                # new FlashSprite
                anim = animimage.FlashSprite()
                # choose a random font, size, text and color and render it into a pygame Surface
                fnt = pygame.font.SysFont(FONTS[randrange(4)], SIZES[randrange(4)], bold=True, italic=randrange(2))
                surf = fnt.render(TEXTS[randrange(4)], True, COLORS[randrange(4)])
                # set the Surface as the FlashSprite image: this starts the animation
                anim.set_image(surf)
                # choose a random position for the writing
                anim.rect.topleft = (randrange(20, 800 - surf.get_width() - 20),
                                     randrange(20, 600 - surf.get_height() - 20))
                # check if the writing overlaps another animation (only if not in persistent mode)
                if not pygame.sprite.spritecollide(anim, all_sprites, False) or persistent:
                    # if not add the animation to the main Group, so it can be drawn
                    all_sprites.add(anim)
                    # set a random speed for flashing and persistent on if in persistent mode
                    anim.set_param(rate=randrange(10, 18) / 2, flashes=randrange(4, 9), hold=persistent)
            pygame.time.set_timer(CUSTOM_EV, randrange(2000, 3000))
    
    screen.fill("aqua")
    # make all animation progress
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clk.tick(30)
    
pygame.quit()
            
    
