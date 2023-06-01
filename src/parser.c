#include "parser.h"

#include <ctype.h>
#include <string.h>

#include "err.h"
#include "lexer.h"
#include "list.h"
#include "propformula.h"
#include "util.h"

/**
 * Assigns symbols to strings.
 *
 * Aborts the program with an error message if an invalid input is detected.
 *
 * @param str  a string to translate
 * @return     the resulting symbol
 */
FormulaKind toKind(const char* str) {
    if (str == NULL || *str == '\0') {
        err("Empty string detected");
    }

    if (strcmp(str, "!") == 0) {
        return NOT;
    } else if (strcmp(str, "&&") == 0) {
        return AND;
    } else if (strcmp(str, "||") == 0) {
        return OR;
    } else if (strcmp(str, "=>") == 0) {
        return IMPLIES;
    } else if (strcmp(str, "<=>") == 0) {
        return EQUIV;
    } else {
        for (int i = 0; i < strlen(str); i++) {
            if (!isalnum(*str))
                err("Not valid variable");  // Not alphanumeric char
        }
        return VAR;  // All characters are alphanumeric
    }
}

int checkstack(List* s) {
    if (s->head != NULL) {
        return 1;
    } else {
        return 0;
    }
}

PropFormula* parseFormula(FILE* input, VarTable* vt) {
    List ls = mkList();  // Creating an empty list
    /*
    if (input == NULL) {
        err("No tokens provided");
    }*/

    char* key;  // Initializing my key token

    while ((key = nextToken(input)) != NULL) {  // check if token not null
        if (key == NULL) {
            err("NO TOKEN PASSED");
        }

        FormulaKind kindForm = toKind(key);  // Sending kind variable to

        if (kindForm == VAR) {  // var case
            PropFormula* var = mkVarFormula(vt, key);
            push(&ls, var);

        } else if (kindForm == NOT) {  // not case//checkonce

            int check = checkstack(&ls);
            if (check == 1)

            {
                PropFormula* Op = peek(&ls);
                pop(&ls);
                PropFormula* uForm = mkUnaryFormula(kindForm, Op);
                push(&ls, uForm);
            } else {
                err("EmptyUnary");
            }

        } else if (kindForm == AND || kindForm == OR || kindForm == EQUIV ||
                   kindForm == IMPLIES) {
            PropFormula* Rightop = peek(&ls);

            int checkfirst = checkstack(&ls);

            if (checkfirst == 1) {
                pop(&ls);

                int checksecond = checkstack(&ls);

                if (checksecond == 1) {
                    PropFormula* Leftop = peek(&ls);
                    pop(&ls);
                    PropFormula* biForm =
                        mkBinaryFormula(kindForm, Leftop, Rightop);
                    push(&ls, biForm);
                } else {
                    err("Binary Problem");
                }
            }
        } else {
            err("Invalid token encountered");
        }
    }

    PropFormula* result = (PropFormula*)peek(&ls);
    pop(&ls);
    if (ls.head == NULL) {
        return result;
    } else {
        err("Stack is not empty there are variables, parsing fail");
    }
}
