#include "list.h"

#include <assert.h>
#include <stdlib.h>

#include "err.h"
#include "util.h"

/**
 * Struct for encapsulating a single list element.
 */
typedef struct ListItem {
    struct ListItem* next;  // pointer to the next element (NULL if last)
    void* data;             // pointer to the data
} ListItem;

List mkList(void) {
    List res;
    res.head = NULL;
    return res;
}

void clearList(List* s) {
    // TODO Implement me!
    NOT_IMPLEMENTED;
    UNUSED(s);
}

void push(List* s, void* data) {
    // TODO Implement me!
    NOT_IMPLEMENTED;
    UNUSED(s);
    UNUSED(data);
}

void* peek(List* s) {
    // TODO Implement me!
    NOT_IMPLEMENTED;
    UNUSED(s);
}

void pop(List* s) {
    // TODO Implement me!
    NOT_IMPLEMENTED;
    UNUSED(s);
}

char isEmpty(List* s) {
    // TODO Implement me!
    NOT_IMPLEMENTED;
    UNUSED(s);
}

ListIterator mkIterator(List* list) {
    ListIterator res;
    res.list = list;
    res.prev = NULL;
    res.current = list->head;

    return res;
}

void* getCurr(ListIterator* it) {
    assert(it->current != NULL);
    return it->current->data;
}

void next(ListIterator* it) {
    assert(isValid(it));
    it->prev = it->current;
    it->current = it->current->next;
}

char isValid(ListIterator* it) { return it->current != NULL; }
