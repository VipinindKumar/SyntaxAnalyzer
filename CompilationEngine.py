import JackTokenizer

class CompilationEngine:
    """ Gets its input from JackTokenizer and 
        emits it parsed structure in output stream/file """
    
    def __init__(self, inFile, outFile):
        """ Creates a new CompilationEngine with given
            input and output. The next routine called must
            be compileClass() """
        
        # Create an object of JackTokenizer with the input file
        self.tokenizer = JackTokenizer.JackTokenizer(inFile)
        
        # Open a output file to write to
        self.out = open(outFile, 'w')
        
        self.currentToken = ''
        self.currentTokenType = ''
        self.tabs = 0
        
    
    def __charRef(self, sym):
        """ Change <, >, &, " to their respective
            character reference - &lt;, &gt;, &amp;, &quot; """
        
        if sym == '<':
            return '&lt;'
        elif sym == '>':
            return '&gt;'
        elif sym == '&':
            return '&amp;'
        elif sym == '"':
            return '&quot;'
        else:
            return sym
    
    def __advance(self):
        """ Advance the tokenizer and store the 
            token and it's respective type """
        
        if not self.tokenizer.hasMoreTokens():
            # error
            raise Exception('Unexpected end of file')
        else:
            self.tokenizer.advance()
            self.currentTokenType = self.tokenizer.tokenType()
            
            if self.currentTokenType == 'KEYWORD':
                self.currentToken = self.tokenizer.keyword()
            
            elif self.currentTokenType == 'SYMBOL':
                self.currentToken = self.tokenizer.symbol()
            
            elif self.currentTokenType == 'IDENTIFIER':
                self.currentToken = self.tokenizer.identifier()
            
            elif self.currentTokenType == 'INT_CONST':
                self.currentToken = self.tokenizer.intVal()
            
            elif self.currentTokenType == 'STRING_CONST':
                self.currentToken = self.tokenizer.stringVal()
    
    def __printTag(self):
        """ Print the currentToken as an appropriate tag in xml file
            using currentToken and currentTokenType """
        
        # Print the appropriate numbers of tabs, before the tag
        for i in range(self.tabs):
            self.out.write('\t')
        
        # Print the tag and its value in the xml file
        self.out.write('<' + self.currentTokenType + '> ' + self.currentToken + ' <' + self.currentTokenType + '>\n')
        
        self.__advance() # advance the tokenizer
    
    def __eat(self, string):
        """ Make sure the string equals the currentToken value
            and if it does it advances the tokenizer
            else an exception is thrown"""
        
        if self.currentToken != string:
            raise Exception('Expected ' + string + 'but found ' + self.currentToken)
        else:
            self.__printTag()
    
    def compileClass(self):
        """ Compiles a complete class """
        
        self.out.write('<class>\n') # Start <class> tag in output
        self.__eat('class') # check that there is class keyword as next token and output the fact
        
        self.__printTag() # Handles className identifier
        
        self.__eat('{') # '{'
        
        # 0 or more class variable declarations
        while self.currentToken not in ['constructor', 'method', 'function']:
            self.compileClassVarDec()
        
        # 0 or more subroutines
        while self.currentToken != '}':
            self.compileSubroutine()
        
        self.__eat('}') # '}'
        
        self.out.write('</class>')
    
    def compileClassVarDec(self):
        """ Compiles a static or a field declaration """
        
        
    
    def compileSubroutine(self):
        """ Compiles a complete method, function or constructor """
        
    
    def CompileParameterList(self):
        """ Compiles a parameter list(possibly empty) not including the enclosing () """
        
    
    def compileVarDec(self):
        """ compiles a variable declaration """
        
    
    def compileStatements(self):
        """ Compiles series of statements, without {} """
        
    
    def compileDo(self):
        """ Compiles a do statement """
        
    
    def compileLet(self):
        """ Compiles a Let statement """
        
    
    def compileWhile(self):
        """ Compiles a while statement """
        
    
    def compileReturn(self):
        """ Compiles a return statement """
        
    
    def compileIf(self):
        """ Compiles an If statement, possibly with a trailing else clause """
        
    
    def compileExpression(self):
        """ Compiles an expression """
        
    
    def compileTerm(self):
        """ Compiles a Term """
        
    
    def compileExpressionList(self):
        """ Compiles(possibly empty) comma separated list of expressions """
        
    