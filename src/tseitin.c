#include "tseitin.h"

#include <stdio.h>

#include "err.h"
#include "propformula.h"
#include "util.h"
#include "variables.h"

/**
 * Inserts a clause with one literal into the CNF.
 *
 * @param vt   the underlying variable table
 * @param cnf  a formula
 * @param a    a literal
 */
void addUnaryClause(VarTable* vt, CNF* cnf, Literal a) {
    Clause* clause = mkTernaryClause(vt, a, 0, 0);
    addClauseToCNF(cnf, clause);
}

/**
 * Inserts a clause with two literals into the CNF.
 *
 * @param vt   the underlying variable table
 * @param cnf  a formula
 * @param a    the first literal
 * @param b    the second literal
 */
void addBinaryClause(VarTable* vt, CNF* cnf, Literal a, Literal b) {
    Clause* clause = mkTernaryClause(vt, a, b, 0);
    addClauseToCNF(cnf, clause);
}

/**
 * Inserts a clause with three literals into the CNF.
 *
 * @param vt   the underlying variable table
 * @param cnf  a formula
 * @param a    the first literal
 * @param b    the second literal
 * @param c    the third literal
 */
void addTernaryClause(VarTable* vt, CNF* cnf, Literal a, Literal b, Literal c) {
    Clause* clause = mkTernaryClause(vt, a, b, c);
    addClauseToCNF(cnf, clause);
}

/**
 * Adds clauses for a propositional formula to a CNF.
 *
 * For a propositional formula pf, clauses that are added that are equivalent to
 *
 *     x <=> pf
 *
 * where x is usually a fresh variable. This variable is also returned.
 *
 * @param vt   the underlying variable table
 * @param cnf  a formula
 * @param pf   a propositional formula
 * @return     the variable x, as described above
 */
VarIndex addClauses(VarTable* vt, CNF* cnf, const PropFormula* pf) {
    switch (pf->kind) {
        case VAR: {
            return pf->data.var;
        }  // following the examples of formula given in the pdf
        case AND: {
            VarIndex c = addClauses(vt, cnf, pf->data.operands[0]);
            VarIndex d = addClauses(vt, cnf, pf->data.operands[1]);
            VarIndex x = mkFreshVariable(vt);      // fresh variable
            addBinaryClause(vt, cnf, -x, c);       // binary first
            addBinaryClause(vt, cnf, -x, d);       // binary clause again
            addTernaryClause(vt, cnf, -c, -d, x);  // Third is ternary
            return x;
        }
        case OR: {
            VarIndex c = addClauses(vt, cnf, pf->data.operands[0]);
            VarIndex d = addClauses(vt, cnf, pf->data.operands[1]);
            VarIndex x = mkFreshVariable(vt);     // Fresh Variable
            addTernaryClause(vt, cnf, -x, c, d);  // first Ternary in Formula
            addBinaryClause(vt, cnf, -c, x);      // Second Binary
            addBinaryClause(vt, cnf, -d, x);      // Third Binary
            return x;
        }
        case IMPLIES: {
            VarIndex c = addClauses(vt, cnf, pf->data.operands[0]);
            VarIndex d = addClauses(vt, cnf, pf->data.operands[1]);
            VarIndex x = mkFreshVariable(vt);
            addTernaryClause(vt, cnf, -x, -c, d);  // First Ternary
            addBinaryClause(vt, cnf, c, x);        // Secojd Binary
            addBinaryClause(vt, cnf, -d, x);       // Third Binary
            return x;
        }
        case EQUIV: {
            VarIndex a = addClauses(vt, cnf, pf->data.operands[0]);
            VarIndex b = addClauses(vt, cnf, pf->data.operands[1]);
            VarIndex x = mkFreshVariable(vt);
            addTernaryClause(vt, cnf, -x, -a, b);  // Ternary First
            addTernaryClause(vt, cnf, -x, -b, a);  // Ternary Second
            addTernaryClause(vt, cnf, x, -a, -b);  // Ternary Third
            addTernaryClause(vt, cnf, x, a, b);    // Ternary Fourth
            return x;
        }
        case NOT: {
            VarIndex a = addClauses(vt, cnf, pf->data.single_op);
            VarIndex x = mkFreshVariable(vt);
            addBinaryClause(vt, cnf, -x, -a);  // Binary Clause
            addBinaryClause(vt, cnf, a, x);    // Binary Ckause
            return x;
        }
        default:
            err("Default case");  // Default Case
            break;
    }
}

CNF* getCNF(VarTable* vt, const PropFormula* f) {
    CNF* res = mkCNF();

    VarIndex x = addClauses(vt, res, f);

    addUnaryClause(vt, res, x);

    return res;
}
