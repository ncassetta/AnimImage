#include <stdio.h>
#include <stdlib.h>
#include "myvector.h"
#include "GIFDecoder.h"

unsigned char* bytes = 0;
size_t tot_size;

FILE* fptr;

void read_blocks() {
    size_t new_size = 0;
    unsigned char size;

    if (bytes != 0) {
        free(bytes);
        bytes = 0;
    }
    tot_size = 0;

    fread(&size, 1, 1, fptr);
    while(size != 0) {
        new_size = tot_size + size;
        if (bytes == 0)
            bytes = (unsigned char *)malloc(new_size);
        else
            bytes = (unsigned char *)realloc(bytes, new_size);
        fread(bytes + tot_size, size, 1, fptr);
        tot_size = new_size;
        fread(&size, 1, 1, fptr);
    }
}

int main(int argc, char *argv[]) {
    fptr = fopen("C:\\Users\\ncass\\Python\\AnimImage\\se2017aug21t.gif", "rb");
    fseek(fptr, 205, SEEK_SET);
    read_blocks();
    struct myvector* lzw_codes_ptr = LZWAlgorythm(4, tot_size, bytes);
    print_codes_table(lzw_codes_ptr);
    return 0;
}

