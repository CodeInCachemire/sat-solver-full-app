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
    ListItem* current = s->head;  // assign head to current
    ListItem* next;               // initialize next

    while (current != NULL) {  // Top element is not null
        next = current->next;  // next has the next element
        free(current);         // free current element
        current = next;        // change current to next to move to next element
    }

    s->head = NULL;  // write null in the head
}

void push(List* s, void* data) {
    ListItem* newitem = malloc(sizeof(ListItem));  // allocation

    newitem->data = data;     // data we recieve to newitem data
    newitem->next = s->head;  // our current head gets shifted to next
    s->head = newitem;        // our head gets the new item
}

void* peek(List* s) {
    ListItem* current = s->head;
    if (s->head != NULL) {
        return current->data;  // retrieve data
    } else {
        return NULL;
    }
}

void pop(List* s) {
    if (s->head != NULL) {  // stack not empty
        ListItem* current = s->head;
        ListItem* next;

        next = current->next;  // current element assigned to head, thereby
                               // deletion of an element
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
