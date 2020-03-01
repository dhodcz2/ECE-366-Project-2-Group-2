givenTestCase = [0x20072000, 0x20e6fffd, 0x00072022, 0x00864020, 0x3105000f, 0x0085402a,
                 0xac082008, 0x20e70008, 0xace8fffc, 0x8c082004, 0x8ce50000]

myTestCase = [0x2084115c, 0x2001115c, 0x00812022, 0x200501a4, 0x30a60539, 0xac062000, 0x8c072000, 0xac070000]

instructions = {"0b000000": {"0b00000100000": "add", "0b00000100010": "sub", "0b00000101010": "slt"},
                "0b001000": "addi", "0b001100": "andi", "0b100011": "lw", "0b101011": "sw"}

# This was stolen from StackOverflow
def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def machine_to_assembly(machine_codes):

    assembly_languages = []

    for machine_code in machine_codes:
        machine_code_hex = hex(machine_code)  # Just for debugging
        machine_code = format(machine_code, '#034b')

        i = machine_code[23:]
        rd = str(machine_code[18:23])
        rt = str(machine_code[13:18])
        rs = str(machine_code[8:13])
        op = str(machine_code[0:8])  # if 0, instruction is r-type

        r_type = True if op == "0b000000" else False

        if r_type:
            funct = "0b" + i
        else:
            imm = twos_comp(int((rd + i), 2), 16)
            imm = hex(imm) if imm >= 8192 else str(imm)

        rd = int(rd, 2) if r_type else None
        rt = int(rt, 2)
        rs = int(rs, 2)

        instruction = instructions[op][funct] if r_type else instructions[op]

        if r_type:
            assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
        else:
            if instruction == "lw" or instruction == "sw":
                assembly_language = f"{instruction} {rt}, 0$({rs})" if imm == "0x0" else f"{instruction} {rt}, {imm}(${rs})"
            else:
                assembly_language = f"{instruction}, ${rt}, ${rs}, {imm}"

        assembly_languages.append(assembly_language)

    return assembly_languages


print("Given Test Case:")
for test in machine_to_assembly(givenTestCase):
    print("\t" + test)

print("My Test Case:")
for test in machine_to_assembly(myTestCase):
    print("\t" + test)








