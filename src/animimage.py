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

_VERSION = "1.0.0"

import pygame.sprite


_debug = False

def set_debug(f):
    """Turn on/off the debug mode.
    
    When you import the file debug mode is disabled, if the user turns it
    on the various methods will print additional informations on the
    console.
    /param f **True** or **False**.
    """
    global _debug
    _debug = f
    
def version():
    """Prints on the console the version number."""
    print("animimage v", _VERSION, "\nCopyright Nicola Cassetta")
    

# ######################################################################
# ###
# ###           A n i m S p r i t e
# ###
# ######################################################################


class AnimSprite(pygame.sprite.Sprite):
    """An animated Sprite class to be used within pygame.
    You can set for it a list of frames (pygame Surface objects) which will be shown in
    sequence calling the update() method, choosing between a one-shot animation (the Sprite
    will be killed at the end of the sequence) or a repeated one.
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
        ## **True** if the animation restarts after the last frame, **False** otherwise.
        self.loop = False
        ## The current frame of the animation.
        self.frame = 0
        self._rate_offset = 0
        ## **True** if the animation is in process, **False** if it is stopped.
        self.running = False
        ## The Sprite actual image.
        self.image = None
        ## The Sprite actual Rect.
        self.rect = None
        
    def set_images(self, img_list, loop=False):
        """Set the list of the animation frames and start the animation.
        You **must** call this before using the object.
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
        self.rect = self.images[0].get_rect() if self.images else None
        self.frame = 0
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
        otherwise you can choose the fixed frame to show. It throws an IndexError if
        _frame_ is out of range.
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
        an IndexError if _frame_ is out of range.
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
        /param rate this is relative to the update() calls, i.e\. a rate of 1 will
        change frame at every call of update(), a rate of 2 every two calls, and so on.
        It can be a float number for finer adjustement (see update()).
        """
        self.rate = rate
        self._rate_offset = 0

    def update(self):
        """Make the animation avance.
        The object has an internal attribute _rate_offset_. At every call of this
        _rate_offset_ is incremented by one and, if it is greater or equal to the
        animation rate, the frame is changed (and _rate_offset_ is decremented by
        the rate). This allows to set a float as rate
        When the animation reaches its last frame it checks the _loop_ parameter: if
        it is **False** it calls self.kill() deleting the object from all Group it
        belongs (so the object will no longer be drawn), otherwise restarts from the
        first frame.
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
        You can do it also with the set_images() method, so you need this only if
        you want to change a formerly set parameter.
        \param loop if **False** the Sprite will be killed (i.e\. deleted from all
        Group it belongs) after the last frame, otherwise the animation will restart
        from the first frame and you must kill or stop it by yourself.
        """
        if loop in (True, False):
            self.loop = loop
            
            
# ######################################################################
# ###
# ###           V a n i s h S p r i t e
# ###
# ######################################################################


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
        ## The Sprite actual image.
        self.image = None
        ## The Sprite actual Rect.
        self.rect = None
        self.set_param()
        ## **True** if the animation is in process, **False** if it is stopped.
        self.running = False
        
    def set_image(self, img):
        """Set the initial image of the animation and start the animation.
        You must call this before using the object.
        \param img can be a string (which is interpreted as a filename, and the method
        will try to load it) or a Surface object.
        """
        if isinstance(img, str):
            ## The original image passed by set_image().
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
        otherwise you can choose the fixed frame to show. It throws an IndexError if
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
        an IndexError if frame is out of range.
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
        ## The speed rate.
        self.rate = rate
        self._rate_offset = 0
        ## The current frame of the animation.
        self.frame = 0
        ## The scale factor between a frame and the previous.
        self.scale = scale
        ## The number of frames the animation will take to disappear.
        self.frames = frames
        self._trans_amt = 256 // int(frames) + 1
        ## The direction of the movement (a duple x, y)
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
        img.set_alpha(255 - self._trans_amt * self.frame)
        self.image = img
        center = (self.rect.centerx + self.dir[0], self.rect.centery + self.dir[1])
        self.rect = img.get_rect()
        self.rect.center = center
        if _debug:
            print("Frame", self.frame, "Dimensions", self.image.get_size(), "Alpha", img.get_alpha())        


# ######################################################################
# ###
# ###           F l a s h S p r i t e
# ###
# ######################################################################


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
        ## The Sprite actual image.
        self.image = None
        ## The Sprite actual Rect.
        self.rect = None
        ## List of groups from whom the sprite will be removed after flashing
        self.toberemoved = None
        self.set_param()
        ## **True** if the animation is in process, **False** if it is stopped.
        self.running = False
        
    def set_image(self, img):
        """Set the initial image of the animation and start the animation. 
        You must call this before using the object.
        \param img can be a string (which is interpreted as a filename, and the method
        will try to load it) or a Surface object.
        """
        if isinstance(img, str):
            ## The original image set by set_image().
            self.orig_image = pygame.image.load(img).convert_alpha()
        elif isinstance(img, pygame.Surface):
            self.orig_image = img.convert_alpha()
        if self.orig_image:
            self.rect = self.orig_image.get_rect()
            self._orig_alpha = self.orig_image.get_alpha()
        else:
            self.rect = self._orig_alpha = None
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
        otherwise you can choose the fixed frame to show, where
        0 = show first time, 1 = hide first time, 2 = show second time ... until
        2 * self.flashes - 1. It throws an IndexError if frame is out of range.
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
        Animations are automatically started when you call set_image(), so you need
        this only if you had formerly stopped the animation.
        \param frame if you leave None the animation will restart from the last frame
        on which it was stopped, otherwise you can set the starting frame (see anim_stop()).
        It throws an IndexError if frame is out of range.
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
        ## The speed rate.
        self.rate = rate
        self._rate_offset = 0
        ## The current frame of the animation.
        self.frame = 0
        ## The number of flashes.
        self.flashes = int(flashes)
        ## If **True** the sprite remains shown after the flashing, otherwise it will be killed.
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
                        self.image.set_alpha(self._orig_alpha)
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
            self.image.set_alpha(self._orig_alpha)
            if _debug:
                print("Frame", self.frame, "Flash", self.frame // 2 + 1, "Image on")
                
                
# ######################################################################
# ###
# ###           G i f D e c o d e r
# ###
# ######################################################################
       

import time, os
from ctypes import *
                
# codes for GIF blocks
_IMAGE_SEPARATOR = 0x2C
_EXTENSION_INTRODUCER = 0x21
_GRAPHIC_CONTROL_EXTENSION = 0xF9
_COMMENT_EXTENSION = 0xFE
_PLAIN_TEXT_EXTENSION = 0x01
_APPLICATION_EXTENSION = 0xFF
_BLOCK_TERMINATOR = 0x00
_TRAILER = 0x3B
# values for LZW flag
_MUSTCLEAR = 1
_FIRST = 2
_NORMAL = 3
_DEFERRED = 4
# maximum for LZW code size (bits)
_MAX_CSIZE = 12
# GIF disposal methods
_DISPOSALS = (
    "Unspecified",
    "No disposal",
    "Restore to background color",
    "Restore to previous")
# String for version algorythm
_LOG_STRING = """"Algorythm with output
LZWAlgorythm and fill_colors in C called from Python
                
