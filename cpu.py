"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # The memory storage for the RAM.
        self.reg = [0] * 8   # 8 new registers.
        self.pc = 0          # The program counter.
        self.running = True
        self.fl = 0b00000000
        self.reg[7] = 0xF4

        # The branchtable.
        self.branchtable = {}
        self.branchtable[HLT] = self.HLT
        self.branchtable[LDI] = self.LDI
        self.branchtable[PRN] = self.PRN
        self.branchtable[ADD] = self.ADD
        self.branchtable[MUL] = self.MUL
        self.branchtable[PUSH] = self.PUSH
        self.branchtable[POP] = self.POP
        self.branchtable[CALL] = self.CALL
        self.branchtable[RET] = self.RET
        self.branchtable[CMP] = self.CMP
        self.branchtable[JMP] = self.JMP
        self.branchtable[JEQ] = self.JEQ
        self.branchtable[JNE] = self.JNE

    # Memory Address Register
    def ram_read(self, MAR):
        return self.ram[MAR]
    
    # Memory Data Register
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def HLT(self):
        self.running = False

    def LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b

    def PRN(self):
        num = self.ram_read(self.pc + 1)
        print(self.reg[num])

    def ADD(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADD", operand_a, operand_b)

    def MUL(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MUL", operand_a, operand_b)

    def PUSH(self):
        # Decrement the pointer.
        self.reg[7] -= 1

        # Grab reg_index from memory and grab the value from register.
        reg_index = self.ram[self.pc + 1]
        value = self.reg[reg_index]

        # Insert the value of the SP in RAM.
        sp = self.reg[7]
        self.ram[sp] = value

    def POP(self):
        # Get the stack pointer address.
        sp = self.reg[7]

        # Grab reg_index from memory and set the value with the SP in RAM.
        reg_index = self.ram[self.pc + 1]
        value = self.ram[sp]

        # Take the value from the stack and put it in register.
        self.reg[reg_index] = value

        # Increment SP.
        self.reg[7] += 1
    
    def CALL(self):
        # Get the register number
        reg = self.ram_read(self.pc + 1)

        # From the register, get the address to jump to.
        address = self.reg[reg]

        # Push the command after CALL onto the stack.
        return_address = self.pc + 2

        # Decrement SP.
        self.reg[7] -= 1
        sp = self.reg[7]

        # Put the return address on the stack.
        self.ram[sp] = return_address

        # Look at register, then jump to the address.
        self.pc = address

    def RET(self):
        # Pop the return address off the stack.
        sp = self.reg[7]
        return_address = self.ram[sp]
        self.reg[7] += 1

        # Set the PC to return address.
        self.pc = return_address
    
    def CMP(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("CMP", operand_a, operand_b)

    def JMP(self):
        # Get the register number.
        reg = self.ram_read(self.pc + 1)

        # From the register, get the address to jump to.
        address = self.reg[reg]

        # Look at register, then jump to the address.
        self.pc = address

    def JEQ(self):
        # Get the register number.
        reg = self.ram_read(self.pc + 1)

        # From the register, get the address to jump to.
        address = self.reg[reg]
        if self.fl == 0b00000001:
            # Look at register, then jump to the address.
            self.pc = address
        else:
            self.pc += 2

    def JNE(self):
        # Get the register number.
        reg = self.ram_read(self.pc + 1)

        # From the register, get the address to jump to.
        address = self.reg[reg]
        if self.fl != 0b00000001:
            # Look at register, then jump to the address.
            self.pc = address
        else:
            self.pc += 2

    def load(self, filename):
        """Load a program into memory."""

        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    split_comment = line.split("#")
                    # strip the whitespace and other chars
                    n = split_comment[0].strip()
                    if n == '':
                        continue
                    value = int(n, 2)
                    self.ram[address] = value
                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram_read(self.pc) # Instruction Register.
            op_count = IR >> 6
            ir_length = 1 + op_count
            self.branchtable[IR]()
            if IR == 0 or None:
                print(f"Unknown Instruction: {IR}")
                sys.exit()
            if IR != CALL and IR != RET and IR != JMP and IR != JEQ and IR != JNE:
                self.pc += ir_length