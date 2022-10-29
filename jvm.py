#!/usr/bin/env python3

# parsing functions
def pu_1(f)->int: return int.from_bytes(f.read(1), 'big')
def pu_2(f)->int: return int.from_bytes(f.read(2), 'big')
def pu_4(f)->int: return int.from_bytes(f.read(4), 'big')
def pu_8(f)->int: return int.from_bytes(f.read(8), 'big')

# Tag to string
def tag(i:int)->str:
    match(i):
        case 10:
            return "Methodref"
        case _:
            assert False, "Unimplemented tag: " + str(i)

# jvm class
class jvm:
    def __init__(self, path):
        self.f = open(path, 'rb')
        assert self.f.read(4) == b'\xca\xfe\xba\xbe', "not a class file"
        min_v = pu_2(self.f)
        self.v = str(pu_2(self.f))+'.'+str(min_v)
        self.const_c = pu_2(self.f)-1
        self.const_pool = []
        self.parse_cp()
    def parse_cp(self):
        for i in range(0, self.const_c):
            const = {}
            const['tag'] = tag(pu_1(self.f))
            match const['tag']:
                case "Methodref":
                    const['class_index'] = pu_2(self.f)-1
                    const['name_and_type_index'] = pu_2(self.f)-1
                    print(const)
                case _:
                    assert False, str(const['tag'])+" type const unimplemented"
            self.const_pool.append(const)
    def __repr__(self):
        rep = "VERSION: "+ self.v + "\nCONST_COUNT: " + str(self.const_c) + "\nCONST_POOL:" + str(self.const_pool)

        return rep

#init
vm = jvm("test.class")
print(vm)