"""
                
_debug, _log = False, False

def set_debug(debug=None, log=None):
    if debug is not None:
        _debug = debug
    if log is not None:
        _log = log


class GIFDecoderError(Exception):
    def __init__(self, message, image=None):
        if image:
            message = message + " decoding image " + str(image)
        super.__init__(message)
        

class GIFDecoder:
    """An object which splits an animated GIF file into its frames.
    You can split a GIF file with the decode() method, returning its
    frames as a list of pygame Surface objects. Then you can get them
    with the get_images() method or save them with the save_images()
    method.
    """
    
    def __init__(self):
        """The constructor.
        It tries to use the C dynamic library %GIFDecoder (.dll or .so)
        for high speed decoding of the GIF files. If it doesn't find it
        uses a slower Python routine."""
        libpath = os.path.split(os.path.realpath(__file__))[0]
        libpath = os.path.join(libpath, "GIFDecoder", "GIFDecoder.dll")
        try:
            self._lib = CDLL(libpath)
        except FileNotFoundError:
            self._lib = None
            print("WARNING: C Library not found. Using (slower) Python implementation")
        else:
            self._lib.LZWAlgorythm.argtypes = (c_uint, c_uint, c_char_p, c_uint, POINTER(c_uint16))
            self._lib.LZWAlgorythm.restype = c_uint
            self._lib.fill_colors.argtypes = (c_char_p, c_uint, POINTER(c_uint16), POINTER(c_ubyte))
            self._lib.fill_colors.restype = c_uint
        
        self.reset_all()
        
    def reset_all(self):
        """Reset the class to its initial state.
        This is done automatically by the decode() method before decoding
        a file, so usually the user doesn't need to use this.
        """
        self._buffer = bytearray()
        self._f = None
        self._screen_width = 0
        self._screen_height = 0
        self._has_global_table = False
        self._global_table_size = 0
        self._global_color_table = bytes()
        self._is_global_sorted = False
        self._color_depth = 0
        self._back_index = 0
        self._aspect_ratio = 0
        self._images = []
        self._reset_graphics()
        self._reset_image()
        
    def _reset_graphics(self):
        ## INTERNAL FUNCTION
        self._disposal_method = 0
        self._user_input = False
        self._has_transparent_color = False
        self._delay_time = 0
        self._transparent_index = 0          
        
    def _reset_image(self):
        ## INTERNAL FUNCTION
        self._image_left_pos = 0
        self._image_top_pos = 0
        self._image_width = 0
        self._image_height = 0
        self._has_local_table = False
        self._local_table_size = 0
        self._local_color_table = bytes()
        self._is_interlaced = False
        self._is_local_sorted = False
        self._lzw_code_size = 0
        
    def _read_header(self):
        """Read the  1st 9 bytes of the file, which contain
        the header and the screen descriptor.
        It throws a GIFDecoderError if it is not an appropriate
        GIF header."""
        self._buffer = self._f.read(6)
        if self._buffer not in (b"GIF87a", b"GIF89a"):
            raise GIFDecoderError("Not a .GIF file")
        self._screen_width = int.from_bytes(self._f.read(2), "little")
        self._screen_height = int.from_bytes(self._f.read(2), "little")
        self._buffer = self._f.read(1)
        self._has_global_table = bool(self._buffer[0] & 0x80)
        self._color_depth = (self._buffer[0] & 0x70) >> 4 + 1
        if self._has_global_table:
            self._is_global_sorted = bool(self._buffer[0] & 0x08)
            self._global_table_size = 2 ** ((self._buffer[0] & 0x07) + 1)
        self._buffer = self._f.read(2)
        self._back_index = self._buffer[0]
        self._aspect_ratio = self._buffer[1]
            
    def _read_blocks(self):
        """Read a series of data block putting their content into
        self._buffer.
        """
        self._buffer = bytearray()
        size = self._f.read(1)[0]
        while  size != _BLOCK_TERMINATOR:
            self._buffer += self._f.read(size)
            size = self._f.read(1)[0]
    
    def _print_image_attr(self):
        """Print the attributes of the image being decoded."""
        print("Image n.", len(self._images) + 1)
        print("Topleft {:5} x{:5}    Dims {:5} x{:5}".
              format(self._image_left_pos, self._image_top_pos, self._image_width, self._image_height))
        print("Disposal method:   ", _DISPOSALS[self._disposal_method])
        print("Interlaced:", self._is_interlaced, " Local table:", self._has_local_table,
              " Transparent color:", self._transparent_index if self._has_transparent_color else "None")
            
    def _LZWalgorythm(self, color_codes):
        """Implement the LZW algorythm to decodify an image data block.
        The object uses this method only when it can't find the C dynamic library
        GIFDecoder (.dll or .so).""" 
        CLEAR = 2 ** self._lzw_code_size
        EOI = CLEAR + 1
        lzw_table = [(i,) for i in range(2 ** self._lzw_code_size)]
        lzw_table.extend((CLEAR, EOI))
        csize = self._lzw_code_size + 1
        mask = 2 ** csize - 1
        flag = _MUSTCLEAR
        code = oldcode = None
        
        offset = 0
        ind = 0
        while ind < len(self._buffer):
            accumulator = int.from_bytes(self._buffer[ind:ind + 3], "little")
            accumulator >>= offset
            code = accumulator & mask
            offset += csize
            while offset >= 8:
                offset -= 8
                ind += 1
                
            if flag not in (_NORMAL, _DEFERRED):
                if flag == _MUSTCLEAR:
                    if code != CLEAR:
                        raise GIFDecoderError("Bad LZW code", image=len(self._images)+1)
                    flag = _FIRST
                elif flag == _FIRST:
                    if code < CLEAR:
                        color_codes.extend(lzw_table[code])
                    else:
                        raise GIFDecoderError("Bad LZW code", image=len(self._images)+1)
                    flag = _NORMAL
            elif code == EOI:
                break
            elif code == CLEAR:
                lzw_table = lzw_table[:2 ** self._lzw_code_size + 2]
                csize = self._lzw_code_size + 1
                mask = 2 ** csize - 1
                flag = _FIRST
                code = None         # sets oldcode in the last instruction
            else:
                if flag == _DEFERRED:
                    color_codes.extend(lzw_table[code]) 
                    continue
                elif code < len(lzw_table):
                    color_codes.extend(lzw_table[code])
                    s = lzw_table[oldcode] + (lzw_table[code][0],)
                else:
                    s = lzw_table[oldcode] + (lzw_table[oldcode][0],)
                    color_codes.extend(s)
                lzw_table.append(s)
                if len(lzw_table) == 2 ** csize:
                    if csize < _MAX_CSIZE:
                        csize += 1
                        mask = 2 ** csize - 1
                    else:
                        flag = _DEFERRED        
            oldcode = code
        
    
    def decode(self, fname):
        """Decode a GIF file and return its frames as a list of pygame Surface.
        You can get the list of images of the last decoded file also with the
        get_images() method.
        This can throw various GIFDecoderError if the decoding process fails for
        some cause.
        \param fname the name of the GIF file to be slicen 
        """
        if _log:
            self._log_start()
        if _debug:
            print ("Start decoding", fname)
        self._fname = fname
        self.reset_all()
        with open(fname, "r+b") as self._f:
            self._read_header()
            if self._has_global_table:
                self._global_color_table = bytes(self._f.read(3 * self._global_table_size))
            screen = pygame.Surface((self._screen_width, self._screen_height))
            self._buffer = self._f.read(1)
            while self._buffer[0] != _TRAILER:
                if self._buffer[0] == _EXTENSION_INTRODUCER:
                    self._buffer = self._f.read(1)
                    if self._buffer[0] == _GRAPHIC_CONTROL_EXTENSION:
                        if _debug:
                            print("Graphic control extension")
                        self._read_blocks()
                        self._disposal_method = (self._buffer[0] & 0x1C) >> 2
                        self._user_input = bool(self._buffer[0] & 0x02)
                        self._has_transparent_color = bool(self._buffer[0] & 0x01)
                        self._delay_time = int.from_bytes(self._buffer[1:3], "little")
                        self._transparent_index = self._buffer[3]    
                    elif self._buffer[0] == _COMMENT_EXTENSION:
                        self._read_blocks()
                        if _debug:
                            print("Comment extension")
                            print(self._buffer.decode("utf-8"))
                    elif self._buffer[0] == _PLAIN_TEXT_EXTENSION:
                        self._read_blocks()
                        if _debug:
                            print("Plain text extension")
                            print(self._buffer.decode("utf-8"))
                    elif self._buffer[0] == _APPLICATION_EXTENSION:
                        self._read_blocks()
                        if _debug:
                            print("Application extension")
                            print(self._buffer.decode("utf-8"))
                    else:
                        raise ValueError("Unknown extension")
                elif self._buffer[0] == _IMAGE_SEPARATOR:
                    if _debug:
                        print("Image n.", len(self._images) + 1)
                    self._reset_image()
                    self._image_left_pos = int.from_bytes(self._f.read(2), "little")
                    self._image_top_pos = int.from_bytes(self._f.read(2), "little")
                    self._image_width = int.from_bytes(self._f.read(2), "little")
                    self._image_height = int.from_bytes(self._f.read(2), "little")
                    self._buffer = self._f.read(1)
                    self._has_local_table = bool(self._buffer[0] & 0x80)
                    self._is_interlaced = bool(self._buffer[0] & 0x40)
                    if self._has_local_table:
                        self._is_local_sorted = bool(self._buffer[0] & 0x20)
                        self._local_table_size = 2 ** ((self._buffer[0] & 0x07) + 1)
                        self._local_color_table = bytes(self._f.read(3 * self._local_table_size))
                    self._lzw_code_size = self._f.read(1)[0]
                    self._read_blocks()
                    color_codes_len = self._image_width * self._image_height
                    # use the C dynamic library via ctypes
                    if self._lib:
                        color_codes = (c_uint16 * color_codes_len)()
                        if not self._lib.LZWAlgorythm(c_uint(self._lzw_code_size),
                                                      c_uint(len(self._buffer)),
                                                      c_char_p(bytes(self._buffer)),
                                                      c_uint(color_codes_len),
                                                      color_codes):
                            raise GIFDecoderError("LZW algorythm failed", image=len(self._images)+1)
                    # use the Python method
                    else:
                        try:
                            color_codes = []
                            self._LZWalgorythm(color_codes)
                        except GIFDecoderError:
                            raise GIFDecoderError("LZW algorythm failed", image=len(self._images)+1) 
                    if self._has_local_table:
                        color_table = self._local_color_table
                    elif self._has_global_table:
                        color_table = self._global_color_table
                    else:
                        raise GIFDecoderError("No color table", image=len(self._images)+1)
                    if self._lib:
                        array = (c_ubyte * (3 * color_codes_len))()
                        self._lib.fill_colors(color_table, c_uint(color_codes_len), color_codes, array)
                    else:
                        array = bytearray(3 * color_codes_len)
                        for i in range(color_codes_len):
                            array[3 * i : 3 * i + 3] = color_table[3 * color_codes[i] : 3 * color_codes[i] + 3]                    
                    surf = pygame.image.frombuffer(array, (self._image_width, self._image_height), "RGB")
                    if self._has_transparent_color:
                        surf.set_colorkey(color_table[3 * self._transparent_index:3 * self._transparent_index + 3])
                    if self._disposal_method == 1:
                        previous = surf.copy()
                    elif self._disposal_method == 2:
                        screen.fill(color_table[self._back_index])
                        previous = screen.copy()
                    elif self._disposal_method == 3:
                        screen.blit(previous, (0, 0))
                    screen.blit(surf, (self._image_left_pos, self._image_top_pos))          
                    self._images.append(screen.copy())
                    self._reset_graphics()
                                        
                self._buffer = self._f.read(1)
            if _debug:
                print("End of input stream")
            if _log:
                self._log_end()
        return self._images          
            
    def debug_blocks(self, fname):
        """Print a summary of the blocks included in a GIF file.
        For each one it prints the type of the block, its offset in bytes
        from the beginning of the file, its size and the size of the
        \param fname the name of the GIF file to process.
        """
        print("{:^30}{:>10}{:>10}{:>10}{:>10}".format("BLOCK TYPE", "OFFSET", "TOT SIZE", "BUF SIZE", "BLOCKS"))
        print("{:-<66}".format(""))
        with open(fname, "r+b") as self._f:
            self._buffer = self._f.read(6)
            btype, boffs, tsize, bsize, subbl = "HEADER", 0, 6, 6, 1 
            if self._buffer not in (b"GIF87a", b"GIF89a"):
                raise GIFDecoderError("Not a .GIF file")
            print("{:30}{:10}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize, subbl))
            
            btype, boffs, tsize, bsize, subbl = "LOGICAL SCREEN DESCRIPTOR", self._f.tell(), 7, 7, 1
            self._f.read(4)                                  # width and height
            self._buffer = self._f.read(1)
            has_table = bool(self._buffer[0] & 0x80)
            color_depth = (self._buffer[0] & 0x70) >> 4 + 1
            if has_table:
                table_size = 2 ** ((self._buffer[0] & 0x07) + 1)
            self._buffer = self._f.read(2)                    # background and axpect ratio
            print("{:30}{:10}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize, subbl))
            
            if has_table:
                btype, boffs, tsize = "GLOBAL COLOR TABLE", self._f.tell(), table_size * color_depth
                print("{:30}{:10}{:10}{:10}{:10}".format(btype, boffs, tsize, tsize, 1))
                self._f.read(tsize)            
            
            self._buffer = self._f.read(1)
            while self._buffer[0] != _TRAILER:
                if self._buffer[0] == _EXTENSION_INTRODUCER:
                    
                    self._buffer = self._f.read(1)
                    boffs = self._f.tell() - 2                       # for extension and type bytes
                    if self._buffer[0] == _GRAPHIC_CONTROL_EXTENSION:
                        btype = "GRAPHIC CONTROL EXTENSION"    
                    elif self._buffer[0] == _COMMENT_EXTENSION:
                        btype = "COMMENT EXTENSION"
                    elif self._buffer[0] == _PLAIN_TEXT_EXTENSION:
                        btype = "PLAIN TEXT EXTENSION"
                    elif self._buffer[0] == _APPLICATION_EXTENSION:
                        btype = "APPLICATION EXTENSION"
                    else:
                        raise GIFDecoderError("Unknown extension")
                    tsize, bsize, subbl = self._read_blocks_debug()
                    tsize += 2                                      # for block markers                       
                    print("{:30}{:10}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize, subbl))                    
                elif self._buffer[0] == _IMAGE_SEPARATOR:
                    btype, boffs, bsize, subbl = "IMAGE DESCRIPTOR", self._f.tell() - 1, 10, 1
                    self._f.read(8)                  # various image CONTROL
                    self._buffer = self._f.read(1)
                    has_table = bool(self._buffer[0] & 0x80)
                    print("{:30}{:10}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize, subbl))
                    if has_table:
                        table_size = 2 ** ((self._buffer[0] & 0x07) + 1)
                        boffs, btype, tsize, subbl = self._f.tell(), "LOCAL COLOR TABLE", table_size * color_depth, 1
                        print("{:30}{:10}{:10}{:10}{:10}".format(btype, boffs, tsize, tsize, subbl))
                        self._f.read(tsize)                    
                    
                    boffs, btype = self._f.tell(), "IMAGE DATA"
                    self._f.read(1)              # LZW code size
                    tsize, bsize, subbl = self._read_blocks_debug()
                    tsize += 1
                    print("{:30}{:10}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize, subbl))
                                        
                self._buffer = self._f.read(1)
            print("End of input stream")
            
                  
    def _read_blocks_debug(self):
        ## INTERNAL FUNCTION
        totsize, bufsize, blocks = 0, 0, []
        subsize = self._f.read(1)[0]
        while  subsize != _BLOCK_TERMINATOR:
            totsize += (subsize + 1)        # adds block size byte
            bufsize += subsize
            blocks.append(subsize)
            self._f.read(subsize)
            subsize = self._f.read(1)[0]
        totsize += 1                        # for terminator
        return totsize, bufsize, len(blocks)    
            
    def _log_start(self):
        ## INTERNAL FUNCTION
        self._logf = open("GIFDecoder.log", "a")
        self._init_time = time.time_ns()
        
    def _log_end(self):
        ## INTERNAL FUNCTION
        self._end_time = time.time_ns()
        if self._logf:
            time_diff = self._end_time - self._init_time
            self._logf.write("Date:    " + time.asctime() + "\n")
            self._logf.write("File:    " + self._fname + "\n")
            
            self._logf.write("Images:  " + str(len(self._images)) + "\n")
            self._logf.write("Time:    " + "{:.3f}".format(time_diff / 1000000000) + "\n")
            self._logf.write("Average: " + "{:.3f}".format(time_diff / (1000000000 * len(self._images))) + "\n")
            self._logf.write(_LOG_STRING)
            self._logf.close()
            
    
    def get_images(self):
        """Return the list of images of the last decoded GIF file."""
        return self._images
    
    def save_images(self, prefix=None, form="04d", ext=".png"):
        """Save the single frames of the last decoded GIF file into separate files.
        It appends to the file name a numeric suffix in order to get different names
        easy to load.
        \param prefix if you leave **None** the method uses the name of the GIF file
        as prefix, otherwise you can specify your own name.
        \param form a format for the numeric suffix: this is a format specifier of
        the string format() method (without trailing :). If you leave the default the
        files will be named "prefix0001", "prefix0002", "prefix0003" etc.
        \param ext you can choose ".png", ".jpg" or ".jpeg".
        """
        if (self._images):
            if not prefix:
                prefix = self._fname
            if ext not in (".png", ".jpg", "jpeg"):
                raise ValueError("Invalid extension") 
            s = prefix + "{:" + form + "}" + ext
            for i in range(len(self._images)):
                fname = s.format(i)
                with open(fname, "r+b") as f:
                    pygame.image.save_extended(self._images[i], f)
        else:
            raise ValueError("Empty image list")
        
        
# ######################################################################
# ###
# ###           S h e e t S l i c e r
# ###
# ######################################################################


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


# #####################################################################
# ###
# ###           v i e w l i s t
# ###
# ######################################################################        


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

# #####################################################################
# ###
# ###           E n d
# ###
# ######################################################################
                

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
