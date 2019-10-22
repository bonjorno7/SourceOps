from lexer import tokens
from token_reader import tokenReader
from datatypes import *

class base_class:
    def __init__(self, tread):
        self.tread = tread
        self.keyvals = {}

    def parse_value(self, val, tk):
        return base_variable.get_variable_from_token(val, tk)

    def parse_to_next_cb(self):
        _ = self.tread.forw()
        if _ is None:
            raise Exception("Unexpected EOF")
        if _[0] != tokens.sp_cBrOpen:
            raise Exception("Malformed class at token " + self.tread.tokens[self.tread.currentPos-1][1])
        
        k = self.tread.forw()
        v = self.tread.forw()
        while k is not None and k[0] != tokens.sp_cBrClose:
            if v is not None and v[0] == tokens.sp_cBrClose:
                raise Exception("Malformed class before token " + k[1])
            self.keyvals[k[1]] = self.parse_value(v[1], v[0])
            k = self.tread.forw()
            if k[0] == tokens.sp_cBrClose:
                break
            v = self.tread.forw()
    
class base_parent_class(base_class):
    def __init__(self, tread):
        base_class.__init__(self, tread)
        self.children = []

    def parse_to_next_cb(self):
        _ = self.tread.forw()
        if _ is None:
            raise Exception("Unexpected EOF")
        if _[0] != tokens.sp_cBrOpen:
            raise Exception("Malformed class at token " + self.tread.tokens[self.tread.currentPos-1][1])
        
        k = self.tread.forw()
        while k is not None and k[0] != tokens.sp_cBrClose:
            if k[0] == tokens.s_class:
                self.children.append(vmf_classes.resolve_class(k[1], self.tread))
            else:
                v = self.tread.forw()
                if v is not None and v[0] == tokens.sp_cBrClose:
                    raise Exception("Malformed class before token " + k[1])
                self.keyvals[k[1]] = self.parse_value(v[1], v[0])
            k = self.tread.forw()

base_classes = ["versioninfo", "visgroup", "viewsettings", "editor", "normals",
                "distances", "offsets", "offset_normals", "alphas",
                "triangle_tags", "allowed_verts", "connections", "camera",
                "cordon"]
parent_classes = ["visgroups", "world", "solid", "side", "hidden", "group",
                  "dispinfo", "entity", "cameras", "cordons"]

for i in base_classes:
    exec("class "+i+"(base_class):\n    pass")
for i in parent_classes:
    exec("class "+i+"(base_parent_class):\n    pass")

classes = [eval(i) for i in base_classes]
classes += [eval(i) for i in parent_classes]


class vmf_classes:
    
    @staticmethod
    def resolve_class(cname, tread):
        found = False
        for i in classes:
            if found is False and cname == i.__name__:
                var = i(tread)
                var.parse_to_next_cb()
                found = True
                return var
        if found is False:
            raise Exception("Unknown class name " + cname)

    @staticmethod
    def parse_expression(term, tread):
        _ = tread.currentToken
        while _ is not None and _[0] != tokens.s_class:
            _ = tread.forw()
            continue
        if _ is None:
            raise Exception("Unexpected EOF")
        return vmf_classes.resolve_class(tread.currentToken[1], tread)
