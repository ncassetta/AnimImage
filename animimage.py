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

"""pygame module with animated Sprite class.

This module contains a simple AnimSprite (animated Sprite) class to be used
within pygame. It is a subclass of the Sprite object, so it can be added
and deleted to groups via usual pygame methods.
Before using an AnimSprite you must call the set_images() method which
initializes the list of its frames, then you can make the animation
to progress calling the update() method on a Group it belongs. When
subclassing the AnimSprite class remember, if you subclass the update()
method, to call the base class method.

"""

import pygame.sprite

_debug = False

def set_debug(f):
    """Turn on/off the debug mode.
    
    When you import the file debug mode is disabled, if the user turns it
    on the various methods will print additional informations on the
    console.
    """
    global _debug
    _debug = f


class AnimSprite(pygame.sprite.Sprite):
    """An animated Sprite class to be used within pygame.
    
    You can set for it a list of frames (pygame Surface) which will be shown in sequence
    calling the update() method; moreover you can choose between a one-shot animation
    (the Sprite will be killed at the end of the sequence) or a repeated one and set the
    animation speed.
    
    It is a subclass of the Sprite object, so it can be added and deleted to groups via
    usual pygame methods. Before using an AnimSprite you must call the set_images() method
    which initializes the list of its frames, then you can make the animation to progress
    calling the update() method on a Group it belongs. When subclassing the AnimSprite
    class remember, if you subclass the update() method, to call the base class method.
    """

    def __init__(self, *args):
        """The constructor. 
        
        You can add here the AnimSprite to one or more Group, passing them as parameters.
        You should consider creating a Group of only AnimSprite (or FlashSprite and
        VanishSprite), so you can call update() on it keeping all animations in progress.
        """
        pygame.sprite.Sprite.__init__(self, *args)
        
        ## The list of all frames.
        self.images = []
        ## The speed rate.
        self.rate = 1
        ## **True** if the animation is loop.
        self.loop = False
        ## The current frame of the animation.
        self.frame = 0
        self._rate_offset = 0
        ## **True** if the animation is in process, **False** if it is stopped.
        self.running = False
        ## The Sprite actual image
        self.image = None
        ## The Sprite actual Rect
        self.rect = None
        
    def set_images(self, img_list, loop=False):
        """Set the list of the animation frames and start the animation.
        
        You must call this before using the object.
        \param img_list an iterable which can contain strings (they are interpreted
        as filenames, and the method will try to load them) or Surface objects;
        \param loop if **False** the Sprite will be killed (i.e\. deleted from all
        Group it belongs) after the last frame, otherwise the animation will restart
        from the first frame and you must kill or stop it by yourself.
        \note this method assigns to the Sprite _rect_ attribute the Rect got from
        the 1st Surface, so all frames should have the same dimensions or you may get
        unexpected behaviour.
        """
        for obj in img_list:
            if isinstance(obj, str):
                self.images.append(pygame.image.load(obj).convert_alpha())
            elif isinstance(obj, pygame.Surface):
                self.images.append(obj)
        self.loop = loop
        ## The sprite rect
        self.rect = self.images[0].get_rect() if self.images else None
        self.frame = 0
        ## The sprite image
        self.image = self.images[0] if self.images else None
        self._rate_offset = 0
        self.running = True
        if _debug:
            print("Frame 0 AnimSprite animation started")

    def anim_stop(self, frame=None):
        """Stop the animation.
        
        The Sprite remains visible, but calling update() will no longer progress to
        the next frame.
        \param frame if you leave None the animation will stop on the actual frame,
        otherwise you can choose the fixed frame to show. It throws an exception if
        frame is out of range.
        """
        self.running = False
        if frame:
            if frame >= len(self.images):
                raise IndexError("List index out of range")
            self.frame = frame
            self.image = self.images[self.frame]
        if _debug:
            print("Frame", self.frame, "AnimSprite animation stopped")        
    
    def anim_start(self, frame=None):
        """Restart an animation which had been stopped by anim_stop().
        
        Animations are automatically started when you call set_images(), so you need
        this only if you had formerly stopped the animation.
        \param frame if you leave None the animation will restart from the last frame
        on which it was stopped, otherwise you can set the starting frame. It throws
        an exception if frame is out of range.
        """
        if frame:
            if frame >= len(self.images):
                raise IndexError("List index out of range")
            self.frame = frame
            self.image = self.images[self.frame]
        self.running = True
        self._rate_offset = 0
        if _debug:
            print("Frame", self.frame, "AnimSprite animation restarted")        
        

    def set_rate(self, rate):
        """Set the speed of the animation.
        
        This is relative to the update() calls, i.e\. a rate of 1 will change frame
        at every call of update(), a rate of 2 every two calls, and so on. The
        parameter can be a float number.
        """
        self.rate = rate
        self._rate_offset = 0

    def update(self):
        """Make the animation avance.
        
        The object has an internal attribute _rate_offset_. At every call of this
        _rate_offset_ is incremented by one and, if it is greater or equal to the
        animation rate, the frame is changed (and _rate_offset_ is decremented by
        the rate). This allows to set a float as rate.
        
        Moreover, if we have reached the last frame and must change it, this checks
        if the loop is enabled: if yes it Restarts from the first frame, otherwise
        it calls self.kill() deleting the object from all Group it belongs (so the
        object will no longer be drawn).
        """
        if self.images and self.running:
            self._rate_offset += 1
            if self._rate_offset >= self.rate:
                self._rate_offset -= self.rate
                self.frame += 1
                if _debug:
                    print("Frame", self.frame) 
                if self.frame == len(self.images):
                    self.frame = 0
                    if not self.loop:
                        self.kill()
                self.image = self.images[self.frame]

    def set_loop(loop):
        """Enable or disable the animation loop.
        
        \param loop if **False** the Sprite will be killed (i.e\. deleted from all
        Group it belongs) after the last frame, otherwise the animation will restart
        from the first frame and you must kill or stop it by yourself.
        """
        if loop in (True, False):
            self.loop = loop



