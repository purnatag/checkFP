def is_pure_functional_program(code):
    import ast
    try:
        tree = ast.parse(code)
    except ValueError:
        print("Parser returned error: Source contains a null character.")
        return False
    except:
        print("Parser returned unknown error.")
        return False
    
    # Implementing validation logic here
    class fpChecker(ast.NodeVisitor):
        def __init__(self):
            self.arglist = []
            #Allowing built-in functions that are not OOP-related
            self.funclist = ['abs', 'all', 'any', 'ascii', 'bin', 'bool', 'chr', 'complex', 'dict', 'divmod',
                             'float', 'format', 'hash', 'help', 'hex', 'input', 'int', 'isinstance', 'len',
                             'list', 'locals', 'max', 'min', 'oct', 'ord', 'pow', 'print', 'range', 'round',
                             'slice', 'sorted', 'str', 'tuple', 'type']
            self.undeffunc = []
            self.retval = True

        def is_input_immutable(self, node):
            #Make a list of function arguments/inputs

            for ip_arg in node.args.posonlyargs:
                self.arglist.append(ip_arg.arg)
            for ip_arg in node.args.args:
                self.arglist.append(ip_arg.arg)
            if isinstance(node.args.vararg, ast.arg): self.arglist.append(node.body[0].args.vararg.arg)
            for ip_arg in node.args.kwonlyargs:
                self.arglist.append(ip_arg.arg)
            if isinstance(node.args.kwarg, ast.arg): self.arglist.append(node.body[0].args.kwarg.arg)

            print("Arguments to current function", node.name, "are:", self.arglist)
            
            #Walk on the AST rooted at FunctionDef to check if inputs are being modified
            #Function inputs should not occur on the left side of assign statements i.e have ctx = Store()
            for bnode in ast.walk(node):
                if isinstance(bnode, ast.Name) and bnode.id in self.arglist and isinstance(bnode.ctx, ast.Store):
                    print("Function arguments cannot be modified.")
                    self.retval = False

            
        def limit_local_var_modification(self, node):
            loaddict = {}
            storedict = {}
            for lnode in ast.walk(node):
                #Every local variable can be assigned a value or an expression only once (store)
                #Every local variable should occur on the right side of an assign operator only once (load)
                if isinstance(lnode, ast.Name) and (lnode.id not in self.arglist):
                    print("Loading/Storing variable", lnode.id)
                    if isinstance(lnode.ctx, ast.Store):
                        if lnode.id in storedict:
                            storedict[lnode.id] += 1
                        else: 
                            storedict[lnode.id] = 1
                    if isinstance(lnode.ctx, ast.Load):
                        if lnode.id in loaddict:
                            loaddict[lnode.id] += 1
                        else:
                            loaddict[lnode.id] = 1
                
            #Remove function names from the load dictionary
            for lnode in ast.walk(node):
                if isinstance(lnode, ast.Call):
                    fn = lnode.func
                    if isinstance(fn, ast.Name) and fn.id in loaddict: del loaddict[fn.id]
                    if isinstance(fn, ast.Attribute):
                        fnval = fn.value
                        if isinstance(fnval, ast.Name) and fnval.id in loaddict: del loaddict[fnval.id]

            print("List of vars loaded:", loaddict)
            print("List of vars stored:", storedict)
            #Check for variables outside the function scope
            #No local variable will get loaded without getting stored first
            if self.retval == True:
                for lname in loaddict:
                    if lname not in list(storedict):
                        print("Function attempting to modify/call non-local/global variable", lname)
                        self.retval = False
                    elif loaddict[lname] > 1:
                        print("Variable used too many times")
                        self.retval = False

                for sname in storedict:
                    if storedict[sname] > 1:
                        print("Too many changes in variable value")
                        self.retval = False                 
        
        def check_global_nonlocal(self, node):
            #Checks for side effects of the function outside the input program
            for bnode in ast.walk(node):
                if isinstance(bnode, ast.Global) or isinstance(bnode, ast.Nonlocal): self.retval = False

        def visit_FunctionDef(self, node):
            self.funclist.append(node.name)
            if node.name in self.undeffunc: self.undeffunc.remove(node.name)
            self.is_input_immutable(node)
            self.check_global_nonlocal(node)
            self.limit_local_var_modification(node)
            #Reset the list of function args
            self.arglist = []
            self.generic_visit(node)

        #Functions called should be defined in the input program 
        def visit_Call(self, node):
            func = node.func
            if isinstance(func, ast.Name) and func.id not in self.funclist: 
                self.undeffunc.append(func.id)
            self.generic_visit(node)
       
        #Disallowing defining of classes and their instantiation (only Objects have Attribute)       
        def visit_ClassDef(self, node):
            print("Program contains definition of class", node.name, " not permitted.")
            self.retval = False
            self.generic_visit(node)

        def visit_Attribute(self, node):
            allowList = ['math', 'string', 'list', 'tuple', 'dict']
            nval = node.value
            if isinstance(nval, ast.Name) and nval.id not in allowList:
                print("Attribute of Object", nval.id, " referred to, not permitted.") 
                self.retval = False
            self.generic_visit(node)

        #Disallowing For Loop
        def visit_For(self, node):
            print("Program contains for Loop, not permitted.")
            self.retval = False
            self.generic_visit(node)
        
        #Disallowing While Loop
        def visit_While(self, node):
            print("Program contains while Loop, not permitted.")
            self.retval = False
            self.generic_visit(node)

        #Disallowing imports and from x import y
        def visit_Import(self, node):
            print("Program contains import statement, not permitted.")
            self.retval = False
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            print("Program contains 'from x import y' statement, not permitted.")
            self.retval = False
            self.generic_visit(node)

        def report(self):
            if len(self.undeffunc) > 0:
                print("Program called functions not defined inside it, not permitted.")
                self.retval = False
            return self.retval
        
    checkfp = fpChecker()
    checkfp.visit(tree)
    report = checkfp.report()
    return report
    #return True or False