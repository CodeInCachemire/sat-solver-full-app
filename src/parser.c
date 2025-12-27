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
        for (long unsigned int i = 0; i < strlen(str); i++) {
            if (!isalnum(str[i]))
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

    char* key;  // Initializing my key token
    int tokenCount = 0;

    while ((key = nextToken(input)) != NULL) {  // check if token not null

        tokenCount++;
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
                free(key);
                err("Empty Unary Formula");
            }

        } else if (kindForm == AND || kindForm == OR || kindForm == EQUIV ||
                   kindForm == IMPLIES) {  // double stack check has to be use
                                           // for two operands
            PropFormula* Rightop = peek(&ls);  // get values

            int checkfirst =
                checkstack(&ls);  // checkingg if there exists a first operand

            if (checkfirst == 1) {  // operand exists
                pop(&ls);           // pop operand

                int checksecond = checkstack(&ls);  // check for second operand

                if (checksecond == 1) {               // check
                    PropFormula* Leftop = peek(&ls);  // peek to get values
                    pop(&ls);  // pop it to make spac ein stack
                    PropFormula* biForm =
                        mkBinaryFormula(kindForm, Leftop, Rightop);
                    push(&ls, biForm);
                } else {
                    free(key);
                    err("Binary Problems");
                }
            }
        } else {
            free(key);
            err("Invalid token encountered");
        }
        free(key);
    }

    if (tokenCount ==
        0) {  // stack check to see if the while loop is entered, if count is> 0
              // means tokens were valid and not empty
        err("No tokens passed");
    }

    PropFormula* result = (PropFormula*)peek(&ls);  // give the formula to
                                                    // result
    pop(&ls);
    if (ls.head ==
        NULL) {  // check stack if empty, for exmple a b && c, stack would have
                 // two elements and c would remain after pop
        return result;
    } else {
        err("Stack is not empty there are variables, parsing fail");  // errror
                                                                      // case
                                                                      // where
                                                                      // stack
                                                                      // isn't
                                                                      // empyt
        return NULL;
    }
}
