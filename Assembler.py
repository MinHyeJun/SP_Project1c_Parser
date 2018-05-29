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

        if (not eq(current_token.label, "")) and (not eq(current_token.label, ".")):
            if eq(current_token.operator, "EQU"):
                sym_tab_list[program_number].put_symbol(current_token.label, operate_address(current_token.operand[0]))
            else:
                sym_tab_list[program_number].put_symbol(current_token.label, locctr)

            if (not eq(current_token.label, "")) and ("=" in current_token.operand[0]):
                literal_tab_list[program_number].put_symbol(current_token.operand[0], 0)

        if not eq(current_token.operator, ""):
            if eq(current_token.operator, "LTORG") or eq(current_token.operator, "END"):
                for j in range(0, literal_tab_list[program_number].get_size()):
                    literal = literal_tab_list[program_number].get_symbol(j)
                    literal_tab_list[program_number].modif_symbol(literal, locctr)

                    if "X" in literal:
                        locctr += 1
                    elif "C" in literal:
                        literal = literal.replace("C", "")
                        literal = literal.replace("\'", "")
                        locctr += len(literal)

            elif eq(current_token.operator, "EXTREF"):
                for j in range(0, len(current_token.operand)):
                    external_tab_list[program_number].put_symbol(current_token.operand[j], 0)

            elif len(current_token.operand) > 0:
                for j in range(0, external_tab_list[program_number].get_size()):
                    if external_tab_list[program_number].get_symbol(j) in current_token.operand[0]:
                        modif_size = 6

                        if "+" in current_token.operator:
                            modif_size = 5

                        if "-" in current_token.operand[0]:
                            op_symbols = current_token.operand[0].split("-")
                            modif_tab_list[program_number].put_modif_symbol("+" + op_symbols[0],
                                                                            locctr + (6-modif_size), modif_size)
                            modif_tab_list[program_number].put_modif_symbol("-" + op_symbols[1],
                                                                            locctr + (6 - modif_size), modif_size)
                        else:
                            modif_tab_list[program_number].put_modif_symbol("+" + current_token.operand[0],
                                                                            locctr + (6 - modif_size), modif_size)
                        break
        locctr += current_token.byte_size
        token_index += 1

def pass2():
    code_line = ""
    token_index = 0
    line_size = 0

    for i in range(0, len(token_tab_list)):
        token_tab = token_tab_list[i]
        for j in range(0, token_tab.get_size()):
            token_tab.make_object_code(j)

        j = 0
        while j < token_tab.get_size():
            current_token = token_tab.get_token(j)

            if eq(current_token.label, "."):
                j += 1
                continue
            elif eq(current_token.operator, "START") or eq(current_token.operator, "CSECT"):
                token_index = 0

                start_address = token_tab.get_token(0).location
                program_size = 0

                for k in range(0, token_tab.get_size()):
                    program_size += token_tab.get_token(k).byte_size

                for k in range(0, literal_tab_list[i].get_size()):
                    program_size += literal_tab_list[i].get_literal_size(k)

                code_line = "H" + current_token.label + " " + ("%06X" % start_address) + ("%06X" % (program_size-start_address))

            elif eq(current_token.operator, "EXTDEF"):
                code_line = "D"
                for k in range(0, len(current_token.operand)):
                    code_line += current_token.operand[k] + ("%06X" % sym_tab_list[i].search(current_token.operand[k]))
            elif eq(current_token.operator, "EXTREF"):
                code_line = "R"
                for k in range(0, len(current_token.operand)):
                    code_line += current_token.operand[k]
            elif inst_table.is_instruction(current_token.operator) or eq(current_token.operator, "BYTE") or eq(current_token.operator, "WORD"):
                line_size = 0
                token_index = j

                while token_index < token_tab_list[i].get_size():
                    if token_tab_list[i].get_token(token_index).byte_size == 0 or eq(token_tab_list[i].get_token(token_index).operator, "RESW") or eq(token_tab_list[i].get_token(token_index).operator, "RESB") or (line_size + token_tab.get_token(token_index).byte_size > 30):
                        break;

                    line_size += token_tab.get_token(token_index).byte_size
                    token_index += 1

                code_line = "T" + ("%06X" % current_token.location) + ("%02X" % line_size)

                for k in range(j, token_index):
                    code_line += str(token_tab.get_token(k).object_code)
                    j += 1

                j -= 1
            elif eq(current_token.operator, "LTORG") or eq(current_token.operator, "END"):
                line_size = 0

                for k in range(0, literal_tab_list[i].get_size()):
                    line_size += literal_tab_list[i].get_literal_size(k)

                code_line = "T" + ("%06X" % current_token.location) + ("%02X" % line_size)

                for k in range(0, literal_tab_list[i].get_size()):
                    literal_data = literal_tab_list[i].get_symbol(k)

                    if "X" in literal_data:
                        literal_data = literal_data.replace("X", "")
                        literal_data = literal_data.replace("\'", "")
                    elif "C" in literal_data:
                        temp = ""
                        literal_data = literal_data.replace("C", "")
                        literal_data = literal_data.replace("\'", "")

                        for l in range(0, literal_tab_list[i].get_literal_size(k)):
                            temp += ("%02X" % ord(literal_data[l]))
                        literal_data = temp

                    code_line += literal_data
            else:
                j += 1
                continue

            code_list.append(code_line)
            j += 1


        for j in range(0, modif_tab_list[i].get_size()):
            code_list.append("M" + ("%06X" % modif_tab_list[i].get_location(j)) + ("%02X" % modif_tab_list[i].get_modif_size(j)) + modif_tab_list[i].get_symbol(j))

        if i == 0:
            code_list.append("E" + ("%06X" % token_tab.get_token(0).location))
        else:
            code_list.append("E")

        j += 1

load_input_file("input.txt", line_list)
pass1()
print_symbol_table("symbol_20160286")
pass2()
print_object_code("output_20160286")