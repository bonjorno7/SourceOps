from lexer import *
from token_reader import tokenReader

from vmf_classes import *
from datatypes import *

class parseFile:

    def __init__(self, tokens):
        self.tread = tokenReader(tokens)
        self.classes = []
        self.parse()

    def parse_expression(self, term):
        return vmf_classes.parse_expression(term, self.tread)


    def parse(self):
        while self.tread.EOF is False:
            self.classes.append(self.parse_expression(tokens.sp_cBrClose))


def print_class(cls, tab=1):
    print("\t"*(tab-1)+str(type(cls)))
    if(issubclass(type(cls), base_parent_class)):
        for i in cls.keyvals:
            if issubclass(type(cls.keyvals[i]), base_variable):
                print("\t"*tab+i+", "+cls.keyvals[i].string())
            else:
                print("\t"*tab+i+", "+str(cls.keyvals[i]))
        for i in cls.children:
            print_class(i,tab+1)
    else:
        for i in cls.keyvals:
            if issubclass(type(cls.keyvals[i]), base_variable):
                print("\t"*tab+i+", "+cls.keyvals[i].string())
            else:
                print("\t"*tab+i+", "+str(cls.keyvals[i]))

def search_class_for_kv(cls, typ, key, val):
    if type(cls).__name__ == typ:
        if key in cls.keyvals.keys():
            kv_s = cls.keyvals[key]
            if type(kv_s) == type(val):
                
                if issubclass(type(val), base_variable):
                    if val.__class__.equals(kv_s,val):
                        return cls
                else:
                    if isinstance(kv_s, float):
                        if base_variable.eq_s(kv_s, val):
                            return cls
                    else:
                        if kv_s==val:
                            return cls
    if not issubclass(type(cls), base_parent_class):
        return None
    for i in cls.children:
        x = search_class_for_kv(i, typ, key, val)
        if x is not None:
            return x
    return None

def search_first_class(cls, typ):
    if type(cls).__name__ == typ:
        return cls
    else:
        if not issubclass(type(cls), base_parent_class):
            return None
        for i in cls.children:
            x = search_first_class(i, typ)
            if x is not None:
                return x
    return None

def search_all_for_kv(lst, typ, key, val):
    for i in lst:
        ret = search_class_for_kv(i, typ, key, val)
        if ret is not None:
            return ret
    return None

def search_all_first_class(lst, typ):
    for i in lst:
        ret = search_first_class(i, typ)
        if ret is not None:
            return ret
    return None

def __search_single_class(cls, typ, lst):
    if type(cls).__name__ == typ:
        lst.append(cls)
    if not issubclass(type(cls), base_parent_class):
        return
    for i in cls.children:
        __search_single_class(i, typ, lst)
        
def search_single_class(cls, typ):
    lst = []
    __search_single_class(cls, typ, lst)
    return lst
        

def search_all_classes(lst,typ):
    cls_lst = []
    for i in lst:
        search_single_class(i,typ,cls_lst)
    return cls_lst

if __name__ == "__main__":
    lex = lexFile("data.txt")
    lex.cleanup()

    parse = parseFile(lex.tokens)


    while True:
        x = input("get object: ").split()
        ret = None
        if len(x) >= 3:
            ret = search_all_for_kv(parse.classes, x[0], x[1], base_variable.get_variable(" ".join(x[1:])))
        if len(x) == 2:
            print(type(base_variable.get_variable(x[1])))
            ret = search_all_for_kv(parse.classes, x[0], "id", base_variable.get_variable(x[1]))
        elif len(x) == 1:
            ret = search_all_first_class(parse.classes, x[0])
        if ret is not None:
            print_class(ret)
        else:
            print("No instances found.")
        
