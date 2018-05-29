class InstTable:
    def __init__(self, inst_file):
        self.inst_dic = dict()
        self.open_file(inst_file)

    def open_file(self, inst_file):
        f = open(inst_file, 'r')
        for line in f:
            token = Instruction(line)
            self.inst_dic[token.instruction] = token
        f.close()

    def get_opcode(self, inst_name):
        keys = self.inst_dic.keys()
        if inst_name in keys:
            return self.inst_dic.get(inst_name).opcode
        else:
            return -1

    def get_number_of_operand(self, inst_name):
        keys = self.inst_dic.keys()
        if inst_name in keys:
            return self.inst_dic.get(inst_name).number_of_operand
        else:
            return -1

    def get_format(self, inst_name):
        keys = self.inst_dic.keys()
        if inst_name in keys:
            return self.inst_dic.get(inst_name).format
        else:
            return 0

    def is_instruction(self, name):
        keys = self.inst_dic.keys()
        if name in keys:
            return True
        else:
            return False


class Instruction:
    def __init__(self, line):
        self.instruction = ""
        self.opcode = 0
        self.number_of_operand = 0
        self.format = 0
        self.parsing(line)

    def parsing(self, line):
        units = line.split()
        self.instruction = units[0]
        self.format = int(units[1])
        self.opcode = int(units[2], 16)
        self.number_of_operand = int(units[3])
