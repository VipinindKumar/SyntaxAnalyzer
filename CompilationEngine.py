import JackTokenizer
import SymbolTable
import VMWriter


class CompilationEngine:
    """ Gets its input from JackTokenizer and
        emits it parsed structure in output stream/file """

    op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    unaryOp = ['-', '~']
    keywordConstant = ['true', 'false', 'null', 'this']

    def __init__(self, inFile, outFile):
        """ Creates a new CompilationEngine with given
            input and output. The next routine called must
            be compileClass() """

        # Create an object of JackTokenizer with the input file
        self.tokenizer = JackTokenizer.JackTokenizer(inFile)

        # Create an object of SymbolTable
        self.symbolTable = SymbolTable.SymbolTable()

        # Create an object of VMWriter
        self.vmWriter = VMWriter.VMWriter(outFile[:-3] + 'vm')

        # Open a output file to write to
        self.out = open(outFile, 'w')

        self.currentToken = ''
        self.currentTokenType = ''
        self.tabs = 0
        self.i = 0  # for creating unique labels
        self.nfield = 0
        self.nstatic = 0

        self.__advance()

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
            self.currentToken = ''
            self.currentTokentype = ''
        else:
            self.tokenizer.advance()
            self.currentTokenType = self.tokenizer.tokenType()

            if self.currentTokenType == 'KEYWORD':
                self.currentToken = self.tokenizer.keyword()
                self.currentTokenType = 'keyword'

            elif self.currentTokenType == 'SYMBOL':
                self.currentToken = self.tokenizer.symbol()
                self.currentTokenType = 'symbol'

            elif self.currentTokenType == 'IDENTIFIER':
                self.currentToken = self.tokenizer.identifier()
                self.currentTokenType = 'identifier'

            elif self.currentTokenType == 'INT_CONST':
                self.currentToken = self.tokenizer.intVal()
                self.currentTokenType = 'integerConstant'

            elif self.currentTokenType == 'STRING_CONST':
                self.currentToken = self.tokenizer.stringVal()
                self.currentTokenType = 'stringConstant'

    def __printTabs(self):
        """ Print the appropriate numbers of tabs(two spaces), before the tag """
        for i in range(self.tabs):
            self.out.write('  ')

    def __printTag(self):
        """ Print the currentToken as an appropriate tag in xml file
            using currentToken and currentTokenType """

        self.__printTabs()

        # Print the tag and its value in the xml file
        self.out.write('<' + self.currentTokenType + '> ' + self.currentToken + ' </' + self.currentTokenType + '>\n')

        self.__advance()  # advance the tokenizer

    def __eat(self, stringList):
        """ Make sure the string equals the currentToken value
            and if it does it advances the tokenizer
            else an exception is thrown"""

        if self.currentToken not in stringList:
            raise Exception('Expected ' + str(stringList) + ' but found ' + self.currentToken)
        else:
            self.__printTag()

    def __printIdentifier(self, name, mode=''):
        """ print the variable with all its components
            and advance the tokenizer """

        if mode == 'DEC':
            self.currentTokenType = 'identifierDeclaration'
        else:
            self.currentTokenType = 'identifierUse'

        # x, int, VAR, 0
        self.currentToken = name + ' -> (' + self.symbolTable.typeOf(name) + ', ' + self.symbolTable.kindOf(
            name) + ', ' + self.symbolTable.indexOf(name) + ')'

        self.__printTag()

    def __varDec(self, kind):
        """ Compilea part of class variable declaration and
            variable declaration
            : type varName (',' varName)* ';' """

        # Store the type of variable
        vartype = self.currentToken

        # number of variable declaration
        nvar = 0

        # type: int | char | boolean | className
        # can just use self.__printTag()
        try:
            self.__eat(['int', 'char', 'boolean'])
        except:
            self.__printTag()

        # Store the name of the variable
        name = self.currentToken

        # Store the complete variable definition in the symbolTable
        self.symbolTable.define(name, vartype, kind.upper())
        nvar += 1

        # self.__printTag() # varName identifier
        self.__printIdentifier(name, 'DEC')

        # (',' varName)*
        while self.currentToken != ';':
            self.__eat([','])
            # Store the name of the variable
            name = self.currentToken
            # Store the complete variable definition in the symbolTable
            self.symbolTable.define(name, vartype, kind.upper())
            nvar += 1

            # self.__printTag() # varName identifier
            self.__printIdentifier(name, 'DEC')

        self.__eat([';'])  # ';'

        return nvar

    def compileClass(self):
        """ Compiles a complete class
            Class: 'class' className '{' classVarDec* subroutineDec* '}' """

        self.__printTabs()
        self.out.write('<class>\n')  # Start <class> tag in output
        self.tabs += 1  # Add single Indentation to xml file tags from here

        self.__eat(['class'])  # check that there is class keyword as next token and output the fact

        self.className = self.currentToken  # Saves the name of the current class

        self.__printTag()  # Handles className identifier
        self.__eat(['{'])  # '{'

        # 0 or more class variable declarations
        while self.currentToken not in ['constructor', 'method', 'function']:
            self.compileClassVarDec()

        # 0 or more subroutines
        while self.currentToken != '}':
            self.compileSubroutine()

        self.__eat(['}'])  # '}'

        self.tabs -= 1  # Remove single indentation from the tags
        self.__printTabs()
        self.out.write('</class>\n')
        self.out.close()

    def compileClassVarDec(self):
        """ Compiles a static or a field declaration
            ClassVarDec: ('static' | 'field') type varName (',' varName)* ';' """

        self.__printTabs()
        self.out.write('<classVarDec>\n')

        self.tabs += 1  # increase indentation

        # Store the kind of variable being declared
        kind = self.currentToken

        self.__eat(['static', 'field'])  # (static | field)

        if kind == 'static':
            self.nstatic += self.__varDec(kind)  # type varName (',' varName)* ';'
        else:
            self.nfield += self.__varDec(kind)  # type varName (',' varName)* ';'

        # Remove single indentation from the tags
        self.tabs -= 1

        self.__printTabs()
        self.out.write('</classVarDec>\n')

    def compileSubroutine(self):
        """ Compiles a complete method, function or constructor
            Subroutine: ('constructor' | 'method' | 'function')
                        ('void' | type) subroutineName '(' parameterList ')'
                        subroutineBody """

        self.__printTabs()
        self.out.write('<subroutineDec>\n')
        self.tabs += 1  # increase indentation

        # Start the subroutine variable declarations
        self.symbolTable.startSubroutine()

        # store the type of subroutine
        subroutine = self.currentToken

        self.__eat(['constructor', 'function', 'method'])  # constructor | function | method

        # void | type: int | char | boolean | className
        # can just use self.__printTag()
        try:
            self.__eat(['void', 'int', 'char', 'boolean'])
        except:
            self.__printTag()

        subroutineName = self.currentToken

        self.__printTag()  # subroutineName identifier

        self.__eat(['('])  # '('

        self.compileParameterList()

        self.__eat([')'])  # ')'

        # subroutineBody
        # subroutineBody: '{' (varDec)* statements '}'

        self.__printTabs()
        self.out.write('<subroutineBody>\n')
        self.tabs += 1  # increase indentation

        self.__eat(['{'])

        nLocals = 0
        # (varDec)*
        while self.currentToken not in ['let', 'if', 'do', 'while', 'return']:
            nLocals += self.compileVarDec()

        # write the function statement
        self.vmWriter.writeFunction(self.className + '.' + subroutineName, nLocals)

        # Add 'this' as 'argument 0' in symbolTable in case of a method
        if subroutine == 'method':
            self.symbolTable.define('this', self.className, 'ARG')

            # push the argument 0 and then pop it in pointer 0
            self.vmWriter.writePush('ARG', 0)
            self.vmWriter.writePop('POINTER', 0)

        elif subroutine == 'constructor':
            # push the number of parameters to stack and allocate the memory
            self.vmWriter.writePush('CONST', self.nfield)
            self.vmWriter.writeCall('Memory.alloc', 1)

            # and pop it in 'THIS' by pointer 0
            self.vmWriter.writePop('POINTER', 0)

        # statements
        self.compileStatements()

        self.__eat(['}'])

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</subroutineBody>\n')

        # Remove single indentation from the tags
        self.tabs -= 1
        self.__printTabs()
        self.out.write('</subroutineDec>\n')

    def compileParameterList(self):
        """ Compiles a parameter list(possibly empty) not including the enclosing ()
            ParameterList: ((type varName) (',' type varName)*)? """

        self.__printTabs()
        self.out.write('<parameterList>\n')
        self.tabs += 1  # add indentation

        if self.currentToken != ')':

            # type: int | char | boolean | className
            vartype = self.currentToken
            try:
                self.__eat(['int', 'char', 'boolean'])
            except:
                self.__printTag()

            name = self.currentToken
            # add the vaariable into the symbolTable
            self.symbolTable.define(name, vartype, 'ARG')

            # self.__printTag() # varName identifier
            self.__printIdentifier(name, 'DEC')

            while self.currentToken != ')':
                self.__eat([','])
                # type: int | char | boolean | className
                vartype = self.currentToken
                try:
                    self.__eat(['int', 'char', 'boolean'])
                except:
                    self.__printTag()

                name = self.currentToken
                # add the vaariable into the symbolTable
                self.symbolTable.define(name, vartype, 'ARG')

                # self.__printTag() # varName identifier
                self.__printIdentifier(name, 'DEC')

        self.tabs -= 1  # remove indentation
        self.__printTabs()
        self.out.write('</parameterList>\n')

    def compileVarDec(self):
        """ compiles a variable declaration
            varDec: var type varName (',' varName)* ';' """

        self.__printTabs()
        self.out.write('<varDec>\n')
        self.tabs += 1  # increase indentation

        self.__eat(['var'])  # var

        nLocals = self.__varDec('VAR')  # type varName (',' varName)* ';'

        # Remove single indentation from the tags
        self.tabs -= 1
        self.__printTabs()
        self.out.write('</varDec>\n')

        return nLocals

    def compileStatements(self):
        """ Compiles series of statements, without {}
            statements: statement*
            statement: letStatement | doStatement | ifStatement |
                       whileStatement | returnStatement """

        self.__printTabs()
        self.out.write('<statements>\n')
        self.tabs += 1

        while True:
            if self.currentToken == 'do':
                self.compileDo()
            elif self.currentToken == 'let':
                self.compileLet()
            elif self.currentToken == 'while':
                self.compileWhile()
            elif self.currentToken == 'return':
                self.compileReturn()
            elif self.currentToken == 'if':
                self.compileIf()
            else:
                break

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</statements>\n')

    def __subroutineCall(self):
        """ Compiles the subroutine call part of the program
            SubroutineCall: subroutineName '(' expressionList ')' | (className | varName) '.'
                            subroutineName '(' expressionList ')' """

        className = ''
        name = ''
        # subroutineName | (className | varName)
        # if varName
        method = False
        varkind = self.symbolTable.kindOf(self.currentToken)
        varindex = self.symbolTable.indexOf(self.currentToken)
        if varkind != 'NONE':
            # push the variable on the stack before the call command
            self.vmWriter.writePush(varkind, varindex)

            method = True

            # Save the name of the class variable is refering to
            className = self.symbolTable.typeOf(self.currentToken)

            self.__printIdentifier(self.currentToken)
        
        # if className or subroutineName
        else:
            name = self.currentToken
            self.__printTag()

        if self.currentToken == '.':
            # in the case of '.', it should be className.name(expressionList)
            # set className to name, only run if it's a class
            if name:
                className = name

            self.__eat(['.'])

            name = self.currentToken
            self.__printTag()  # subroutineName
        # run only for 'subroutineName'
        else:
            # push the variable on the stack before the call command
            self.vmWriter.writePush('POINTER', 0)

            method = True

        self.__eat(['('])  # '('
        nArgs = self.compileExpressionList()
        self.__eat([')'])  # ')'

        # build the name of the function to call, if className.name(expressionList)
        if className:
            name = className + '.' + name
        # else add the current className in front of the subroutineName
        else:
            name = self.className + '.' + name

        # if calling a method add one to the nArgs
        if method:
            nArgs += 1

        # Write call vm command
        self.vmWriter.writeCall(name, nArgs)

        # Dump the returned value residing at the top of stack, in case of a 'do' statement
        self.vmWriter.writePop('TEMP', 0)

    def compileDo(self):
        """ Compiles a do statement
            doStatment: 'do' subroutineCall ';' """

        self.__printTabs()
        self.out.write('<doStatement>\n')
        self.tabs += 1

        self.__eat(['do'])

        # subrutineCall
        self.__subroutineCall()

        self.__eat([';'])  # ';'

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</doStatement>\n')

    def compileLet(self):
        """ Compiles a Let statement
        LetStatement: 'let' varName ('[' expression ']')? '=' expression ';' """

        self.__printTabs()
        self.out.write('<letStatement>\n')
        self.tabs += 1

        self.__eat(['let'])

        # store the varialbe
        variable = self.currentToken
        self.__printTag()

        # if it's an array
        if self.currentToken == '[':
            self.__eat(['['])
            
            # When it is an array
            # 1.) push the variable
            self.vmWriter.writePush(self.symbolTable.kindOf(variable), self.symbolTable.indexOf(variable))
            
            # 2.) compute and push the value of expresssion
            self.compileExpression()
            
            # 3.) add
            self.vmWriter.writeArithmetic('ADD')
            
            self.__eat([']'])
            self.__eat(['='])
            
            # 4.) computer and push the value of expression
            self.compileExpression()
            
            # 5.) pop the value of last expression in temp
            self.vmWriter.writePop('TEMP', 0)
            
            # 6.) set THAT to the array location from value before '='
            self.vmWriter.writePop('POINTER', 1)
            
            # 7.) Now push the value saved in the temp onto the stack
            self.vmWriter.writePush('TEMP', 0)
            
            # 8.) Put the value in the array location in THAT
            self.vmWriter.writePop('THAT', 0)
        
        else:
            self.__eat(['='])
            
            self.compileExpression()
            
            # after compiling expression value, pop the value into the variable
            self.vmWriter.writePop(self.symbolTable.kindOf(variable), self.symbolTable.indexOf(variable))
        
        self.__eat([';'])
        
        self.tabs -= 1
        self.__printTabs()
        self.out.write('</letStatement>\n')

    def compileWhile(self):
        """ Compiles a while statement
            whileStatement: 'while' '(' expression ')' '{' statements '}' """

        self.__printTabs()
        self.out.write('<whileStatement>\n')
        self.tabs += 1

        self.__eat(['while'])
        self.__eat(['('])

        # write a Label before compiling the expression 'L0'
        L0 = 'L' + str(self.i)
        self.vmWriter.writeLabel(L0)
        self.i += 1

        self.compileExpression()

        # negate the expression above, and if true jump to the label at the end 'L1'
        self.vmWriter.writeArithmetic('NOT')
        L1 = 'L' + str(self.i)
        self.vmWriter.writeIf(L1)
        self.i += 1

        self.__eat([')'])
        self.__eat(['{'])

        self.compileStatements()

        # after compiled statements create a goto statement to the expression at the start 'L0'
        self.vmWriter.writeGoto(L0)

        # write the label for the end 'L1'
        self.vmWriter.writeLabel(L1)

        self.__eat(['}'])

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</whileStatement>\n')

    def compileReturn(self):
        """ Compiles a return statement
            ReturnStatement: 'return' (expression)? ';' """

        self.__printTabs()
        self.out.write('<returnStatement>\n')
        self.tabs += 1

        self.__eat(['return'])

        if self.currentToken != ';':
            self.compileExpression()

            # Write Return VM command
            self.vmWriter.writeReturn()
        else:
            # if there is no expression to return, push a dummy value to the stack
            self.vmWriter.writePush('CONST', 0)

            # Write Return VM command
            self.vmWriter.writeReturn()

        self.__eat([';'])

        # !!! add a dump value before returning

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</returnStatement>\n')

    def compileIf(self):
        """ Compiles an If statement, possibly with a trailing else clause
            IfStatements: 'if' '(' expression ')' '{' statements '}'
                          ('else' '{' statements '}')? """

        self.__printTabs()
        self.out.write('<ifStatement>\n')
        self.tabs += 1

        self.__eat(['if'])
        self.__eat(['('])

        self.compileExpression()

        # negate the expression and then write an if-goto statement 'L0' to the else statements
        self.vmWriter.writeArithmetic('NOT')
        L0 = 'L' + str(self.i)
        self.vmWriter.writeIf(L0)
        self.i += 1

        self.__eat([')'])
        self.__eat(['{'])

        self.compileStatements()

        # after compiling statements, write a goto statement to 'L1' the end of conditional
        L1 = 'L' + str(self.i)
        self.vmWriter.writeGoto(L1)
        self.i += 1

        self.__eat(['}'])

        # Add the label to represent end of if and start of else is any 'L0'
        self.vmWriter.writeLabel(L0)

        if self.currentToken == 'else':
            self.__eat(['else'])
            self.__eat(['{'])

            self.compileStatements()

            self.__eat(['}'])

        # Add a label to represent end of the whole if-else consitional 'L1'
        self.vmWriter.writeLabel(L1)

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</ifStatement>\n')

    def compileExpression(self):
        """ Compiles an expression
            expression: term (op term)* """

        self.__printTabs()
        self.out.write('<expression>\n')
        self.tabs += 1

        self.compileTerm()

        while self.currentToken in self.op:
            # Push the operation after compiling both expressions
            op = self.currentToken

            self.__eat(self.op)
            self.compileTerm()

            # Write code for handling different operations
            # op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
            if op == '+':
                self.vmWriter.writeArithmetic('ADD')
            elif op == '-':
                self.vmWriter.writeArithmetic('SUB')
            elif op == '*':
                self.vmWriter.writeCall('Math.multiply', 2)
            elif op == '/':
                self.vmWriter.writeCall('Math.divide', 2)
            elif op == '&':
                self.vmWriter.writeArithmetic('AND')
            elif op == '|':
                self.vmWriter.writeArithmetic('OR')
            elif op == '<':
                self.vmWriter.writeArithmetic('LT')
            elif op == '>':
                self.vmWriter.writeArithmetic('GT')
            elif op == '=':
                self.vmWriter.writeArithmetic('EQ')
            else:
                raise ValueError('Wrong operation is used')

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</expression>\n')

    def compileTerm(self):
        """ Compiles a Term
            Term: integerConstant | StringConstant | keywordConstant |
                  varName | varName '[' expression ']' | subroutineCall |
                  '(' expression ')' | unaryOp term """

        self.__printTabs()
        self.tabs += 1
        self.out.write('<term>\n')

        # integerConstant
        if self.currentTokenType == 'integerConstant':
            # Push the integer constant
            self.vmWriter.writePush('CONST', int(self.currentToken))

            self.__printTag()

        # StringConstant
        elif self.currentTokenType == 'stringConstant':
            # Create the string constant using VM commands
            string = self.currentToken
            length = len(string)
            
            # VM commands to create a new string object of length
            self.vmWriter.writePush('CONST', length)
            self.vmWriter.writeCall('String.new', 1)
            
            # Create the stringConstant using series of call to String.append('c')
            for i in range(length):
                # push the character ascii value, 32-126 only
                self.vmWriter.writePush('CONST', ord(string[i]))
                self.vmWriter.writeCall('String.appendChar', 2)
            
            self.__printTag()

        # keywordConstant
        elif self.currentToken in self.keywordConstant:
            if self.currentToken in ['null', 'false']:
                self.vmWriter.writePush('CONST', 0)
                self.__printTag()
            elif self.currentToken == 'true':
                self.vmWriter.writePush('CONST', 1)
                self.vmWriter.writeArithmetic('NEG')
                self.__printTag()
            else:  # 'this'
                self.vmWriter.writePush('POINTER', 0)
                self.__printTag()

        # unaryOp term
        elif self.currentToken in self.unaryOp:
            unaryOp = self.currentToken

            self.__eat(self.unaryOp)
            self.compileTerm()

            # Push the unary operation, after compiling the term
            if unaryOp == '-':
                self.vmWriter.writeArithmetic('NEG')
            else:
                self.vmWriter.writeArithmetic('NOT')  # '~'

        # '(' expression ')'
        elif self.currentToken == '(':
            self.__eat(['('])
            self.compileExpression()
            self.__eat([')'])

        else:
            # varName | varName '[' expression ']' |
            # subroutineCall: subroutineName '(' expressionList ')' |
            #                (className | varName) '.' subroutineName '(' expressionList ')'

            name = self.currentToken
            method = False
            # varName
            varkind = self.symbolTable.kindOf(self.currentToken)
            varindex = self.symbolTable.indexOf(self.currentToken)
            if varkind != 'NONE':
                # push the variable value on to the stack
                self.vmWriter.writePush(varkind, varindex)
                
                # change name of the variable to its type ie. className
                name = self.symbolTable.typeOf(self.currentToken)
                
                method = True
                self.__printIdentifier(self.currentToken)
            # subroutineName | className
            else:
                self.__printTag()

            if self.currentToken == '[':  # varName '[' expression ']'
                self.__eat(['['])
                
                # when it is an array call
                # 1.) variable is already on the stack
                # 2.) push the expression
                self.compileExpression()
                
                # 3.) add
                self.vmWriter.writeArithmetic('ADD')
                
                # to retrieve the value
                # 4.) make THAT to point to array location
                self.vmWriter.writePop('POINTER', 1)
                
                # 5.) push the value at the location to stack
                self.vmWriter.writePush('THAT', 0)
                
                self.__eat([']'])

            elif self.currentToken == '(':  # subroutineName '(' expressionList ')'
                self.__eat(['('])
                nArgs = self.compileExpressionList()
                # call the subroutine
                self.vmWriter.writeCall(self.className + '.' + name, nArgs)
                self.__eat([')'])

            elif self.currentToken == '.':  # (className | varName) '.' subroutineName '(' expressionList ')'
                self.__eat(['.'])

                # Create the full call subroutine name with its className append at front
                name = name + '.' + self.currentToken

                self.__printTag()
                self.__eat(['('])
                nArgs = self.compileExpressionList()
                
                # add 1 to nArgs if method is True
                if method:
                    nArgs += 1
                
                # add call command after pushing all the parameters to stack
                self.vmWriter.writeCall(name, nArgs)

                self.__eat([')'])

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</term>\n')

    def compileExpressionList(self):
        """ Compiles(possibly empty) comma separated list of expressions
            ExpressionList: (expression (',' expression)* )? """

        self.__printTabs()
        self.out.write('<expressionList>\n')
        self.tabs += 1

        nArgs = 0
        if self.currentToken != ')':
            self.compileExpression()
            nArgs += 1

            while self.currentToken == ',':
                self.__eat([','])
                self.compileExpression()
                nArgs += 1

        self.tabs -= 1
        self.__printTabs()
        self.out.write('</expressionList>\n')

        return nArgs