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