class VanishSprite(pygame.sprite.Sprite):
    """A vanishing Sprite class to be used within pygame.
    
    Starting from a given image (pygame Surface) it generates a list of frames with
    increasing transparence which will be shown in sequence calling the update() method,
    giving the impression of a disappearing image. The sprite can change its dimensions
    (growing or shrinking) and move in a fixed direction during the animation, and the
    user can set the animation speed.
    
    It is a subclass of the Sprite object, so it can be added and deleted to groups via
    usual pygame methods. Before using a VanishSprite you must call the set_image() method
    which sets the initial image and its Rect, then you can make the animation to progress
    calling the update() method on a Group it belongs. When subclassing the VanishSprite
    class remember, if you subclass the update() method, to call the base class method.
    """    
    
    def __init__(self, *args):
        """The constructor.
        
        You can add here the VanishSprite to one or more Group, passing them as parameters.
        You should consider creating a Group of only VanishSprite (or FlashSprite and
        AnimSprite), so you can call update() on it keeping all animations in progress.
        """
        pygame.sprite.Sprite.__init__(self, *args)
        self.image, self.rect = None, None
        self.set_param()
        self.running = False
        
    def set_image(self, img):
        """Set the initial image of the animation and start the animation.
        
        You must call this before using the object.
        \param img can be a string (which is interpreted as a filename, and the method
        will try to load it) or a Surface object.
        """
        if isinstance(img, str):
            self.orig_image = pygame.image.load(img).convert_alpha()
        elif isinstance(img, pygame.Surface):
            self.orig_image = img.convert_alpha()
        self.rect = self.imag.get_rect() if self.image else None
        self._rate_offset = 0
        self.frame = 0
        self.image = self.orig_image
        self.rect = self.orig_image.get_rect()
        self.running = True
        if _debug:
            print("Frame 0 VanishSprite animation started")        

    def anim_stop(self, frame=None):
        """Stop the animation.
        The Sprite remains visible, but calling update() will no longer progress to
        the next frame.
        \param frame if you leave None the animation will stop on the actual frame,
        otherwise you can choose the fixed frame to show. It throws an exception if
        frame is out of range.
        """
        self.running = False        
        if frame:
            if frame >= self.frames:
                raise IndexError("List index out of range")
            self.frame = frame
            self._set_current_image()
        if _debug:
            print("Frame", self.frame, "VanishSprite animation stopped")        
    
    def anim_start(self, frame=None):
        """Restart an animation which had been stopped by anim_stop().
        
        Animations are automatically started when you call set_image(), so you need
        this only if you had formerly stopped the animation.
        \param frame if you leave None the animation will restart from the last frame
        on which it was stopped, otherwise you can set the starting frame. It throws
        an exception if frame is out of range.
        """        
        if frame:
            if frame >= self.frames:
                raise IndexError("List index out of range")
            self.frame = frame
            self._set_current_image()
        self._rate_offset = 0
        self.running = True
        if _debug:
            print("Frame", self.frame, "VanishSprite animation restarted")        
        
    def set_param(self, rate=1, scale=1, frames=4, dir=(0, 0)):
        """Set the parameters of the animation.
        
        \param rate the speed of the animation. This is relative to the update()
        calls, i.e\. a rate of 1 will change frame at every call of update(), a rate
        of 2 every two calls, and so on. The parameter can be a float number.
        \param scale a scale factor (integer or float) between a frame and the
        previous, so the image can grow or shrink while disappearing.
        \param frames the number of frames the animation will take to disappear. Each
        of them will be assigned increasing transparency. Increasing this parameter
        the animation will be smoother.
        \param dir the direction along which the sprite will move during the animation.
        It is a duple of integers with the x, y values ​(in pixels) ​of the direction
        vector. 
        """
        self.rate = rate
        self._rate_offset = 0
        self.frame = 0
        self.scale = scale
        self.frames = frames
        self.trans_amt = 256 // int(frames) + 1
        self.dir = dir

    def update(self):
        """Make the animation avance.
        
        The object has an internal attribute _rate_offset_. At every call of this
        _rate_offset_ is incremented by one and, if it is greater or equal to the
        animation rate, the frame is changed (and _rate_offset_ is decremented by
        the rate). This allows to set a float as rate.
        
        When the animation reaches its last frame it calls self.kill() deleting the
        object from all Group it belongs (so the object will no longer be drawn).
        """
        if self.orig_image and self.running:
            if self.frame == 0:
                # first visualization: image and rect already set by set_image()
                self.frame = 1
                if _debug:
                    print("Frame", self.frame, "Dimensions", self.image.get_size(), "Alpha 255")
            else:
                self._rate_offset += 1
                if self._rate_offset >= self.rate:
                    self._rate_offset -= self.rate
                    self.frame += 1
                    if self.frame > self.frames:
                        self.kill()
                        return
                    self._set_current_image()
                        
    def _set_current_image(self):
        ## Internal function
        scale_amt = (int(self.orig_image.get_width() * (1 + (self.scale - 1) / self.frames * self.frame)),
                     int(self.orig_image.get_height() * (1 + (self.scale - 1) / self.frames * self.frame)))
        if scale_amt != (0, 0):
            img = pygame.transform.smoothscale(self.orig_image, scale_amt)
        else:
            img = self.orig_image
        img.set_alpha(255 - self.trans_amt * self.frame)
        self.image = img
        center = (self.rect.centerx + self.dir[0], self.rect.centery + self.dir[1])
        self.rect = img.get_rect()
        self.rect.center = center
        if _debug:
            print("Frame", self.frame, "Dimensions", self.image.get_size(), "Alpha", img.get_alpha())        



