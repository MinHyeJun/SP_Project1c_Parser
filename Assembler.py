import re
import sys
from operator import eq
import InstTable
import TokenTable
import SymbolTable

inst_table = InstTable.InstTable("inst.data")
line_list = list()
sym_tab_list = list()
token_tab_list = list()
code_list = list()
literal_tab_list = list()
external_tab_list = list()
modif_tab_list = list()

locctr =0
program_number = 0

def tohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))

def load_input_file(file_name, list):
    f = open(file_name, 'r')
    for line in f:
        list.append(line)
    f.close()

def print_object_code(file_name):
    f = open(file_name, 'w')
    for line in code_list:
        f.write(line+"\n")
        if line[0] == 'E':
            f.write("\n")
    f.close()

def print_symbol_table(file_name):
    f = open(file_name, 'w')
    for symbol in sym_tab_list:
        for i in range(0, symbol.get_size()):
            output = symbol.get_symbol(i) + "\t" + ("%X" % symbol.get_location(i))
            f.write(output + "\n")
        f.write("\n")

def operate_address(input_operand):
    if "*" in input_operand:
        return locctr
    else:
        if "-" in input_operand:
            operands = input_operand.split("-")
            return sym_tab_list[program_number].search(operands[0]) - sym_tab_list[program_number].search(operands[1])

def pass1():
    token_index = 0
    global locctr
    global program_number
    for line in line_list:
        if "START" in line:
            program_number = 0
            locctr = 0
            token_index = 0
            sym_tab_list.append(SymbolTable.SymbolTable())
            literal_tab_list.append(SymbolTable.SymbolTable())
            external_tab_list.append(SymbolTable.SymbolTable())
            modif_tab_list.append(SymbolTable.SymbolTable())
            token_tab_list.append(TokenTable.TokenTable())
            token_tab_list[program_number].set_table(sym_tab_list[program_number], literal_tab_list[program_number],
                                                     external_tab_list[program_number], inst_table, locctr)

        elif "CSECT" in line:
            program_number += 1
            locctr = 0
            token_index = 0
            sym_tab_list.append(SymbolTable.SymbolTable())
            literal_tab_list.append(SymbolTable.SymbolTable())
            external_tab_list.append(SymbolTable.SymbolTable())
            modif_tab_list.append(SymbolTable.SymbolTable())
            token_tab_list.append(TokenTable.TokenTable())
            token_tab_list[program_number].set_table(sym_tab_list[program_number], literal_tab_list[program_number],
                                                     external_tab_list[program_number], inst_table, locctr)

        token_tab_list[program_number].put_token(line)

        current_token = token_tab_list[program_number].get_token(token_index)

        if (not eq(current_token.label, "")) & (not eq(current_token.label, ".")):
            if eq(current_token.operator, "EQU"):
                sym_tab_list[program_number].put_symbol(current_token.label, operate_address(current_token.operand[0]))
            else:
                sym_tab_list[program_number].put_symbol(current_token.label, locctr)

            if (not eq(current_token.label, "")) & ("=" in current_token.operand[0]):
                literal_tab_list[program_number].put_symbol(current_token.operand[0], 0)

        if not eq(current_token.operator, ""):
            if eq(current_token.operator, "LTORG") | eq(current_token.operator, "END"):
                for j in range(0, literal_tab_list[program_number].get_size()):
                    literal = literal_tab_list[program_number].get_symbol(j)
                    literal_tab_list[program_number].modif_symbol(literal, locctr)

                    if "X" in literal:
                        locctr += 1
                    elif "C" in literal:
                        literal = literal.replace("C|\'", "")
                        locctr += len(literal)

            elif eq(current_token.operator, "EXTREF"):
                for j in range(0, len(current_token.operand)):
                    external_tab_list[program_number].put_symbol(current_token.operand[j], 0)

            elif eq(current_token.operand, ""):
                for j in external_tab_list[program_number].get_size():
                    if external_tab_list[program_number].get_symbol(j) in current_token.operand[0]:
                        modif_size = 6

                        if "+" in current_token.operator:
                            modif_size = 5

                        if "-" in current_token.operator:
                            op_symbols = current_token.operand[0].split("-")
                            modif_tab_list[program_number].put_modif_symbol("+" + op_symbols[0],
                                                                            locctr + (6-modif_size), modif_size)
                            modif_tab_list[program_number].put_modif_symbol("-" + op_symbols[1],
                                                                            locctr + (6 - modif_size), modif_size)
                        else:
                            modif_tab_list[program_number].put_modif_symbol("+" + current_token.operand[0],
                                                                            locctr + (6 - modif_size), modif_size)
        locctr += current_token.byte_size
        token_index += 1


load_input_file("input.txt", line_list)
pass1()
print_symbol_table("symbol_20160286")
