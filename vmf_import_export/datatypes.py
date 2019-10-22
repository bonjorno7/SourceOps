import re
from .lexer import tokens
from math import sqrt

EPSILON = 0.000001

class base_variable:

    
    def __init__(self):
        self.value = None

    def get_value(self):
        return self.value

    def set_value(self, val):
        self.value = val

    def string(self):
        return str(self.value)

    @staticmethod
    def get_number_value_precise(st):
        if re.match("^-?\d+$", str(st)): return int(st)
        elif re.match("^-?\d+(\.\d+)?$", str(st)): return float(st)
        elif re.match("^-?\d+(\.\d+)?(e-?\d{3})$", str(st)):
            data = st.split("e")
            return float(data[0]) * 10**int(data[1])
        else:
            return(st)

    @staticmethod
    def get_number_value(st):
        if re.match("^-?\d+(\.\d+)?$", str(st)): return float(st)
        elif re.match("^-?\d+(\.\d+)?(e-?\d{3})$", str(st)):
            data = st.split("e")
            return float(data[0]) * 10**int(data[1])
        else:
            return(st)

    @staticmethod
    def eq_s(n1, n2):
        return abs(n1-n2)<EPSILON

    @staticmethod
    def equals(v1,v2):
        return eq_s(v1,v2)