class FlashSprite(pygame.sprite.Sprite):
    """A flashing Sprite class to be used within pygame.
    
    Starting from a given image (pygame Surface) it shows and hides it for a given number
    of times calling the update() method. After them you can choose if mantaining the Sprite
    shown or not.
    
    It is a subclass of the Sprite object, so it can be added and deleted to groups via
    usual pygame methods. Before using a FlashSprite you must call the set_image() method
    which sets the initial image and its Rect, then you can make the animation to progress
    calling the update() method on a Group it belongs. When subclassing the FlashSprite
    class remember, if you subclass the update() method, to call the base class method.
    """        
    def __init__(self, *args):
        """The constructor.
        
        You can add here the FlashSprite to one or more Group, passing them as parameters.
        You should consider creating a Group of only FlashSprite (or VanishSprite and
        AnimSprite), so you can call update() on it keeping all animations in progress.
        """
        pygame.sprite.Sprite.__init__(self, *args)
        self.image = None
        self.toberemoved = None
        self.set_param()
        self.running = False
        
    def set_image(self, img):
        """Set the initial image of the animation and start the animation.
        
        You must call this before using the object.
        \param img can be a string (which is interpreted as a filename, and the method
        will try to load it) or a Surface object.
        """
        if isinstance(img, str):
            self.orig_image = pygame.image.load(img).convert_alpha()
        elif isinstance(img, pygame.Surface):
            self.orig_image = img.convert_alpha()
        if self.orig_image:
            self.rect = self.orig_image.get_rect()
            self.orig_alpha = self.orig_image.get_alpha()
        else:
            self.rect = self.orig_alpha = None
        self._rate_offset = 0
        self.frame = 0
        self.image = self.orig_image
        self.rect = self.orig_image.get_rect()
        self.running = True
        if _debug:
            print("Frame 0 FlashSprite animation started")        

    def anim_stop(self, frame=None, visible=False):
        """Stop the animation.
        
        The Sprite remains visible, but calling update() will no longer progress to
        the next frame.
        \param frame if you leave None the animation will stop on the actual frame,
        otherwise you can choose the fixed frame to show. It throws an exception if
        frame is out of range.
        \param visible if you set it True the flashing will be stopped when the Sprite
        is visible, otherwise it can be stopped even if the Sprite is actually invisible.
        """   
        if frame and frame >= self.flashes * 2:
            raise IndexError("list index out of range")
        self.running = False
        if frame == None:
            frame = self.frame
        if visible and frame % 2:
            frame -= 1
        self.frame = frame
        self._set_current_image()
        if _debug:
            print("Frame", self.frame, "FlashSprite animation stopped")        
        
    def anim_start(self, frame=None):
        """Restart an animation which had been stopped by anim_stop().
        
        Animations are automatically started when you call set_images(), so you need
        this only if you had formerly stopped the animation.
        \param frame if you leave None the animation will restart from the last frame
        on which it was stopped, otherwise you can set the starting frame. It throws
        an exception if frame is out of range.
        """        
        if frame:
            if frame >= self.flashes * 2:
                raise IndexError("List index out of range")
            self.frame = frame
            self._set_current_image()
        self._rate_offset = 0
        self.running = True
        if _debug:
            print("Frame", self.frame, "AnimSprite animation restarted")        
        
    def set_param(self, rate=1, flashes=3, hold=False):
        """Set the parameters of the animation.
        
        \param rate the speed of the animation. This is relative to the update()
        calls, i.e\. a rate of 1 will change frame at every call of update(),
        a rate of 2 every two calls, and so on. The parameter can be a float
        number.
        \param flashes the number of flashes (appearing and disappearing) of the
        animation. It must be an integer, or an exception will be thrown. You can
        give -1 for a continuosly flashing image.
        \param hold if you leave **False** the Sprite will disappear after the
        last flash, otherwise it will remain as a still image.
        """        
        self.rate = rate
        self._rate_offset = 0
        self.frame = 0
        self.flashes = int(flashes)
        self.hold = hold
        
    def set_remove(self, *args):
        """Set a list of pygame Group from which the Sprite will be removed after the
        end of the flashes, even if it is held shown.
        
        This is useful if you have set a Group of only animated sprites and call update()
        on it for progressing the animations. When the Sprite ends flashing you can
        remove it from the Group, avoiding useless calls.
        """
        self.toberemoved = args

    def update(self):
        """Make the animation avance.
        
        The object has an internal attribute _rate_offset_. At every call of this
        _rate_offset_ is incremented by one and, if it is greater or equal to the
        animation rate, the frame is changed (and _rate_offset_ is decremented by
        the rate). This allows to set a float as rate.
        
        When the animation reaches its last frame (and _hold_ is set to **False**)
        it calls self.kill() deleting the object from all Group it belongs (so the
        object will no longer be drawn).
        """        
        if self.orig_image and self.running:
            self._rate_offset += 1
            if self._rate_offset >= self.rate:
                self._rate_offset -= self.rate
                self.frame += 1
                if self.frame > 2 * self.flashes - 1 and self.flashes != -1:
                    if not self.hold:
                        self.kill()
                        if _debug:
                            print("Frame", self.frame, "Sprite killed")
                    else:
                        self.image.set_alpha(self.orig_alpha)
                        self.running = False
                        if self.toberemoved:
                            self.remove(self.toberemoved)
                        if _debug:
                            print("Frame", self.frame, "Sprite held")
                else:
                    self._set_current_image()
                                                       
    def _set_current_image(self):
        """Internal function."""
        if self.frame % 2:
            self.image.set_alpha(0)
            if _debug:
                print("Frame", self.frame, "Flash", self.frame // 2 + 1, "Image off")
        else:
            self.image.set_alpha(self.orig_alpha)
            if _debug:
                print("Frame", self.frame, "Flash", self.frame // 2 + 1, "Image on")
       
                

if __name__ == "__main__":
    pygame.init()
    fnt_big = pygame.font.SysFont("Arial", 48, bold=True)
    fnt_small = pygame.font.SysFont("Arial", 24)
    screen = pygame.display.set_mode((400, 300))
    screen.fill("aqua")
    surf = fnt_big.render("Animimage 0.9",True, "blue")
    screen.blit(surf, (60, 30))
    surf = fnt_small.render("A library for animated sprites in pygame", True, "blue")
    screen.blit(surf,(20, 120))
    surf = fnt_small.render("(C) 2023 Nicola Cassetta", True, "blue")
    screen.blit(surf, (80, 160))
    surf = fnt_small.render("See the example files for usage.", True, "blue")
    screen.blit(surf, (60, 200))
    pygame.display.flip()
    pygame.time.wait(3500)
    pygame.quit()




#pygame.display.init()
#clk = pygame.time.Clock()
#screen = pygame.display.set_mode((640, 480))

#l = ["explosion2-0.gif", "explosion2-1.gif", "explosion2-2.gif",
#     "explosion2-3.gif", "explosion2-4.gif", "explosion2-5.gif", "explosion2-6.gif",]
#img = AnimatedImage(l, (50, 50))
#img.set_rate(2)

#done = False
#while not done:
#    for event in pygame.event.get():
#        if event.type == QUIT:
#            done = True

#    screen.fill((0, 0, 0))
#    img.paint(screen)
#    pygame.display.flip()
#    clk.tick(30)

#pygame.quit()
