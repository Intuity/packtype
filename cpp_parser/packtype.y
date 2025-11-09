%{
  #include <cstdio>
  #include <iostream>
  using namespace std;

  // Declare stuff from Flex that Bison needs to know about:
  extern int yylex();
  extern int yyparse();
  extern FILE *yyin;

  void yyerror(const char *s);
%}

%start package
%define parse.error verbose

// Keywords
%token T_PACKAGE
%token T_IMPORT
%token T_ALIAS
%token T_SCALAR
%token T_CONSTANT
%token T_SIGNED
%token T_UNSIGNED
%token T_ENUM
%token T_INDEXED
%token T_ONEHOT
%token T_GRAY
%token T_STRUCT
%token T_FROM_MSB
%token T_FROM_LSB
%token T_UNION
%token T_IDENTIFIER
%token T_INTEGER
%token T_HEX
%token T_BINARY
%token T_SINGLE_LINE_STRING
%token T_MULTI_LINE_STRING
%token T_LBRACE
%token T_RBRACE
%token T_LBRACKET
%token T_RBRACKET
%token T_TYPE
%token T_SCOPE
%token T_ASSIGN
%token T_PLUS
%token T_MINUS
%token T_POW
%token T_MUL
%token T_DIV
%token T_MOD
%token T_LPAREN
%token T_RPAREN
%token T_LSHIFT
%token T_RSHIFT
%token T_AND
%token T_OR
%token T_XOR
%token T_NOT
%token T_LT
%token T_GT
%token T_LTE
%token T_GTE
%token T_EQ
%token T_NEQ
%token T_MODIFIER
%token T_COMMA

%%

/* ==========================================================================
 * Utilities
 * ========================================================================== */

descr : T_SINGLE_LINE_STRING
      | T_MULTI_LINE_STRING
      ;

dimension : T_LBRACKET expr T_RBRACKET
          ;

dimensions : dimension
           | dimensions dimension
           ;

signedness : T_SIGNED
           | T_UNSIGNED
           ;

field_assignment : T_IDENTIFIER T_ASSIGN expr
                 | T_IDENTIFIER T_ASSIGN expr descr
                 ;

field_assignments_body : field_assignment
                       | field_assignments_body field_assignment
                       ;

field_assignments : T_LBRACE field_assignments_body T_RBRACE
                  ;

modifier : T_MODIFIER T_IDENTIFIER T_ASSIGN T_SINGLE_LINE_STRING
         | T_MODIFIER T_IDENTIFIER T_ASSIGN T_IDENTIFIER
         | T_MODIFIER T_IDENTIFIER T_ASSIGN T_INTEGER
         ;

modifiers : modifier
          | modifiers modifier
          ;

flex_ref : T_IDENTIFIER
         | foreign_ref
         ;

flex_field : T_IDENTIFIER T_TYPE flex_ref
           | T_IDENTIFIER T_TYPE flex_ref dimensions
           | T_IDENTIFIER T_TYPE flex_ref descr
           | T_IDENTIFIER T_TYPE flex_ref dimensions descr
           | scalar
           ;

/* ==========================================================================
 * Package
 * ========================================================================== */

package : T_PACKAGE T_IDENTIFIER T_LBRACE descr package_body T_RBRACE
        | T_PACKAGE T_IDENTIFIER T_LBRACE package_body T_RBRACE
        ;

package_body :
             | import
             | alias
             | constant
             | scalar
             | enum
             | struct
             | union
             ;

/* ==========================================================================
 * Imports
 * Example: import other_pkg::VALUE_A
 * ========================================================================== */

foreign_ref : T_IDENTIFIER T_SCOPE T_IDENTIFIER
            ;

import : T_IMPORT foreign_ref
       ;

/* ==========================================================================
 * Alias
 * ========================================================================== */

/* Examples:
 * Simple alias     -> local_type_t : foreign_type_t
 * With dimensions  -> local_array_t : foreign_type_t[10][20]
 * With description -> local_type_t : foreign_type_t
                           "This is a type"
 * With assignment  -> local_const_t : foreign_type_t = foreign_pkg::VALUE_A
 */
alias_base : T_IDENTIFIER T_TYPE flex_ref
           | T_IDENTIFIER T_TYPE flex_ref dimensions
           ;
alias_assign : alias_base T_ASSIGN expr
             | alias_base T_ASSIGN field_assignments
             ;
alias : alias_base
      | alias_base descr
      | alias_assign
      | alias_assign descr
      ;

/* ==========================================================================
 * Constant
 * ========================================================================== */

/* Examples:
 * Simple constant  -> MY_VALUE : constant = 123
 * With dimension   -> MY_VALUE : constant[8] = 123
 * With description -> MY_VALUE : constant[8] = 123
                           "This is a constant"
 */

