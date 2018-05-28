class SymbolTable:
    def __init__(self):
        self.symbol_list = list()
        self.location_list = list()
        self.modif_size_list = list()

    def put_symbol(self, symbol, location):
        input_symbol = symbol
        if "=" in input_symbol:
            input_symbol = input_symbol.replace("=", "")
        if input_symbol not in self.symbol_list:
            self.symbol_list.append(input_symbol)
            self.location_list.append(location)

    def put_modif_symbol(self, modif_symbol, location, modif_size):
        self.symbol_list.append(modif_symbol)
        self.location_list.append(location)
        self.modif_size_list.append(modif_size)

    def modif_symbol(self, symbol, new_location):
        input_symbol = symbol

        if "=" in input_symbol:
            input_symbol = input_symbol.replace("=", "")

        if input_symbol in self.symbol_list:
            index = self.symbol_list.index(input_symbol)
            self.location_list[index] = new_location

    def search(self, symbol):
        if symbol in self.symbol_list:
            index = self.symbol_list.index(symbol)
            return self.location_list[index]
        else:
            return -1

    def get_symbol(self, index):
        return self.symbol_list[index]

    def get_location(self, index):
        return self.location_list[index]

    def get_size(self):
        return len(self.symbol_list)

    def get_literal_size(self, index):
        if "X" in self.symbol_list[index]:
            return 1
        elif "C" in self.symbol_list[index]:
            literal = self.symbol_list[index].replace("C|\'", "")
            return len(literal)
        else:
            return 0

    def get_modif_size(self, index):
        return self.modif_size_list[index]