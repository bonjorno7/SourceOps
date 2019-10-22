import re
import pprint
from enum import Enum

class tokens(Enum):
        NULL = 0
        operation = 1
        string = 2
        s_class = 3

        #integer = 4
        number = 5
        vec_3 = 6
        vec_3x3 = 7
        vec_UV = 8
        vec_disp = 9
        

        sp_rBrOpen = 105
        sp_rBrClose = 106 # I don't think these occur but I can't be sure so they're staying for now
        
        sp_cBrOpen = 107
        sp_cBrClose = 108 

        #sp_comma = 109

        #sp_sColon = 110
        #sp_equals = 111
        #sp_rColon = 112

class lexFile:
        def __init__(self, path):
                self.file = open(path)
                self.lexify()

        def next_char(self):
                c = self.file.read(1)
                return c

        def move_back(self,amt):
                self.file.seek(self.file.tell() - amt)

        def _classify_string(self, st):
                if re.match("^$", st): return (tokens.string, st)
                elif re.match("^-?\d+(\.\d+)?(e-?\d{3})?$", st): return (tokens.number, st)
                elif re.match("^(((-?\d+(\.\d+)?(e-?\d{3})? +){2}(-?\d+(\.\d+)?(e-?\d{3})?))|(\[(-?\d+(\.\d+)?(e-?\d{3})? +){2}(-?\d+(\.\d+)?(e-?\d{3})?))\])$", st):
                        return (tokens.vec_3, st)
                elif re.match("^(\((-?\d+(\.\d+)?(e-?\d{3})? +){2}(-?\d+(\.\d+)?(e-?\d{3})?)\) +){2}(\((-?\d+(\.\d+)?(e-?\d{3})? ){2}(-?\d+(\.\d+)?(e-?\d{3})?)\))$", st):
                        return (tokens.vec_3x3, st)
                elif re.match("^\[(-?\d+(\.\d+)?(e-?\d{3})? +){3}(-?\d+(\.\d+)?(e-?\d{3})?)\] +(-?\d+(\.\d+)?(e-?\d{3})?)$", st):
                        return (tokens.vec_UV, st)
                elif re.match("^((-?\d+(\.\d+)?(e-?\d{3})? ){4,}(-?\d+(\.\d+)?(e-?\d{3})?))$", st):
                        return (tokens.vec_disp, st)
                else:
                        #print("Warning: string " + st + " was found invalid in classification")
                        return (tokens.string, st)
                        

        def _scan_string(self, delim):
                c = self.next_char()
                retval = ""
                while c != delim:
                        if c is None:
                                raise Exception("Unexpected EOF")
                        retval = retval + c
                        c = self.next_char()
                return self._classify_string(retval)

        def _scan(self, first_char, allowed_c, allowed_f):
                c = self.next_char()
                retval = first_char
                while c is not None and re.match(allowed_c, c):
                        retval = retval + c
                        c = self.next_char()
                if re.match(allowed_f, retval):
                        self.move_back(1)
                        return retval
                else:
                        raise Exception("Malformed token around character " + str(self.file.tell()))

        def special_char(self, c):
                if c == "(": return tokens.sp_rBrOpen
                elif c == ")": return tokens.sp_rBrClose
                elif c == "{": return tokens.sp_cBrOpen
                elif c == "}": return tokens.sp_cBrClose
                #elif c == ",": return tokens.sp_comma
                #elif c == ";": return tokens.sp_sColon
                #elif c == "=": return tokens.sp_equals
                #elif c == ":": return tokens.sp_rColon
                else:
                        raise Exception("Something went horribly wrong with special character analysis")
 
        def lex_iter(self):
                c = self.next_char()
                while c:
                        if c in " \n\t": pass
                        elif c in "+-*/": yield (tokens.operation, c)
                        elif c in "(){}": yield (self.special_char(c), "")
                        elif c in ("'", '"'): yield self._scan_string(c)
                        elif re.match("[\d]", c):
                                yield (tokens.number, self._scan(c, "[\d]", "^(\d*\.)?\d+$"))
                        elif re.match("[_a-zA-Z]", c):
                                yield (tokens.s_class, self._scan(c, "[_a-zA-Z0-9]", "^[\da-zA-Z_]*$"))
                        else:
                                raise Exception("Unknown token at character " + str(self.file.tell()))
                        c = self.next_char()

        def lexify(self):
                self.tokens = list(self.lex_iter())

        def cleanup(self):
                self.file.close()


if __name__ == "__main__":
        file = lexFile("data.txt");

        file.cleanup()


        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(file.tokens)
