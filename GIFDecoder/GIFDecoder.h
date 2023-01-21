#include <stdlib.h>
#include <inttypes.h>
#include <string.h>
#include <stdio.h>

void print_lzw_table(struct myvector *table);
void print_codes_table(struct myvector *table);
void print_uint16_string(struct myvector *table);

unsigned int LZWAlgorythm(unsigned int lzw_code_size, unsigned int len, unsigned char* bytes, unsigned int codes_len, uint16_t* lzw_codes_ptr);
unsigned int fill_colors(unsigned char* color_table, unsigned int color_codes_size, uint16_t* color_codes, unsigned char* colors);
