import time, os
import pygame
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

# times for time log
init_time = 0
end_time = 0


class GIFDecoder:
    """
    Object which splits an animated GIF file into its frames.
    """
    def __init__(self):
        """
    The constructor.
        """
        self.reset_all()
        
        libpath = os.path.join("GIFDecoder", "GIFDecoder.dll")
        self.lib = CDLL(libpath)
        self.lib.LZWAlgorythm.argtypes = (c_uint, c_uint, c_char_p, c_uint, POINTER(c_uint16))
        self.lib.LZWAlgorythm.restype = c_uint
        self.lib.fill_colors.argtypes = (c_char_p, c_uint, POINTER(c_uint16), POINTER(c_ubyte))
        self.lib.fill_colors.restype = c_uint
        print(self.lib.__dict__)
        
    def reset_all(self):
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
        self.reset_graphics()
        self.reset_image()
        
    def reset_graphics(self):
        self._disposal_method = 0
        self._user_input = False
        self._has_transparent_color = False
        self._delay_time = 0
        self._transparent_index = 0          
        
    def reset_image(self):          
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
        self._buffer = self._f.read(6)
        if self._buffer not in (b"GIF87a", b"GIF89a"):
            raise Exception("Not a .GIF file")
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
        self._buffer = bytearray()
        size = self._f.read(1)[0]
        while  size != _BLOCK_TERMINATOR:
            self._buffer += self._f.read(size)
            size = self._f.read(1)[0]
            
    def _read_blocks_debug(self):
        totsize, bufsize, blocks = 0, 0, []
        subsize = self._f.read(1)[0]
        while  subsize != _BLOCK_TERMINATOR:
            totsize += (subsize + 1)        # adds block size byte
            bufsize += subsize
            blocks.append(subsize)
            self._f.read(subsize)
            subsize = self._f.read(1)[0]
        totsize += 1                        # for terminator
        return totsize, bufsize, blocks
    
    def print_image_attr(self):
        print("Image n.", len(self._images) + 1)
        print("Topleft {:5} x{:5}    Dims {:5} x{:5}".
              format(self._image_left_pos, self._image_top_pos, self._image_width, self._image_height))
        print("Disposal method:   ", _DISPOSALS[self._disposal_method])
        print("Interlaced:", self._is_interlaced, " Local table:", self._has_local_table,
              " Transparent color:", self._transparent_index if self._has_transparent_color else "None")
            
    def _LZWalgorythm(self): 
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
                        raise Exception("Bad LZW code")
                    flag = _FIRST
                elif flag == _FIRST:
                    if code < CLEAR:
                        self._color_codes.extend(lzw_table[code])
                    else:
                        raise Exception("Bad LZW code")
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
                    self._color_codes.extend(lzw_table[code]) 
                    continue
                elif code < len(lzw_table):
                    self._color_codes.extend(lzw_table[code])
                    s = lzw_table[oldcode] + (lzw_table[code][0],)
                else:
                    s = lzw_table[oldcode] + (lzw_table[oldcode][0],)
                    self._color_codes.extend(s)
                lzw_table.append(s)
                if len(lzw_table) == 2 ** csize:
                    if csize < _MAX_CSIZE:
                        csize += 1
                        mask = 2 ** csize - 1
                    else:
                        flag = _DEFERRED        
            oldcode = code
        
            #for i in range(len(lzw_table)):
            #    print(i + 1, lzw_table[i])
        #for i in range(len(self._color_codes) // self._image_width + 1):
            #for j in range(self._image_width):
                #if self._image_width * i + j < len(self._color_codes):
                    #print(self._color_codes[self._image_width * i + j], end=' ')
            #print()
        #print()
        
    
    def decode(self, fname):
        self.log_start()
        self._fname = fname
        print ("Start decoding", fname)
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
                        print("Graphic control extension")
                        self._read_blocks()
                        self._disposal_method = (self._buffer[0] & 0x1C) >> 2
                        self._user_input = bool(self._buffer[0] & 0x02)
                        self._has_transparent_color = bool(self._buffer[0] & 0x01)
                        self._delay_time = int.from_bytes(self._buffer[1:3], "little")
                        self._transparent_index = self._buffer[3]    
                    elif self._buffer[0] == _COMMENT_EXTENSION:
                        print("Comment extension")
                        self._read_blocks()
                        print(self._buffer.decode("utf-8"))
                    elif self._buffer[0] == _PLAIN_TEXT_EXTENSION:
                        print("Plain text extension")
                        self._read_blocks()
                        print(self._buffer.decode("utf-8"))
                    elif self._buffer[0] == _APPLICATION_EXTENSION:
                        print("Application extension")
                        self._read_blocks()
                        print(self._buffer.decode("utf-8"))
                    else:
                        raise ValueError("Unknown extension")
                elif self._buffer[0] == _IMAGE_SEPARATOR:
                    print("Image n.", len(self._images) + 1)
                    self.reset_image()
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
                    #self.print_image_attr()
                    color_codes_len = self._image_width * self._image_height
                    color_codes = (c_uint16 * color_codes_len)()
                    if not self.lib.LZWAlgorythm(c_uint(self._lzw_code_size),
                                                 c_uint(len(self._buffer)),
                                                 c_char_p(bytes(self._buffer)),
                                                 c_uint(color_codes_len),
                                                 color_codes):
                        raise ValueError("LZW algorythm failed, file partially decoded!")
                    #try:
                        #self._LZWalgorythm()
                    #except:
                        #print("LZW algorythm failed, file partially decoded!")
                    if self._has_local_table:
                        color_table = self._local_color_table
                    elif self._has_global_table:
                        color_table = self._global_color_table
                    else:
                        raise ValueError("No color table")
                    array = (c_ubyte * (3 * color_codes_len))()
                    self.lib.fill_colors(color_table, c_uint(color_codes_len), color_codes, array)
                    #array = bytearray(3 * self._image_width * self._image_height)
                    #for i in range(color_codes_len)):
                        #array[3 * i : 3 * i + 3] = color_table[3 * color_codes[i] : 3 * color_codes[i] + 3]                    
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
                    self.reset_graphics()
                                        
                self._buffer = self._f.read(1)
            print("End of input stream")
            self.log_end()
        return self._images          
        
    
    #def decode(self, fname):                         OLD METHOD WITHOUT CTYPES
        #self.log_start()
        #self._fname = fname
        #print ("Start decoding", fname)
        #self.reset_all()
        #with open(fname, "r+b") as self._f:
            #self._read_header()
            #if self._has_global_table:
                #self._read_color_table(self._global_color_table)
            #screen = pygame.Surface((self._screen_width, self._screen_height))
            #self._buffer = self._f.read(1)
            #while self._buffer[0] != _TRAILER:
                #if self._buffer[0] == _EXTENSION_INTRODUCER:
                    #self._buffer = self._f.read(1)
                    #if self._buffer[0] == _GRAPHIC_CONTROL_EXTENSION:
                        ##print("Graphic control extension")
                        #self._read_blocks()
                        #self._disposal_method = (self._buffer[0] & 0x1C) >> 2
                        #self._user_input = bool(self._buffer[0] & 0x02)
                        #self._has_transparent_color = bool(self._buffer[0] & 0x01)
                        #self._delay_time = int.from_bytes(self._buffer[1:3], "little")
                        #self._transparent_index = self._buffer[3]    
                    #elif self._buffer[0] == _COMMENT_EXTENSION:
                        ##print("Comment extension")
                        #self._read_blocks()
                        ##print(self._buffer.decode("utf-8"))
                    #elif self._buffer[0] == _PLAIN_TEXT_EXTENSION:
                        ##print("Plain text extension")
                        #self._read_blocks()
                        ##print(self._buffer.decode("utf-8"))
                    #elif self._buffer[0] == _APPLICATION_EXTENSION:
                        ##print("Application extension")
                        #self._read_blocks()
                        ##print(self._buffer.decode("utf-8"))
                    #else:
                        #raise("Unknown extension")
                #elif self._buffer[0] == _IMAGE_SEPARATOR:
                    ##print("Image n.", len(self._images) + 1)
                    #self.reset_image()
                    #self._image_left_pos = int.from_bytes(self._f.read(2), "little")
                    #self._image_top_pos = int.from_bytes(self._f.read(2), "little")
                    #self._image_width = int.from_bytes(self._f.read(2), "little")
                    #self._image_height = int.from_bytes(self._f.read(2), "little")
                    #self._buffer = self._f.read(1)
                    #self._has_local_table = bool(self._buffer[0] & 0x80)
                    #self._is_interlaced = bool(self._buffer[0] & 0x40)
                    #if self._has_local_table:
                        #self._is_local_sorted = bool(self._buffer[0] & 0x20)
                        #self._table_size = 2 ** ((self._buffer[0] & 0x07) + 1)
                        #self._read_color_table(self._local_color_table)
                    #self._lzw_code_size = self._f.read(1)[0]
                    #self._read_blocks()
                    ##self.print_image_attr()
                    #try:
                        #self._LZWalgorythm()
                    #except:
                        #print("LZW algorythm failed, file partially decoded!")
                    ##print("color codes _buffer length: {:} (teoric: {:}".format(
                    ##      len(self._color_codes), self._image_width * self._image_height))
                    #if self._has_local_table:
                        #color_table = self._local_color_table
                    #elif self._has_global_table:
                        #color_table = self._global_color_table
                    #else:
                        #raise Exception("No color table")
                    #array = bytearray(3 * self._image_width * self._image_height)
                    #for i in range(len(self._color_codes)):
                        #for j in range(3):
                            #array[3 * i + j] = color_table[self._color_codes[i]][j]
                    #surf = pygame.image.frombuffer(array.copy(), (self._image_width, self._image_height), "RGB")
                    #if self._has_transparent_color:
                        #surf.set_colorkey(color_table[self._transparent_index])
                    #if self._disposal_method == 1:
                        #previous = surf.copy
                    #elif self._disposal_method == 2:
                        #screen.fill(color_table[self._back_index])
                        #previous = screen.copy()
                    #elif self._disposal_method == 3:
                        #screen.blit(previous, (0, 0))
                    #screen.blit(surf, (self._image_left_pos, self._image_top_pos))          
                    #self._images.append(screen.copy())
                    #self.reset_graphics()
                                        
                #self._buffer = self._f.read(1)
            #print("End of input stream")
            #self.log_end()
        #return self._images
            
    def debug_blocks(self, fname):
        print("{:^30}{:>10}{:>10}{:>10}".format("BLOCK TYPE", "OFFSET", "TOT SIZE", "BUF SIZE"))
        print("{:-<66}".format(""))
        with open(fname, "r+b") as self._f:
            self._buffer = self._f.read(6)
            btype, boffs, tsize, bsize = "HEADER", 0, 6, 6 
            if self._buffer not in (b"GIF87a", b"GIF89a"):
                raise("Not a .GIF file")
            print("{:30}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize))
            
            btype, boffs, tsize, bsize = "LOGICAL SCREEN DESCRIPTOR", self._f.tell(), 7, 7
            self._f.read(4)                                  # width and height
            self._buffer = self._f.read(1)
            has_table = bool(self._buffer[0] & 0x80)
            color_depth = (self._buffer[0] & 0x70) >> 4 + 1
            if has_table:
                table_size = 2 ** ((self._buffer[0] & 0x07) + 1)
            self._buffer = self._f.read(2)                    # background and axpect ratio
            print("{:30}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize))
            
            if has_table:
                btype, boffs, tsize = "GLOBAL COLOR TABLE", self._f.tell(), table_size * color_depth
                print("{:30}{:10}{:10}{:10}".format(btype, boffs, tsize, tsize))
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
                        raise("Unknown extension")
                    tsize, bsize, subblocks = self._read_blocks_debug()
                    tsize += 2                                      # for block markers                       
                    print("{:30}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize))                    
                elif self._buffer[0] == _IMAGE_SEPARATOR:
                    btype, boffs, bsize = "IMAGE DESCRIPTOR", self._f.tell() - 1, 10
                    self._f.read(8)                  # various image CONTROL
                    self._buffer = self._f.read(1)
                    has_table = bool(self._buffer[0] & 0x80)
                    print("{:30}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize))
                    if has_table:
                        table_size = 2 ** ((self._buffer[0] & 0x07) + 1)
                        boffs, btype, tsize = self._f.tell(), "LOCAL COLOR TABLE", table_size * color_depth
                        print("{:30}{:10}{:10}{:10}".format(btype, boffs, tsize, tsize))
                        self._f.read(tsize)                    
                    
                    boffs, btype = self._f.tell(), "IMAGE DATA"
                    self._f.read(1)              # LZW code size
                    tsize, bsize, subblocks = self._read_blocks_debug()
                    tsize += 1
                    print("{:30}{:10}{:10}{:10}".format(btype, boffs, tsize, bsize))
                                        
                self._buffer = self._f.read(1)
            print("End of input stream")
            
    def log_start(self):
        self.logf = open("GIFDecoder.log", "a")
        self.init_time = time.time_ns()
        
    def log_end(self):
        self.end_time = time.time_ns()
        if self.logf:
            time_diff = self.end_time - self.init_time
            self.logf.write("Date:    " + time.asctime() + "\n")
            self.logf.write("File:    " + self._fname + "\n")
            
            self.logf.write("Images:  " + str(len(self._images)) + "\n")
            self.logf.write("Time:    " + "{:.3f}".format(time_diff / 1000000000) + "\n")
            self.logf.write("Average: " + "{:.3f}".format(time_diff / (1000000000 * len(self._images))) + "\n")
            self.logf.write(_LOG_STRING)
            self.logf.close()
            
    
    def get_images(self):
        return self._images
    
    def save_images(self, prefix=None, ext=".png", form="04d"):
        if (self._images):
            if not prefix:
                prefix = self._fname
            s = prefix + "{:" + form + "}" + ext
            for i in range(len(self._images)):
                fname = s.format(i)
                with open(fname, "r+b") as f:
                    save(self._images[i], f)
        else:
            raise("Empty image list")
        

    
        
    
    
from slicesheet import viewlist

dec = GIFDecoder()
fname = input("GIF file name: ")
dec.decode(fname)
pygame.init()

viewlist(dec.get_images(), 200)

##img = dec.images[0].copy()
##screen = pygame.display.set_mode((4 * (dec.screen_width + 10) + 10, (len(dec.images) // 4 + 1) * (dec.screen_height + 10) + 10))
##screen.fill("white")
##for i in range(len(dec.images)):
    ###x, y = i // 4, i % 4
    ###screen.blit(dec.images[i], (10 + x * (dec.screen_width + 10), 10 + y * (dec.screen_height + 10)))
    ##screen.fill("white")
    ##screen.blit(dec.images[i], (100, 100))
    ##pygame.display.flip()
    ##pygame.time.wait(50)
#print("Quitting pygame")
#pygame.quit()


#dec = GIFDecoder()
#fname = input("GIF file name: ")
#dec.debug_blocks(fname)
