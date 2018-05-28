import copy
import re
from operator import eq


class TokenTable:
    def __init__(self):
        self.sym_tab = 0
        self.lit_tab = 0
        self.ext_tab = 0
        self.inst_tab = 0
        self.token_list = list()
        self.program_counter = 0
        self.locctr = 0

    def set_table(self, sym_tab, lit_tab, ext_tab, inst_tab, locctr):
        self.sym_tab = sym_tab
        self.lit_tab = lit_tab
        self.ext_tab = ext_tab
        self.inst_tab = inst_tab
        self.locctr = copy.deepcopy(locctr)

    def put_token(self, line):
        self.token_list.append(Token(line, self.inst_tab, self.locctr))

    def get_token(self, index):
        return self.token_list[index]

    def get_object_code(self, index):
        return self.token_list[index].object_code

    def get_size(self):
        return len(self.token_list)

    def address_to_string(self, address, size):
        address_data = ""
        if size == 4:
            address_data = "%05X" % (address & 0xFFFFF)
        else:
            address_data = "%03X" % (address & 0xFFF)

        return address_data

    def make_object_code(self, index):
        self.program_counter += self.token_list[index].byte_size
        current_token = self.token_list[index]
        operator = current_token.operator
        target_address = 0
        operand_data = ""
        address_data = ""

        if not operator:
            return

        if "+" in operator:
            operator = operator.replace("+", "")

        if self.inst_tab.is_instruction(operator):
            opcode = self.inst_tab.get_opcode(operator)

            if self.inst_tab.get_format(operator) == 3:
                opcode += (current_token.get_flag(32)) // 16
                opcode += (current_token.get_flag(16)) // 16

                xbpe = 0
                xbpe += current_token.get_flag(8)
                xbpe += current_token.get_flag(4)
                xbpe += current_token.get_flag(2)
                xbpe += current_token.get_flag(1)

                if self.inst_tab.get_number_of_operand(operator) >= 1:
                    if current_token.get_flag(32) == 32:
                        operand_data = current_token.operand[0]

                        if "@" in operand_data:
                            operand_data = operand_data.replace("@", "")

                        if "=" in operand_data:
                            operand_data = operand_data.replace("=", "")
                            target_address = self.lit_tab.search(operand_data)
                        else:
                            target_address = self.sym_tab.search(operand_data)
                    elif current_token.get_flag(16) == 16:
                        operand_data = current_token.operand[0]

                        if "#" in operand_data:
                            operand_data = operand_data.replace("#", "")

                        target_address = int(operand_data)

                    if current_token.get_flag(2) == 2:
                        target_address -= self.program_counter
                    elif current_token.get_flag(1) == 1:
                        target_address = 0
                else:
                    target_address = 0

                address_data = self.address_to_string(target_address, current_token.byte_size)

                current_token.object_code = ("%02X" % opcode) + ("%01X" % xbpe) + address_data

            elif self.inst_tab.get_format(operator) == 2:
                register1 = 0
                register2 = 0

                if self.inst_tab.get_number_of_operand(operator) == 1:
                    if eq(current_token.operand[0], "A"):
                        register1 = 0
                    elif eq(current_token.operand[0], "X"):
                        register1 = 1
                    elif eq(current_token.operand[0], "L"):
                        register1 = 2
                    elif eq(current_token.operand[0], "B"):
                        register1 = 3
                    elif eq(current_token.operand[0], "S"):
                        register1 = 4
                    elif eq(current_token.operand[0], "T"):
                        register1 = 5

                    register2 = 0

                elif self.inst_tab.get_number_of_operand(operator) == 2:
                    if eq(current_token.operand[0], "A"):
                        register1 = 0
                    elif eq(current_token.operand[0], "X"):
                        register1 = 1
                    elif eq(current_token.operand[0], "L"):
                        register1 = 2
                    elif eq(current_token.operand[0], "B"):
                        register1 = 3
                    elif eq(current_token.operand[0], "S"):
                        register1 = 4
                    elif eq(current_token.operand[0], "T"):
                        register1 = 5

                    if eq(current_token.operand[1], "A"):
                        register2 = 0
                    elif eq(current_token.operand[1], "X"):
                        register2 = 1
                    elif eq(current_token.operand[1], "L"):
                        register2 = 2
                    elif eq(current_token.operand[1], "B"):
                        register2 = 3
                    elif eq(current_token.operand[1], "S"):
                        register2 = 4
                    elif eq(current_token.operand[1], "T"):
                        register2 = 5

                current_token.object_code = ("%02X" % opcode) + ("%01X" % register1) + ("%01X" % register2)

        elif eq(operator, "BYTE") | eq(operator, "WORD"):
            if eq(operator, "BYTE"):
                if current_token.operand[0][0] == 'X' :
                    operand_data = current_token.operand[0].replace("X|\'", "")
                    current_token.object_code = operand_data
            elif eq(operator, "WORD"):
                for i in range(0, self.ext_tab.get_size()):
                    if self.ext_tab.get_symbol(i) in current_token.operand[0]:
                        break;
                if i < self.ext_tab.get_size():
                    current_token.object_code = "%06X" % 0

class Token:
    def __init__(self, line, inst_table, locctr):
        self.label = ""
        self.operator = ""
        self.operand = list()
        self.comment = ""
        self.location = 0
        self.nixbpe = 0
        self.object_code = 0
        self.byte_size = 0
        self.inst_table = inst_table
        self.parsing(line, locctr)

    def parsing(self, line, locctr):
        units = re.split("\t|\n", line)

        if eq(units[0], "."):
            self.label = units[0]
            if len(units) > 1:
                self.comment = units[1]
        else:
            self.label = units[0]
            self.operator = units[1]
            if not self.inst_table.get_number_of_operand(self.operator) == 0:
                if len(units) > 2:
                    self.operand = units[2].split(',')

                if len(units) > 3:
                    self.comment = units[3]
            else:
                if not eq(units[2], ""):
                    self.comment = units[2]

            if "+" in self.operator:
                self.byte_size = 4
                self.set_flag(1, 1)
            else:
                self.byte_size = self.get_inst_size(self.operator)
                if (len(self.operand) > 0) & (self.byte_size > 0):
                    self.set_flag(2, 1)

            if self.byte_size >= 3:
                if len(self.operand):
                    if len(self.operand) > 1:
                        if eq(self.operand[1], "X"):
                            self.set_flag(8, 1)
                    if "#" in self.operand[0]:
                        self.set_flag(16, 1)
                        self.set_flag(2, 1)
                    elif "@" in self.operand[0]:
                        self.set_flag(32, 1)
                    else:
                        self.set_flag(32, 1)
                        self.set_flag(16, 1)

            self.location = locctr

    def set_flag(self, flag, value):
        if value == 1:
            self.nixbpe |= flag
        else:
            self.nixbpe ^= flag

    def get_flag(self, flag):
        return self.nixbpe & flag

    def get_inst_size(self, operator):
        if self.inst_table.is_instruction(operator):
            return self.inst_table.get_format(operator)
        elif eq(operator, "RESB"):
            return int(self.operand[0])
        elif eq(operator, "RESW"):
            return int(self.operand[0]) * 3
        elif eq(operator, "BYTE"):
            return 1
        elif eq(operator, "WORD"):
            return 3
        else:
            return 0