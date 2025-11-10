// Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
// SPDX-License-Identifier: Apache-2.0
//

#include <cstdio>
#include <iostream>
#include <string>
#include "y.tab.h"

void yyerror(char const* s)
{
    std::cerr << "Error: " << s << std::endl;
}

extern FILE * yyin;

int main(int argc, char * argv[])
{
    yyin = fopen(argv[1], "r");
    std::cout << "Parsing file: " << argv[1] << std::endl;
    yyparse();
    std::cout << "Parsing completed." << std::endl;
    fclose(yyin);
    return 0;
}
