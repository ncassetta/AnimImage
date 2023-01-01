#include <stdlib.h>

enum t_status {
    MUSTCLEAR,
    FIRST,
    NORMAL,
    DEFERRED
};

struct array {
    void* pt = 0;
    unsigned long tot_size = 0;
    unsigned int num = 0;
};

void* array_alloc(struct array, a, unsigned int size, unsigned int num)  {
    a.tot_size = size * num;
    a.num = num;
    a.pt = malloc(a.tot_size);
    return a.pt;
}

void* array_extend(struct array a, unsigned int add_size) {
    a.tot_size += add_size * num;
}




void* LZWAlgorythm(unsigned int lzw_code_size, unsigned int len, char* bytes) {
    char CLEAR = 1 << lzw_code_size;
    char EOI = CLEAR + 1;
    unsigned int csize = lzw_code_size + 1;
    unsigned int mask = (1 << csize) - 1;
    lzw_table = malloc(sizeof(int*) * (1 << csize));
    t_status flag = MUSTCLEAR;
    unsigned int code, oldcode;

    unsigned int offset = 0;
    unsigned int ind = 0;
    char accumulator[3];

    while (ind <= len) {
        memcopy (accumulator, bytes[ind], 3);
        accumulator <<= offset;
        code = accumulator & mask;
        offset += csize;
        while (offset >= 8) {
            offset -= 8;
            ind++;
        }
        if (flag != NORMAL && flag != DEFERRED) {
            if (flag == MUSTCLEAR) {
                if (code != CLEAR) {
                    printf("%s", "Bad LZW code")
                    return 0;
                }
                flag = FIRST;
            }
            else if (flag = FIRST) {
                if (code < CLEAR)

            }
        }

    }


}
