%{
  #include <iostream>
  using namespace std;
  extern int yylex();
%}

%option noyywrap

LETTER   [a-zA-Z]
DIGIT    [0-9]
HEXDIGIT [0-9a-fA-F]
BINDIGIT [01]
STRING   {LETTER}({LETTER}|{DIGIT}|_)*
SIGN     [+-]

%%

[ \t\r]+   {             }
\n         { yylineno++; }

"package"  { return T_PACKAGE;  }
"import"   { return T_IMPORT;   }
"alias"    { return T_ALIAS;    }
"scalar"   { return T_SCALAR;   }
"constant" { return T_CONSTANT; }
"signed"   { return T_SIGNED;   }
"unsigned" { return T_UNSIGNED; }
"enum"     { return T_ENUM;     }
"indexed"  { return T_INDEXED;  }
"onehot"   { return T_ONEHOT;   }
"graycode" { return T_GRAY;     }
"struct"   { return T_STRUCT;   }
"msb"      { return T_FROM_MSB; }
"from_msb" { return T_FROM_MSB; }
"lsb"      { return T_FROM_LSB; }
"from_lsb" { return T_FROM_LSB; }
"union"    { return T_UNION;    }

{STRING}        { return T_IDENTIFIER; }
{SIGN}?{DIGIT}+ { return T_INTEGER;    }
0[x]{HEXDIGIT}+ { return T_HEX;        }
0[b]{BINDIGIT}+ { return T_BINARY;     }

\"[^"]*\"           { return T_SINGLE_LINE_STRING; }
\"\"\"([^"])*\"\"\" { return T_MULTI_LINE_STRING;  }

"@"  { return T_MODIFIER; }
"{"  { return T_LBRACE;   }
"}"  { return T_RBRACE;   }
"["  { return T_LBRACKET; }
"]"  { return T_RBRACKET; }
":"  { return T_TYPE;     }
"::" { return T_SCOPE;    }
"="  { return T_ASSIGN;   }
"+"  { return T_PLUS;     }
"-"  { return T_MINUS;    }
"**" { return T_POW;      }
"*"  { return T_MUL;      }
"/"  { return T_DIV;      }
"%"  { return T_MOD;      }
"("  { return T_LPAREN;   }
")"  { return T_RPAREN;   }
"<<" { return T_LSHIFT;   }
">>" { return T_RSHIFT;   }
"&"  { return T_AND;      }
"|"  { return T_OR;       }
"^"  { return T_XOR;      }
"~"  { return T_NOT;      }
"<"  { return T_LT;       }
">"  { return T_GT;       }
"<=" { return T_LTE;      }
">=" { return T_GTE;      }
"==" { return T_EQ;       }
"!=" { return T_NEQ;      }
","  { return T_COMMA;    }

%%
