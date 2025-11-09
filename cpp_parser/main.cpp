// Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
// SPDX-License-Identifier: Apache-2.0
//

#include <iostream>

int yyparse();

void yyerror(char const* s)
{
    std::cerr << "Error: " << s << std::endl;
}

int main()
{
    yyparse();
    return 0;
}
