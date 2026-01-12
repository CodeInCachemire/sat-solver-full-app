#pragma once
#include <stdio.h>

#include "cnf.h"
#include "variables.h"

CNF* parseCNF(FILE* input, VarTable* vt);
