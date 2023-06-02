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
        }
        case AND: {
            VarIndex c = addClauses(vt, cnf, pf->data.operands[0]);
            VarIndex d = addClauses(vt, cnf, pf->data.operands[1]);
            VarIndex x = mkFreshVariable(vt);
            addBinaryClause(vt, cnf, -x, c);
            addBinaryClause(vt, cnf, -x, d);
            addTernaryClause(vt, cnf, -c, -d, x);
            return x;
        }
        case OR: {
            VarIndex c = addClauses(vt, cnf, pf->data.operands[0]);
            VarIndex d = addClauses(vt, cnf, pf->data.operands[1]);
            VarIndex x = mkFreshVariable(vt);
            addTernaryClause(vt, cnf, -x, c, d);
            addBinaryClause(vt, cnf, -c, x);
            addBinaryClause(vt, cnf, -d, x);
            return x;
        }
        case IMPLIES: {
            VarIndex c = addClauses(vt, cnf, pf->data.operands[0]);
            VarIndex d = addClauses(vt, cnf, pf->data.operands[1]);
            VarIndex x = mkFreshVariable(vt);
            addTernaryClause(vt, cnf, -x, -c, d);
            addBinaryClause(vt, cnf, c, x);
            addBinaryClause(vt, cnf, -d, x);
            return x;
        }
        case EQUIV: {
            VarIndex a = addClauses(vt, cnf, pf->data.operands[0]);
            VarIndex b = addClauses(vt, cnf, pf->data.operands[1]);
            VarIndex x = mkFreshVariable(vt);
            addTernaryClause(vt, cnf, -x, -a, b);
            addTernaryClause(vt, cnf, -x, -b, a);
            addTernaryClause(vt, cnf, x, -a, -b);
            addTernaryClause(vt, cnf, x, a, b);
            return x;
        }
        case NOT: {
            VarIndex a = addClauses(vt, cnf, pf->data.single_op);
            VarIndex x = mkFreshVariable(vt);
            addBinaryClause(vt, cnf, -x, -a);
            addBinaryClause(vt, cnf, a, x);
            return x;
        }
        default:
            err("Weird case man");
            break;
    }
}

CNF* getCNF(VarTable* vt, const PropFormula* f) {
    CNF* res = mkCNF();

    VarIndex x = addClauses(vt, res, f);

    addUnaryClause(vt, res, x);

    return res;
}
