import Assembler

Assembler.load_input_file("input.txt")
Assembler.pass1()
Assembler.print_symbol_table("symbol_20160286")
Assembler.pass2()
Assembler.print_object_code("output_20160286")