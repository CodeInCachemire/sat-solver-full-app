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
    ListItem* current = s->head;
    ListItem* next;

    while (current != NULL) {
        next = current->next;
        free(current);
        current = next;
    }

    s->head = NULL;
}

void push(List* s, void* data) {
    ListItem* newitem = malloc(sizeof(ListItem));

    newitem->data = data;
    newitem->next = s->head;
    s->head = newitem;
}

void* peek(List* s) {
    ListItem* current = s->head;
    if (s->head != NULL) {
        return current->data;
    } else {
        return NULL;
    }
}

void pop(List* s) {
    if (s->head != NULL) {
        ListItem* current = s->head;
        ListItem* next;

        next = current->next;
        s->head = next;
        free(current);
    }
}

char isEmpty(List* s) { return s->head == NULL; }

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
