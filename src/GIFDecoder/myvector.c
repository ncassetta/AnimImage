#include "myvector.h"

void* myv_init(struct myvector* v, size_t el_sz, unsigned int el, bool fixed) {
    unsigned int alloc_el = fixed ? el : (el <= MIN_ALLOC ? MIN_ALLOC : el);
    v->ptr = calloc(alloc_el, el_sz);
    v->element_size = (v->ptr ? el_sz : 0);
    v->elements = (v->ptr ? el : 0);
    v->alloc_elements = (v->ptr ? alloc_el : 0);
    return v->ptr;
}

void myv_free(struct myvector* v) {
    if (v->ptr) {
        free(v->ptr);
        v->ptr = 0;
    }
}

void myv_clear(struct myvector* v) {
    v->elements = 0;
}

void* myv_realloc(struct myvector* v, unsigned int alloc_el) {
    if (v->ptr) {
        v->ptr = realloc(v->ptr, alloc_el * v->element_size);
        if (v->ptr) {
            v->alloc_elements = alloc_el;
            v->elements = (alloc_el < v->elements ? alloc_el : v->elements);
        }
        else {
            v->alloc_elements = 0;
            v->elements = 0;
        }
    }
    return v->ptr;
}

void* myv_append(struct myvector* v, unsigned int new_el, void* pt) {
    unsigned int alloc_el = 0;
    if (v->ptr) {
        if (v->elements + new_el > v->alloc_elements) {
            alloc_el = (new_el < v->elements ? v->elements : new_el);
            v->ptr = realloc(v->ptr, (v->alloc_elements + alloc_el) * v->element_size);
        }
        if (v->ptr) {
            memcpy(v->ptr + v->elements * v->element_size, pt, new_el * v->element_size);
            v->alloc_elements += alloc_el;
            v->elements += new_el;
        }
        else {
            v->alloc_elements = 0;
            v->elements = 0;
        }
    }
    return v->ptr;
}

void* myv_copy(struct myvector* v_to, struct myvector* v_from) {
    if (v_to && v_from) {
        v_to->elements = 0;
        if (v_from->elements != 0)
            myv_append(v_to, v_from->elements, v_from->ptr);
    }
    return v_to->ptr;
}

void myv_print(struct myvector* v) {
    printf ("Struct myvector:\n");
    printf ("    element_size:   %zu\n", v->element_size);
    printf ("    elements:       %u\n", v->elements);
    printf ("    alloc_elements: %zu\n", v->alloc_elements);
}
