#include <stdlib.h>
#include <inttypes.h>
#include <string.h>
#include <stdio.h>
#include "myvector.h"
#include "GIFDecoder.h"

#define MAX_CSIZE 12

enum t_status {
    MUSTCLEAR,
    FIRST,
    NORMAL,
    DEFERRED
};


struct myvector myv_null = {.ptr = 0, .element_size = 0, .elements = 0, .alloc_elements = 0};

void print_lzw_table(struct myvector *v) {
    unsigned int i;
    struct myvector* struct_ptr;

    printf("\nLZW Table Elements: %u\n", v->elements);
    struct_ptr = (struct myvector *)v->ptr;
    for (i = 0; i < v->elements; i++) {
        printf("%4d:  ", i);
        print_uint16_string((struct myvector *)(struct_ptr + i));
        printf("\n");
    }
}

void print_codes_table(struct myvector *v) {
    printf("\nColor codes Elements: %u\n", v->elements);
    print_uint16_string(v);
    printf("\n");
}

void print_uint16_string(struct myvector *v){
    unsigned int i;
    for (i = 0; i < v->elements; i++)
        printf (" %u", ((uint16_t *)v->ptr)[i]);
}

void* LZWAlgorythm(unsigned int lzw_code_size, unsigned int len, unsigned char* bytes) {
    uint16_t CLEAR = 1 << lzw_code_size;
    uint16_t EOI = CLEAR + 1;
    uint16_t csize = lzw_code_size + 1;
    uint16_t mask = (1 << csize) - 1;
    struct myvector lzw_table, lzw_codes, s, *lzw_table_ptr;
    uint16_t *el_ptr;
    enum t_status flag = MUSTCLEAR;
    uint16_t code, oldcode;

    printf("Arguments:\nlzw_code_size %d\nlen %d\nbytes %p\n", lzw_code_size,
           len, bytes);

    lzw_table_ptr = (struct myvector *)myv_init(&lzw_table, sizeof(struct myvector), (1 << lzw_code_size) + 2, false);
    for (unsigned int i = 0; i <= EOI; i++) {
        el_ptr = (uint16_t *)myv_init(lzw_table_ptr + i, 2, 1, true);
        *el_ptr = i;
    }
    myv_init(&lzw_codes, 2, 0, false);
    myv_init(&s, 2, 0, false);



    unsigned int offset = 0;
    unsigned int ind = 0;
    uint32_t accumulator = 0;

    while (ind <= len) {
/*        print_lzw_table(&lzw_table);
        print_codes_table(&lzw_codes);
        printf("%s", "s =");
        print_uint16_string(&s);
        printf("%s", "\n");         */
        memcpy (&accumulator, bytes + ind, 3);
        accumulator >>= offset;
        code = accumulator & mask;
        offset += csize;
        while (offset >= 8) {
            offset -= 8;
            ind++;
        }
        if (flag != NORMAL && flag != DEFERRED) {
            if (flag == MUSTCLEAR) {
                if (code != CLEAR) {
                    printf("%s", "Bad LZW code");
                    return 0;
                }
                flag = FIRST;
            }
            else if (flag == FIRST) {
                if (code < CLEAR)
                    myv_append(&lzw_codes, 1, &code);
                else {
                    printf("%s", "Bad LZW code");
                    return 0;
                }
                flag = NORMAL;
            }
        }
        else if (code == EOI)
            break;
        else if (code == CLEAR) {
            lzw_table.elements = (1 << lzw_code_size) + 2;
            csize = lzw_code_size + 1;
            mask = (1 << csize) - 1;
            flag = FIRST;
        }
        else {
            if (flag == DEFERRED)
                myv_append(&lzw_codes, lzw_table_ptr[code].elements, lzw_table_ptr[code].ptr);
            else if (code < lzw_table.elements) {
                myv_append(&lzw_codes, lzw_table_ptr[code].elements, lzw_table_ptr[code].ptr);
                myv_copy(&s, lzw_table_ptr + oldcode);
                myv_append(&s, 1, (uint16_t *)lzw_table_ptr[code].ptr);
            }
            else {
                myv_copy(&s, lzw_table_ptr + oldcode);
                myv_append(&s, 1, (uint16_t *)lzw_table_ptr[oldcode].ptr);
                myv_append(&lzw_codes, s.elements, s.ptr);
            }
            lzw_table_ptr = (struct myvector *)myv_append(&lzw_table, 1, &myv_null);
            myv_init(lzw_table_ptr + lzw_table.elements - 1, 2, s.elements, true);
            myv_copy(lzw_table_ptr + lzw_table.elements - 1, &s);
            if (lzw_table.elements == 1 << csize) {
                if (csize < MAX_CSIZE) {
                    csize += 1;
                    mask = (1 << csize) - 1;
                }
                else
                    flag = DEFERRED;
            }
        }
        oldcode = code;

    }
    myv_free(&s);
    for (unsigned int i = 0; i < lzw_table.elements; i++)
        myv_free(lzw_table_ptr + i);
    myv_free(&lzw_table);
    return &lzw_codes;
}

