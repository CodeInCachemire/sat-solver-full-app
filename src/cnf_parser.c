#include "cnf_parser.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cnf.h"
#include "variables.h"

CNF* parseCNF(FILE* input, VarTable* vt) {
    CNF* cnf = mkCNF();
    char line[4096];

    while (fgets(line, sizeof(line), input)) {
        Literal a = 0, b = 0, c = 0;
        int count = 0;

        char* tok = strtok(line, " \n");
        while (tok && count < 3) {
            int neg = (tok[0] == '-');
            char* name = neg ? tok + 1 : tok;

            VarIndex v = mkVariable(vt, strdup(name));
            Literal lit = neg ? -v : v;

            if (count == 0) a = lit;
            if (count == 1) b = lit;
            if (count == 2) c = lit;

            count++;
            tok = strtok(NULL, " \n");
        }

        Clause* cl = mkTernaryClause(vt, a, b, c);
        addClauseToCNF(cnf, cl);
    }

    return cnf;
}
