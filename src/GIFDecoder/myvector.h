#ifndef MYVECTOR_H_INCLUDED
#define MYVECTOR_H_INCLUDED

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>

#define MIN_ALLOC 10

struct myvector {
    void* ptr;
    size_t element_size;
    unsigned int elements;
    size_t alloc_elements;
};

void* myv_init(struct myvector* v, size_t el_sz, unsigned int el, bool fixed);
void  myv_free(struct myvector* v);
void  myv_clear(struct myvector* v);
void* myv_realloc(struct myvector* v, unsigned int alloc_el);
void* myv_append(struct myvector* v, unsigned int new_el, void* pt);
void* myv_copy(struct myvector* v_to, struct myvector* v_from);
void  myv_print(struct myvector* v);



#endif // MYVECTOR_H_INCLUDED
