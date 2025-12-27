#include "dpll.h"

#include "cnf.h"
#include "err.h"
#include "list.h"
#include "util.h"
#include "variables.h"

typedef enum Reason { CHOSEN, IMPLIED } Reason;

/**
 * Struct to represent an entry in the assignment stack. Should only be created
 * and freed by pushAssignment and popAssignment.
 */
typedef struct Assignment {
    VarIndex var;
    Reason reason;
} Assignment;

/**
 * Adds a new assignment to the assignment stack.
 *
 * @param stack  an assignment stack
 * @param var    the variable to assign
 * @param r      the reason for the assignment
 */
void pushAssignment(List* stack, VarIndex var, Reason r) {
    Assignment* a = (Assignment*)malloc(sizeof(Assignment));
    a->var = var;
    a->reason = r;
    push(stack, a);
}

/**
 * Removes the head element of an assignment stack and frees it.
 *
 * @param stack  an assignment stack
 */
void popAssignment(List* stack) {
    Assignment* a = (Assignment*)peek(stack);
    free(a);
    pop(stack);
}

/**
 * Führt eine Iteration des DPLL Algorithmus aus.
 *
 * @param vt       die zugrunde liegende Variablentabelle
 * @param stack    der Zuweisungsstack
 * @param cnf      die zu prüfende Formel
 * @return         1 falls der Algorithmus mit SAT terminieren sollte,
 *                 0 falls der Algorithmus weiterlaufen sollte,
 *                 -1 falls der Algorithmus mit UNSAT terminieren sollte
 */
/**
 * Performs one iteration of the DPLL algorithm.
 *
 * @param vt       the underlying variable table
 * @param stack    an assignment stack
 * @param cnf      the formula to check
 * @return         1 if the algorithm should terminate with SAT,
 *                 0 if the algorithm should continue,
 *                -1 if the algorithm should terminate with UNSAT
 */

void Backtrack(List* s, VarTable* vt) {
    while (!isEmpty(s)) {
        Assignment* topE = peek(s);
        switch (topE->reason) {
            case CHOSEN:  // CHOSEN CASE
            {             // to false, then the reason to false
                updateVariableValue(vt, topE->var,
                                    FALSE);  // update variable ->true
                topE->reason = IMPLIED;
                popAssignment(s);
                return;
            }
            case IMPLIED:  // IMPLIED CASE
            {
                //updateVariableValue(vt, topE->var, UNDEFINED);  // false
                //  variable update
                popAssignment(s);
                break;
            }
            default:
                err("Something is definitely wrong");  // case where reason is
                                                       // not IMPLIED/CHOSEN,
                                                       // prolly won't execute
                                                       // but default needed
                break;
        }
    }
}

int iterate(VarTable* vt, List* stack, CNF* cnf) {
    switch (evalCNF(cnf)) {
        case TRUE: {
            return 1;
            break;
        }
        case FALSE: {
            Assignment* topestack = peek(stack);
            //  if reset is possible
            if (!isEmpty(stack) /*&& topestack == CHOSEN*/) {
                // IF RESET IS POSSIBLE
                Backtrack(stack, vt);  // backtrack
                return 0;              // new iteration

            } else {
                return -1;  // UNSAT
            }
            break;
        }
        case UNDEFINED: {
            // following code sort of sturcture comes from list.h, it was
            // commented is being used here
            ListIterator it = mkIterator(&cnf->clauses);
            int flag = 0;
            while (isValid(&it)) {
                Clause* current = (Clause*)getCurr(&it);
                Literal u_lit;
                //= getUnitLiteral(vt, current);  // the unit gets lit ;)
                if ((u_lit = getUnitLiteral(vt, current)) != 0) {
                    // function
                    // unit literal checked for sign, that +ve or -ve
                    TruthValue u_litval;
                    if (u_lit > 0) {
                        u_litval = TRUE;  // positive
                    } else {
                        u_litval = FALSE;  //-ve unit literal
                    }

                    // Variable Table is updated, absolute val is
                    // used since we want just the absolute value and not
                    // the sign
                    updateVariableValue(vt, abs(u_lit), u_litval);

                    // an entry in the assignment stack, we pushing the
                    // reason and the truthvalue
                    pushAssignment(stack, abs(u_lit), IMPLIED);  //

                    flag++;
                }
                next(&it);
            }

            if (flag <= 0)  // absencde of unit clause
            {
                VarIndex unkown_variable = getNextUndefinedVariable(vt);

                if (unkown_variable != 0) {
                    updateVariableValue(vt, unkown_variable, TRUE);

                    pushAssignment(stack, unkown_variable, CHOSEN);

                    int continue_iterating = iterate(vt, stack, cnf);

                    if (continue_iterating == 1) {
                        return 1;
                    }
                }
            }
            break;
        }

        default: {
            err("Default case, lololololololololol won't be exceuted or "
                "maybe "
                "will this is just default"
                "hahahahha");
            break;
        }
    }

    return 0;
}

char isSatisfiable(VarTable* vt, CNF* cnf) {
    List stack = mkList();

    int res;
    do {
        res = iterate(vt, &stack, cnf);
    } while (res == 0);

    while (!isEmpty(&stack)) {
        popAssignment(&stack);
    }

    return (res < 0) ? 0 : 1;
}
