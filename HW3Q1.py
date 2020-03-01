givenTestCase = [0x20072000, 0x20e6fffd, 0x00072022, 0x00864020, 0x3105000f, 0x0085402a,
                 0xac082008, 0x20e70008, 0xace8fffc, 0x8c082004, 0x8ce50000]

myTestCase = [0x2084115c, 0x2001115c, 0x00812022, 0x200501a4, 0x30a60539, 0xac062000, 0x8c072000, 0xac070000]

instructions = {"0b000000": {"0b100000": "add", "0b100010": "sub", "0b101010": "slt",
                             "0b011010": "div", "0b010000": "mfhi", "0b000100": "sllv",
                             "0b000011": "sra", "0b001000": "jr",  "0b100110": "xor",
                             "0b000000": "sll"},
                "0b001000": "addi", "0b001100": "andi", "0b100011": "lw", "0b101011": "sw", "0b000100": "beq",
                "0b000101": "bne", "0b000010": "j", "0b000011": "jal", "0b001110": "xori", "0b001010": "slti",
                }

i = ""
rd = ""
rt = ""
rs = ""
op = ""
shamt = ""
jumpi = ""
assembly_language = ""
imm = 0

class showUpdate(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        oldRegisters = registers
        oldPc = pc
        self.f()
        for key in registers.keys():
            if registers[key] != oldRegisters[key]:
                print(f"{key}: {oldRegisters[key]} -> {registers[key]}")
            if oldPc != pc:
                print(f"pc: {oldPc} -> {pc}")


# This was stolen from StackOverflow
def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def machine_to_assembly(machine_codes):
    global i
    global rd
    global rt
    global rs
    global op
    global shamt
    global jumpi
    global assembly_language
    global imm

    assembly_languages = []

    for machine_code in machine_codes:
        machine_code_hex = hex(machine_code)  # Just for debugging
        machine_code = format(machine_code, '#034b')

        i = machine_code[23:]
        rd = str(machine_code[18:23])
        rt = str(machine_code[13:18])
        rs = str(machine_code[8:13])
        op = str(machine_code[0:8])  # if 0, instruction is r-type
        shamt = str(machine_code[-11:-6])
        jumpi = str(machine_code[9:])

        r_type = True if op == "0b000000" else False

        if r_type:
            funct = "0b" + i[-6:]
        else:
            imm = twos_comp(int((rd + i), 2), 16)
            imm = hex(imm) if imm >= 8192 else str(imm)

        rd = int(rd, 2)
        rt = int(rt, 2)
        rs = int(rs, 2)
        shamt = int(shamt, 2)
        jumpi = int(jumpi, 2)

        instruction = instructions[op][funct] if r_type else instructions[op]
        pythonInstruction = locals()[instruction]()
        pythonInstruction()

        assembly_languages.append(assembly_language)

    return assembly_languages


print("Given Test Case:")
for test in machine_to_assembly(givenTestCase):
    print("\t" + test)

print("My Test Case:")
for test in machine_to_assembly(myTestCase):
    print("\t" + test)

def reg(num):
    return "$" + str(num)

@showUpdate
def sra():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = registers[reg(rt)] >> imm

@showUpdate
def xori():
    assembly_language = f"{instruction}, ${rt}, ${rs}, {imm}"
    registers[reg(rt)] = registers[reg(rs)] ^ imm

@showUpdate
def slti():
    assembly_language = f"{instruction}, ${rt}, ${rs}, {imm}"
    registers[reg(rt)] = 1 if registers[reg(rs)] < imm else 0

@showUpdate
def xor():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = registers[reg(rs)] ^ registers[reg(rt)]

@showUpdate
def sllv():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = registers[reg(rt)] << rs

@showUpdate
def sll():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = registers[reg(rt)] << shamt

@showUpdate
def add():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = registers[reg(rs)] + registers[reg(rt)]

@showUpdate
def sub():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = registers[reg(rs)] - registers[reg(rt)]

@showUpdate
def slt():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = 1 if registers[reg(rs)] < registers[reg(rt)] else 0

@showUpdate
def addi():
    assembly_language = f"{instruction}, ${rt}, ${rs}, {imm}"
    registers[reg(rt)] = registers[reg(rs)] - imm

@showUpdate
def andi():
    assembly_language = f"{instruction}, ${rt}, ${rs}, {imm}"
    registers[reg(rt)] = registers[reg(rs)] & imm

@showUpdate
def lw():
    assembly_language = f"{instruction} {rt}, 0$({rs})" if imm == "0x0" else f"{instruction} {rt}, {imm}(${rs})"
    registers[reg(rt)] = dataMemory[registers[reg(rs)]+imm]

@showUpdate
def sw():
    assembly_language = f"{instruction} {rt}, 0$({rs})" if imm == "0x0" else f"{instruction} {rt}, {imm}(${rs})"
    dataMemory[registers[reg(rs)]+imm] = registers[reg(rt)]

@showUpdate
def div():
    assembly_language = f"{instruction}, ${rs}, %{rt}"
    registers["lo"] = registers[reg(rs)] / registers[reg(rt)]
    registers["hi"] = registers[reg(rs)] % registers[reg(rt)]

@showUpdate
def mfhi():
    assembly_language = f"{instruction} ${rd}"
    registers[reg(rd)] = registers["hi"]

@showUpdate
def beq():
    assembly_language = f"{instruction}, ${rs}, ${rt}, {imm}"
    if registers[reg(rs)] == registers[reg(rt)]:
        incrementPc()
        incrementPc(imm)
    else:
        pass

@showUpdate
def bne():
    assembly_language = f"{instruction}, ${rs}, ${rt}, {imm}"
    if registers[reg(rs)] == registers[reg(rt)]:
        pass
    else:
        incrementPc()
        incrementPc(imm)

@showUpdate
def j():
    setPc(imm)

@showUpdate
def jr():
    assembly_language = f"{instruction}, ${rs}"
    setPc(registers[reg(rs)])

@showUpdate
def jal():
    registers[reg(31)] = int(pc / 4)
    setPc(registers[reg(rs)])

@showUpdate
def sra():
    assembly_language = f"{instruction}, ${rd}, ${rt}, {shamt}"
    registers[reg(rd)] = registers[reg(rt)] >> imm

@showUpdate
def xori():
    assembly_language = f"{instruction}, ${rt}, ${rs}, {imm}"
    registers[reg(rt)] = registers[reg(rs)] ^ imm

@showUpdate
def slti():
    assembly_language = f"{instruction}, ${rt}, ${rs}, {imm}"
    registers[reg(rt)] = 1 if registers[reg(rs)] < imm else 0

@showUpdate
def xor():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = registers[reg(rs)] ^ registers[reg(rt)]

@showUpdate
def sllv():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${rt}"
    registers[reg(rd)] = registers[reg(rt)] << rs

@showUpdate
def sll():
    assembly_language = f"{instruction} ${rd}, ${rs}, ${shamt}"
    registers[reg(rd)] = registers[reg(rt)] << shamt






