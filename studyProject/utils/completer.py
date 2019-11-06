from IPython.core.completer import IPCompleter

class CompleterStudy2(IPCompleter):
    use_jedi=False
    def _complete(self, *, cursor_line, cursor_pos, line_buffer=None, text=None,
                  full_text=None):
        from IPython.core.completer import DELIMS
        self.splitter.delims = ' \t\n!@#$\\|;:\<>?'
        rep=super()._complete( cursor_line=cursor_line, cursor_pos=cursor_pos, line_buffer=line_buffer, text=text,
                  full_text=full_text)
        self.splitter.delims = DELIMS
        if len(rep)==0:
            rep=super()._complete( cursor_line=cursor_line, cursor_pos=cursor_pos, line_buffer=line_buffer, text=text,
                  full_text=full_text)
        return rep
from IPython.core.completer import IPCompleter
from IPython.core.completer import DELIMS
import re
class CompleterStudy(IPCompleter):
    use_jedi=False
    def allez(self,text):
        s=self.text_until_cursor
        def ooo(s,k=2):
            import re
            regexp =  re.compile(r'''
                        '.*?(?<!\\)' |    # single quoted strings or
                        ".*?(?<!\\)" |    # double quoted strings or
                        \w+          |    # identifier
                        \S           |     # other characters
                        \s+
                        ''', re.VERBOSE | re.DOTALL)
            e=regexp.findall(s)[::-1]
            par_op=0
            ph=e
            for i_,j in enumerate(e):
                if j == "(":
                    par_op+=1
                    if par_op==k:
                        return "".join(ph[:(i_)][::-1])
                elif j == ')':
                    par_op-=1
            return s if par_op+1==k else False 

        def ooi(s):
            e=ooo(s)
            if e:
                #print(e)
                e2=ooo(e,1)
                pattern = r'\(.*\)|\[.*\]|\{.*\}|\=\='
                e3=re.sub(pattern, '', e2)
                e3=[i.split("=") for i in e3.split(",")]
                e3=[i[0] for i in e3 if len(i)>1 ]
                fs=e[::-1][(len(e2)+1):][::-1]

                fs2=re.sub(pattern, '', fs)
                fs2=[i[0] for i in [fs2.split("=")] if len(i)>1 ]
                if len(fs2) >0:
                    fs3=fs[(len(fs2[0])+1):]
                else:
                    fs3=fs
                return [fs3,e3]
            return False
        argMatches = []
        try:
            oo=ooi(s)
            if oo == False:
                raise Exception("pb o")
            
            callableObj,usedNamedArgs=oo
            #print(oo,file=open("/home/devel/work/oo3.txt","a"))
            
            namedArgs = self._default_arguments(eval(callableObj,
                                                    self.namespace))

            # Remove used named arguments from the list, no need to show twice
            for namedArg in set(namedArgs) - set(usedNamedArgs):
                if namedArg.startswith(text):
                    argMatches.append(u"%s=" %namedArg)
        except Exception as e:
            pass

        return argMatches
    def ooo(self,s,k=2):
        import re
        regexp =  re.compile(r'''
                    '.*?(?<!\\)' |    # single quoted strings or
                    ".*?(?<!\\)" |    # double quoted strings or
                    \w+          |    # identifier
                    \S           |     # other characters
                    \s+
                    ''', re.VERBOSE | re.DOTALL)
        e=regexp.findall(s)[::-1]
        par_op=0
        ph=e
        for i_,j in enumerate(e):
            if j == "(":
                par_op+=1
                if par_op==k:
                    return "".join(ph[:(i_)][::-1])
            elif j == ')':
                par_op-=1
        return s if par_op+1==k else False 
    
    def _complete(self, *, cursor_line, cursor_pos, line_buffer=None, text=None,
                      full_text=None):
        #print(dict(cursor_line=cursor_line, cursor_pos=cursor_pos, line_buffer=line_buffer, text=text,
        #             full_text=full_text),file=open("/home/devel/work/oo3.txt","a"))
        #return super()._complete( cursor_line=cursor_line, cursor_pos=cursor_pos, line_buffer=line_buffer, text=text,
        #      full_text=full_text)
        #print("FAKE_DELIM",file=open("/home/devel/work/oo.txt","a"))
        self.use_jedi=True
        self.splitter.delims = ' \t\n!@#$\\|;:\<>?'
        rep=super()._complete( cursor_line=cursor_line, cursor_pos=cursor_pos, line_buffer=line_buffer, text=text,
          full_text=full_text)
        #print(rep,file=open("/home/devel/work/oo3.txt","a"))
        self.splitter.delims = DELIMS
        #print(rep,file=open("/home/devel/work/oo3.txt","a"))
        if len(rep[1])==0:
            self.use_jedi=False
            rep=super()._complete( cursor_line=cursor_line, cursor_pos=cursor_pos, line_buffer=line_buffer, text=text,
                                  full_text=full_text)
            if len(rep[1])==0:
                self.use_jedi=True
                #print("TRUE_DELIM",file=open("/home/devel/work/oo3.txt","a"))
                rep=super()._complete( cursor_line=cursor_line, cursor_pos=cursor_pos, line_buffer=line_buffer, text=text,
                  full_text=full_text)
                #print(rep,file=open("/home/devel/work/oo3.txt","a"))
                if len(rep[1])==0:
                    self.splitter.delims = ' \t\n!@#$\\|;:\<>?'
                    rep=super()._complete( cursor_line=cursor_line, cursor_pos=cursor_pos, line_buffer=line_buffer, text=text,
                                      full_text=full_text)
                    self.splitter.delims = DELIMS
                #self.use_jedi=False
            #print(rep,file=open("/home/devel/work/oo3.txt","a"))
        return rep
    
    def python_func_kw_matches(self,text):
        #print(dict(p=text,tex=self.text_until_cursor),file=open("/home/devel/work/oo3.txt","a"))
        rep=self.allez(text)
        #print("pp",rep,len(rep),file=open("/home/devel/work/oo3.txt","a"))
        if len(rep) == 0:
            return super().python_func_kw_matches(text)
        return rep

    def attr_matches(self, text):
        #print(dict(p=text),file=open("/home/devel/work/oo3.txt","a"))
        d=self.ooo(self.text_until_cursor,1)
        
        m = re.match(r"(\S+(\.\w+)*)\.(\w*)$", d)
        if m:
            expr, attr = m.group(1, 3)
        elif self.greedy:
            m2 = re.match(r"(.+)\.(\w*)$", self.line_buffer)
            if not m2:
                return super().attr_matches(text)
            expr, attr = m2.group(1,2)
        
        rep=super().attr_matches(d)
        #print(rep,text,self.text_until_cursor,expr,rep[0],file=open("/home/devel/work/oo3.txt","a"))
        rep= [i[(len(expr)):] for i in rep] if self.text_until_cursor!=text else rep
        if len(rep)==0:
            rep=super().attr_matches(text)
        return rep
   
   
   
def createSubClass(name,papas,met):
    return type(name,papas,met)  
def createSubClassFromIPCompleter(met,name="blabla"):
    d=IPCompleter.__dict__.copy()
    d.update(met)
    d["__module__"]=None
    d["__name__"]=name
    return createSubClass(name,(IPCompleter,),d)
def returnCom(self,cls=CompleterStudy):
    return cls(shell=self,
                 namespace=self.user_ns,
                 global_namespace=self.user_global_ns,
                 parent=self,
                 )
original=None
import warnings
def config_completer(force=False,origin=False,ipy=lambda: get_ipython(),cls=CompleterStudy):
    global original
    ipy=ipy()
    na=cls.__name__
    n=ipy.Completer.__class__.__name__
    if origin:
        rep=ipy.Completer if original is None else original
        ipy.Completer = rep
    if n == na and not force:
        warnings.warn(
            "Must set force=True to recreate a CompleterStudy"
            )
    elif ( n == na and force ) or (n != na):
        if n!=na:
            original=ipy.Completer
        ipy.Completer = returnCom(ipy,cls)