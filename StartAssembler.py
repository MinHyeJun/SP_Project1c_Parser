from Assembler import assembler

assembler.load_input_file("input.txt")
assembler.pass1()
assembler.print_symbol_table("symbol_20160286")
assembler.pass2()
assembler.print_object_code("output_20160286")