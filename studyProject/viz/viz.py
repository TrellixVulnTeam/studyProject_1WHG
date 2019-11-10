import cufflinks as cf
# import plotly_express as pe
# cf.go_offline(connected=False)

from interface import Interface
from ..utils import get_args, isinstanceBase, isinstance

class Viz:
    def __init__(self,obj):
        self.obj=obj

import functools

def catch_exception_viz(f,obj,names,kw="me"):
    @functools.wraps(f)
    def func(*args, **kwargs):
        # print(names)
        try:
            if kw in names:
                kwargs[kw]=obj
            return f(*args, **kwargs)
        except Exception as e:
            try:
                return f(*args, **kwargs)
            except Exception as e2:
                print(str(e))
                print(str(e2))
                raise e
    return func

def vizGet(o):
    return o.__curr if o.__class__.__name__ == "vizHelper"  else o
def catch_exception_viz2(f,obj,names,kw="me"):
    @functools.wraps(f)
    def func(*args, **kwargs):
        # print(names)
        try:
            if kw in names:
                kwargs[kw]=obj
            if "_obj" in kwargs and kwargs["_obj"]:
                del kwargs["_obj"]
                return f(*args, **kwargs)
            # if "vh" in args and args["vh"]:
            return vizHelper(obj,f(*args, **kwargs),realNone=True)
            # return f(*args, **kwargs)
        except Exception as e:
            try:
                return f(*args, **kwargs)
            except Exception as e2:
                print(str(e))
                print(str(e2))
                raise e
    return func
# class vizHelperMeta(type):
#     def __instancecheck__(self, other):
#         return isinstance(self.__curr,typ)
import copy
class vizHelper(object):
    def __init__(self, arg, curr=None, realNone=False):
        self.__obj = arg
        self.__curr = (None if realNone else arg) if curr is None else curr 

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        # cls = self.__class__
        # result = cls.__new__(cls)
        # memo[id(self)] = result
        # for k, v in self.__dict__.items():
        #     setattr(result, k, copy.deepcopy(v, memo))
        return self

    def __getstate__(self):
        return dict(obj=self.__obj,
                    curr=self.__curr)

    def __setstate__(self,i):
        self.__obj=i["__obj"]
        self.__curr=i["__curr"]

    def __meme(self,rep):
        # print(callable(rep))
        # print(type(rep).__name__)
        # print(callable(rep) and (type(rep).__name__ in ["function","method"]))
        if callable(rep) and (type(rep).__name__ in ["function","method","builtin_function_or_method"]) :
            ng=get_args(rep).names
            # print(ng)
            if "me" not in ng:
                # print("withNotME")
                return catch_exception_viz2(rep,self.__obj,ng)
            # print("withME")
            return catch_exception_viz(rep,self.__obj,ng)
        return vizHelper(self.__obj,rep)

    def __getattr__(self,k):
        # print("getattr")
        if k=="_vizHelper__obj" or k=="_vizHelper__curr" or k=="_vizHelper__meme":
            k=k[len("_vizHelper"):]
        # print(k)
        if k.startswith('___') and k.endswith('___'):
            return self.__meme(getattr(self.__curr,k))

        if k.startswith('__') and k.endswith('__'):
            return getattr(self,k)

        if k=="__curr" or k=="__obj" or k=="__meme" or k=="_instancecheck" or k=="__getstate__" or k=="__setstate__":
            return getattr(self,k)
        return self.__meme(getattr(self.__curr,k))

    def __setattr__(self,k,v):
        # print("setattr")
        # print(k)
        if k=="_vizHelper__obj" or k=="_vizHelper__curr" or k=="_vizHelper__meme":
            k=k[len("_vizHelper"):]
        if k=="__curr" or k=="__obj" or k=="__meme" or k=="_instancecheck" or k=="__getstate__" or k=="__setstate__":
            object.__setattr__(self,k,v)
        else:
            # print(k)
            setattr(self.__curr,k,v)
        # return self.__meme(getattr(self.__curr,k))
    def __dir__(self):
        return self.__curr.__dir__()
    
    def __repr__(self):
        if self.__curr is None:
            return ""
        try:
            return self.__curr.__repr__()
        except:
            return object.__repr__(self.__curr)

    def _getMe(self):
        return self.__curr
    def __getitem__(self,k):
        if isinstance(self.__curr,dict):
            return self.__meme(self.__curr.get(k))
        return self.__meme(self.__curr[k])

    def __iter__(self):
        return iter(self.__curr)
        
    def _instancecheck(self, typ):
        return isinstanceBase(self.__curr,typ)

    def __len__(self):
        return len(self.__curr)

def disable_plotly_in_cell():
    import IPython
    get_ipython().events.unregister('pre_run_cell', enable_plotly_in_cell)

def enable_plotly_in_cell():
    import IPython
    from plotly.offline import init_notebook_mode
    display(IPython.core.display.HTML('''<script src="/static/components/requirejs/require.js"></script>'''))
    init_notebook_mode(connected=False)
def plotly_google_colab():
    get_ipython().events.register('pre_run_cell', enable_plotly_in_cell)