constant : T_IDENTIFIER T_TYPE T_CONSTANT T_ASSIGN expr
         | T_IDENTIFIER T_TYPE T_CONSTANT T_ASSIGN expr descr
         | T_IDENTIFIER T_TYPE T_CONSTANT dimension T_ASSIGN expr
         | T_IDENTIFIER T_TYPE T_CONSTANT dimension T_ASSIGN expr descr
         ;

/* ==========================================================================
 * Scalar
 * ========================================================================== */

/* Examples:
 * Simple constant  -> my_type_t : scalar[4]
 * With signedness  -> my_type_t : signed scalar[8]
 * With description -> my_type_t : scalar[8]
                           "This is a scalar"
 */

scalar_signed : T_SCALAR
              | signedness T_SCALAR
              ;

scalar_dim : scalar_signed
           | scalar_signed dimensions
           ;

scalar : T_IDENTIFIER T_TYPE scalar_dim
       | T_IDENTIFIER T_TYPE scalar_dim descr
       ;

/* ==========================================================================
 * Enumerations
 * ========================================================================== */

/* Example:
 * enum gray [2] my_enum_e {
 *     @prefix=MY_ENUM
 *     "Describes my Gray-coded enumeration"
 *     VALUE_A : constant
 *     VALUE_B : constant
 *     VALUE_C : constant
 *     VALUE_D : constant
 * }
 */

enum_mode : T_ENUM
          | T_ENUM T_INDEXED
          | T_ENUM T_ONEHOT
          | T_ENUM T_GRAY
          ;

enum_dim : enum_mode
         | enum_mode dimension
         ;

enum_body_entry_simple : T_IDENTIFIER
                       | T_IDENTIFIER descr
                       ;

enum_body_entry_typed  : T_IDENTIFIER T_TYPE T_CONSTANT
                       | T_IDENTIFIER T_TYPE T_CONSTANT descr
                       ;

enum_body_entry_assign : T_IDENTIFIER T_ASSIGN expr
                       | T_IDENTIFIER T_ASSIGN expr descr
                       ;

enum_body_entry : enum_body_entry_simple
                | enum_body_entry_typed
                | enum_body_entry_assign
                | constant
                ;

enum_body_inner : enum_body_entry
                | enum_body_inner enum_body_entry
                ;

enum_body : enum_body_inner
          | modifiers enum_body_inner
          ;

enum : enum_dim T_IDENTIFIER T_TYPE T_LBRACE descr enum_body T_RBRACE
     | enum_dim T_IDENTIFIER T_TYPE T_LBRACE enum_body T_RBRACE
     ;

/* ==========================================================================
 * Structs
 * ========================================================================== */

/* Example:
 * struct msb [32] my_struct_t {
 *     "Describes my struct"
 *     field_a : scalar[8]
 *     field_b : some_type_t
 * }
 */

struct_mode : T_STRUCT
            | T_STRUCT T_FROM_MSB
            | T_STRUCT T_FROM_LSB
            ;

struct_dim : struct_mode
           | struct_mode dimension
           ;

struct_body_inner : flex_field
                  | struct_body_inner flex_field
                  ;

struct_body : struct_body_inner
            | descr struct_body_inner
            ;

struct : struct_dim T_IDENTIFIER T_LBRACE struct_body T_RBRACE
       ;

/* ==========================================================================
 * Unions
 * ========================================================================== */

/* Example:
 * union my_union_u {
 *     "Describes my union"
 *     member_a : scalar[8]
 *     member_b : type_8b_wide_t
 * }
 */

union_body_inner : flex_field
                  | union_body_inner flex_field
                  ;

union_body : union_body_inner
            | descr union_body_inner
            ;

union : T_UNION T_IDENTIFIER T_LBRACE union_body T_RBRACE
      ;

/* ==========================================================================
 * Expressions
 * ========================================================================== */

operator : T_PLUS
         | T_MINUS
         | T_POW
         | T_MUL
         | T_DIV
         | T_MOD
         | T_LSHIFT
         | T_RSHIFT
         | T_AND
         | T_OR
         | T_XOR
         | T_NOT
         | T_LT
         | T_GT
         | T_LTE
         | T_GTE
         | T_EQ
         | T_NEQ
         ;

expr_func_args : expr
               | expr_func_args T_COMMA expr
               ;

expr_func : T_IDENTIFIER T_LPAREN expr_func_args T_RPAREN
          ;

expr_term : flex_ref
          | T_INTEGER
          | T_HEX
          | T_BINARY
          | T_LPAREN expr T_RPAREN
          | expr_func
          ;

expr : expr_term
     | expr operator expr_term
     ;

%%