class vec3(base_variable):
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            st = args[0]
        
            self.value = [base_variable.get_number_value(i) for i in
                          re.findall("(?<=(?:\(| |\[))?(?:-?\d+(?:\.\d+)?(?:e-?\d{3})?)(?=(?:\)| |\]))?", str(st))]

            self.x = self.value[0]
            try:
                self.y = self.value[1]
            except:
                print(self.value)
            self.z = self.value[2]
        elif len(args) == 3:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]

            self.value = [self.x,self.y,self.z]
            
    def string(self):
        return "("+str(self.x) + " " + str(self.y) + " " + str(self.z)+")"

    @staticmethod
    def equals(v1, v2):
        return (base_variable.eq_s(v1.x,v2.x)) and (base_variable.eq_s(v1.y,v2.y)) and (base_variable.eq_s(v1.y,v2.y))

    def length(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalise(self):
        l = self.length()
        self.x = self.x / l
        self.y = self.y / l
        self.z = self.z / l

        self.value = [self.x,self.y,self.z]

    def n(self):
        l = self.length()
        return vec3(self.x/l, self.y/l, self.z/l)

    @staticmethod
    def cross(a, b):
        return vec3(a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x)

    @staticmethod
    def dot(a, b):
        return a.x*b.x+a.y*b.y+a.z*b.z

    def __add__(self,y):
        if isinstance(y,vec3):
            return vec3(self.x+y.x, self.y+y.y, self.z+y.z)
        else:
            return vec3(self.x+y, self.y+y, self.z+y)

    def __sub__(self,y):
        if isinstance(y,vec3):
            return vec3(self.x-y.x, self.y-y.y, self.z-y.z)
        else:
            return vec3(self.x-y, self.y-y, self.z-y)

    def __mul__(self,y):
        if isinstance(y,vec3):
            return vec3(self.x*y.x, self.y*y.y, self.z*y.z)
        else:
            return vec3(self.x*y, self.y*y, self.z*y)

    def __div__(self,y):
        if isinstance(y,vec3):
            return vec3(self.x/y.x, self.y/y.y, self.z/y.z)
        else:
            return vec3(self.x/y, self.y/y, self.z/y)

    def __truediv__(self, y):
        if isinstance(y,vec3):
            return vec3(self.x/y.x, self.y/y.y, self.z/y.z)
        else:
            return vec3(self.x/y, self.y/y, self.z/y)

class vec3x3(base_variable):
    def __init__(self, *args, **kwargs):

        if len(args) == 1:
            st = args[0]
        
            self.value = [vec3(i) for i in
                          re.findall("\((?:(?:-?\d+(?:\.\d+)?(?:e-?\d{3})?) ?){3}\)", str(st))]

            self.v1 = self.value[0]
            self.v2 = self.value[1]
            self.v3 = self.value[2]

        elif len(args) == 3:
            self.v1 = args[0]
            self.v2 = args[1]
            self.v3 = args[2]

            self.value = [self.v1.value, self.v2.value, self.v3.value]

        elif len(args) == 9:
            self.v1 = vec3(args[0],args[1],args[2])
            self.v2 = vec3(args[3],args[4],args[5])
            self.v3 = vec3(args[6],args[7],args[8])

            self.value = [self.v1.value, self.v2.value, self.v3.value]

        if self.value is not None:
            self.gen_ijk_form()

    def gen_ijk_form(self):
        self.n = vec3.cross(self.v3-self.v1, self.v2-self.v1).n() #circular dependecy sucks
        self.d = abs(vec3.dot(self.n, self.v1))

    def string(self):
        return str(self.v1.string() + " " + self.v2.string()
                   + " " + self.v3.string())

    @staticmethod
    def equals(v1, v2):
        return vec3.equals(v1.v1, v2.v1) and vec3.equals(v1.v2, v2.v2) and vec3.equals(v1.v3, v2.v3)

class vecUV(base_variable):
    def __init__(self, *args, **kwargs):

        if len(args) == 1:
            st = args[0]
            data = st.split('] ')
            data[0]+=']'

            self.scale = base_variable.get_number_value(data[1])
            self.value = [[base_variable.get_number_value(i) for i in
                           re.findall("(?<=(?:\[| ))(?:-?\d+(?:\.\d+)?(?:e-?\d{3})?)(?=(?:\]| ))", data[0])],
                          self.scale]
            
            self.x = self.value[0][0]
            self.y = self.value[0][1]
            self.z = self.value[0][2]

            self.translate = self.value[0][3]

        elif len(args) == 2:
            self.value = args

            self.x = self.value[0][0]
            self.y = self.value[0][1]
            self.z = self.value[0][2]

            self.translate = self.value[0][3]

            self.scale = self.value[1]

        elif len(args) == 5:
            self.value = [args[0:4],args[4]]

            self.x = self.value[0][0]
            self.y = self.value[0][1]
            self.z = self.value[0][2]

            self.translate = self.value[0][3]

            self.scale = self.value[1]

        else:
            self.x = None
            self.y = None
            self.z = None
            self.scale = None
            self.translate = None

            self.value = None

    def string(self):
        return str("["+str(self.x)+" "+str(self.y)+" "+str(self.z)+" "+str(self.translate)+"]"+" "+str(self.scale))

    @staticmethod
    def equals(v1, v2):
        return (base_variable.eq_s(v1.x,v2.x) and base_variable.eq_s(v1.y,v2.y) and
                base_variable.eq_s(v1.z,v2.z) and base_variable.eq_s(v1.translate,v2.translate) and base_variable.eq_s(v1.scale,v2.scale))

class vec_disp(base_variable):
    def __init__(self, *args, **kwargs):
        if len(args)>4:
            self.value = args
        elif len(args)==1:
            self.value = [base_variable.get_number_value(i) for i in args[0].split()]

    def string(self):
        return str(" ".join([str(i) for i in self.value]))

    @staticmethod
    def equals(v1,v2):
        if len(v1)!=len(v2): return False
        b_vals = []
        for i in range(len(v1.value)):
            b_vals.append(base_variable.eq_s(v1.value[i], v2.value[i]))
        for i in b_vals:
            if i is False:
                return False
        return True
                

def get_variable(st):
    if re.match("^-?\d+(\.\d+)?(e-?\d{3})?$",st): return base_variable.get_number_value_precise(str(st))
    elif re.match("^(?:\[|\()?(?:.+\s+){2}.+(?:\]|\))?$", st): return vec3(st)
    elif re.match("^(?:(?:\[|\()(?:.+\s+){2}.+(?:\]|\)) ){2}(?:\[|\()(?:.+\s+){2}.+(?:\]|\))$", st): return vec3x3(st)
    elif re.match("^\[(?:(?:.+\s+){3}.+)\]\s.+$", st): return vecUV(st)
    elif re.match("^((-?\d+(\.\d+)?(e-?\d{3})? ){4,}(-?\d+(\.\d+)?(e-?\d{3})?))$", st): return vec_disp(st)
    else: return str(st)

def get_variable_from_token(st, tk):
    if tk == tokens.vec_3: return vec3(st)
    elif tk == tokens.vec_3x3: return vec3x3(st)
    elif tk == tokens.vec_UV: return vecUV(st)
    elif tk == tokens.vec_disp: return vec_disp(st)
    elif re.match("^-?\d+$", str(st)): return int(st)
    elif re.match("^-?\d+(\.\d+)?(e-?\d{3})?$",str(st)): return base_variable.get_number_value_precise(str(st))
    else: return str(st)

base_variable.get_variable = get_variable
base_variable.get_variable_from_token = get_variable_from_token
    

if __name__ == "__main__":

    vec = base_variable.get_variable("[1 2 3]")
    print(vec.string())

    v3x3 = base_variable.get_variable("(1 -2.3 3e-005) (4.1e002 5.2e-001 6) (7 8 9)")
    print(v3x3.string())

    vuv = base_variable.get_variable("[1 2 3 4] 0.25")
    print(vuv.string())

    st = base_variable.get_variable("hello")
    print(st)

    int_t = base_variable.get_variable("12")
    print(int_t)

    flt = base_variable.get_variable("12.2")
    print(flt)

    exp = base_variable.get_variable("12.2e003")
    print(exp)

    disp = base_variable.get_variable("1 1 1 1 1 1 1 1 1 1 1 1 1")
    print(disp.string())

    

                
