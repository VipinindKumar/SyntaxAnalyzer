class VMWriter:
    """ Emits VM commands into a file, using the VM command syntax """

    def __init__(self, outFile):
        """ Creates a new file and prepare it for writing """

        # Open a output file to write to
        self.out = open(outFile, 'w')

    def writePush(self, segment, index):
        """ Writes a VM push command
            segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP """

        if segment == 'CONST':
            segment = 'constant'
        elif segment == 'ARG':
            segment = 'argument'
        elif segment == 'VAR':
            segment = 'local'
        elif segment == 'FIELD':
            segment = 'this'
        else:
            segment = segment.lower()

        self.out.write('push ' + segment + ' ' + str(index) + '\n')

    def writePop(self, segment, index):
        """ Writes a VM pop command
            segment: CONST, ARG, VAR, STATIC, THIS, THAT, POINTER, TEMP """

        if segment == 'CONST':
            segment = 'constant'
        elif segment == 'ARG':
            segment = 'argument'
        elif segment == 'VAR':
            segment = 'local'
        elif segment == 'FIELD':
            segment = 'this'
        else:
            segment = segment.lower()

        self.out.write('pop ' + segment + ' ' + str(index) + '\n')

    def writeArithmetic(self, command):
        """ Writes an Arithmetic command
            command: ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT """

        self.out.write(command.lower() + '\n')

    def writeLabel(self, label):
        """ Writes a VM label command """

        self.out.write('label ' + label.upper() + '\n')

    def writeGoto(self, label):
        """ Writes a VM goto command """

        self.out.write('goto ' + label.upper() + '\n')

    def writeIf(self, label):
        """ Writes a VM If-goto command """

        self.out.write('if-goto ' + label.upper() + '\n')

    def writeCall(self, name, nArgs):
        """ Writes a VM call command """

        self.out.write('call ' + name + ' ' + str(nArgs) + '\n')

    def writeFunction(self, name, nLocals):
        """ Writes a VM function command """

        self.out.write('function ' + name + ' ' + str(nLocals) + '\n')

    def writeReturn(self):
        """ Writes a VM return command """

        self.out.write('return' + '\n')

    def close(self):
        """ Close the file """

        self.out.close()