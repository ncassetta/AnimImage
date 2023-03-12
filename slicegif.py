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
        libpath = os.path.join(libpath, "GIFDecoder", "GIFDeco.dll")
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
        

    
        
    
if __name__ == "__main__": 
    from slicesheet import viewlist
    
    dec = GIFDecoder()
    fname = input("GIF file name: ")
    dec.decode(fname)
    pygame.init()
    
    viewlist(dec.get_images(), 200)
    
    #dec = GIFDecoder()
    #fname = input("GIF file name: ")
    #dec.debug_blocks(fname)
