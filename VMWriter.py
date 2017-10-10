class VMWriter:
    """ Emits VM commands into a file, using the VM command syntax """
    
    def __init__(self, outfile):
        """ Creates a new file and prepare it for writing """
        
        
    
    def writePush(self, segment, index):
        """ Writes a VM push command
            segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP """
        
        
    
    def writePop(self, segment, index):
        """ Writes a VM pop command
            segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP """
        
        
    
    def writeArithmetic(self, command):
        """ Writes an Arithmetic command
            command: ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT """
        
        
    
    def writeLabel(self, label):
        """ Writes a VM label command """
        
        
    
    def writeGoto(self, label):
        """ Writes a VM goto command """
        
        
    
    def writeIf(self, label):
        """ Writes a VM If-goto command """
        
        
    
    def writeCall(self, name , nArgs):
        """ Writes a VM call command """
        
        
    
    def writefunction(self, name, nLocals):
        """ Writes a VM function command """
        
        
    
    def writeReturn(self):
        """ Writes a VM return command """
        
        
    
    def close(self):
        """ Close the file """
        
        
    