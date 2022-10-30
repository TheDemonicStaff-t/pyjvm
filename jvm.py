#!/usr/bin/env python3

# parsing functions
def pu_1(f)->int: return int.from_bytes(f.read(1), 'big')
def pu_2(f)->int: return int.from_bytes(f.read(2), 'big')
def pu_4(f)->int: return int.from_bytes(f.read(4), 'big')
def pu_8(f)->int: return int.from_bytes(f.read(8), 'big')

# access flag defs
class_access_flags = [
    (0x0001, 'PUBLIC'),
    (0x0010, 'FINAL'),
    (0x0020, 'SUPER'),
    (0x0200, 'INTERFACE'),
    (0x0400, 'ABSTRACT'),
    (0x1000, 'SYNTHETIC'),
    (0x2000, 'ANNOTATION'),
    (0x4000, 'ENUM'),
]

method_access_flags = [
    (0x0001, 'PUBLIC'),
    (0x0002, 'PRIVATE'),
    (0x0004, 'PROTECTED'),
    (0x0008, 'STATIC'),
    (0x0010, 'FINAL'),
    (0x0020, 'SYNCHRONIZED'),
    (0x0040, 'BRIDGE'),
    (0x0080, 'VARAGRS'),
    (0x0100, 'NATIVE'),
    (0x0400, 'ABSTRACT'),
    (0x0800, 'STRICT'),
    (0x1000, "SYNTHETIC")
]

# external functions
def tag(i:int)->str:
    match(i):
        case 10:
            return "Methodref"
        case 9:
            return "Fieldref"
        case 8:
            return "String"
        case 7:
            return "Class"
        case 12:
            return "NameAndType"
        case 1:
            return "Utf8"
        case _:
            assert False, "Unimplemented tag: " + str(i)

def acc_flag(acfd, data):
    flags = ''
    for i in acfd: 
        if (data&(i[0])) == i[0]: flags+=i[1]+' '
    return flags
    

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
        self.access_flags = pu_2(self.f)
        self.this = pu_2(self.f)-1
        self.super = pu_2(self.f)-1
        self.interface_count = pu_2(self.f)
        self.interfaces = []
        self.parse_interface()
        self.field_count = pu_2(self.f)
        self.fields = []
        self.parse_fields()
        self.method_count = pu_2(self.f)
        self.methods = []
        self.parse_methods()

    def parse_cp(self):
        for i in range(0, self.const_c):
            const = {}
            const['tag'] = tag(pu_1(self.f))
            match const['tag']:
                case "Methodref":
                    const['class_index'] = pu_2(self.f)-1
                    const['name_and_type_index'] = pu_2(self.f)-1
                case "Fieldref":
                    const['class_index'] = pu_2(self.f)-1
                    const['name_and_type_index'] = pu_2(self.f)-1
                case "String":
                    const['string_index'] = pu_2(self.f)-1
                case "Class":
                    const['name_index'] = pu_2(self.f)-1
                case "NameAndType":
                    const['name_index'] = pu_2(self.f)-1
                    const['descriptor_index'] = pu_2(self.f)-1
                case "Utf8":
                    const['length'] = pu_2(self.f)
                    const['bytes'] = ''
                    for i in range(const['length']):
                        const['bytes'] += self.f.read(1).decode('utf8')
                case _:
                    assert False, str(const['tag'])+" type const unimplemented"
            self.const_pool.append(const)
    def parse_interface(self):
        for i in range(self.interface_count):
            self.interfaces.append(pu_2(self.f))
    def parse_fields(self):
        for i in range(self.field_count):
            assert False, 'FIELDS UNIMPLEMENTED'
    def parse_methods(self):
        for i in range(self.method_count):
            method = {}
            method['access_flags'] = pu_2(self.f)
            method['name_index'] = pu_2(self.f)-1
            method['descriptor_index'] = pu_2(self.f)-1
            method['attribute_count'] = pu_2(self.f)
            method['attributes'] = self.parse_attributes(method['attribute_count'])
            self.methods.append(method)
    def parse_attributes(self, count):
        attributes = []
        for i in range(count):
            attribute = {}
            attribute['name_index'] = pu_2(self.f)-1
            attribute['data'] = {}
            attribute['len'] = pu_4(self.f)
            match (self.const_pool[attribute['name_index']]['bytes']):
                case 'Code':
                    attribute['data']['max_stack'] = pu_2(self.f)
                    attribute['data']['max_locals'] = pu_2(self.f)
                    len = pu_4(self.f)
                    attribute['data']['code'] = self.f.read(len)
                    attribute['data']['exception_table'] = []
                    for i in range(pu_2(self.f)):
                        exception = {}
                        exception['start_pc'] = pu_2(self.f)
                        exception['end_pc'] = pu_2(self.f)
                        exception['handler_pc'] = pu_2(self.f)
                        exception['catch_type'] = pu_2(self.f)
                        attribute['data']['exception_table'].append(exception)
                    ac = pu_2(self.f)
                    attribute['data']['attrs'] = self.parse_attributes(ac)
                case 'LineNumberTable':
                    attribute['data']['line_number_table'] = []
                    len = pu_2(self.f)
                    for x in range(len):
                        line_number = {}
                        line_number['start_pc'] = pu_2(self.f)
                        line_number['line_number'] = pu_2(self.f)
                        attribute['data']['line_number_table'].append(line_number)

                case _:
                    assert False, 'UNIMPLEMENTED ATTR ' + self.const_pool[attribute['name_index']]['bytes']
            attributes.append(attribute)
        return attributes
    def attr_rep(self, attribute, spacing):
        name = self.const_pool[attribute['name_index']]['bytes']
        attr = ''
        match name:
            case 'Code':
                attr += spacing + 'max_stack: ' + str(attribute['data']['max_stack'])
                attr += spacing + 'max_locals: ' + str(attribute['data']['max_locals'])
                attr += spacing + 'code: ' + str(attribute['data']['code'])
                attr += spacing + 'exception_table[' + str(len(attribute['data']['exception_table'])) + ']='
                for i in range(len(attribute['data']['exception_table'])):
                    attr += spacing + '    ' + str(i)
                    attr += spacing + '    start_pc:' + attribute['data']['exception_table'][i]['start_pc']
                    attr += spacing + '    end_pc:' + attribute['data']['exception_table'][i]['end_pc']
                    attr += spacing + '    end_pc:' + attribute['data']['exception_table'][i]['handler_pc']
                    attr += spacing + '    end_pc:' + attribute['data']['exception_table'][i]['catch_type']
                attr += spacing + 'attrs:[' + str(len(attribute['data']['attrs'])) + ']='
                for i in range(len(attribute['data']['attrs'])):
                    
                    attr += spacing +'    '+ str(i) + ': ' + self.attr_rep(attribute['data']['attrs'][i], spacing + '        ')
                    
            case 'LineNumberTable':
                attr += 'LineNumberTable:'
                for i in range(len(attribute['data']['line_number_table'])):
                    attr += spacing +str(i)
                    attr += ': ' + str(attribute['data']['line_number_table'][i]['start_pc'])
                    attr += ' , ' + str(attribute['data']['line_number_table'][i]['line_number'])
            case _:
                assert False, 'UNIMPLEMENTED ATTR REP ' + name
        return attr

    def __repr__(self):
        spacing = '\n\t\t\t'
        rep = "VERSION: "+ self.v + "\nCONST_POOL[" + str(self.const_c) + "]:" 
        for i in range(self.const_c):
            rep += spacing + str(i) + ':' + str(self.const_pool[i])
        rep += '\nACCESS_FLAGS: ' + acc_flag(class_access_flags, self.access_flags)
        rep += '\nTHIS: ' + self.const_pool[self.const_pool[self.this]['name_index']]['bytes']
        rep += '\nSUPR: ' + self.const_pool[self.const_pool[self.super]['name_index']]['bytes']
        rep += '\nINTERFACES[' + str(self.interface_count) + ']:' + str(self.interfaces)
        rep += '\nFIELDS[' + str(self.field_count) +']:' + str(self.fields)
        rep += '\nMETHODS[' + str(self.method_count) + ']:' 
        for i in range(self.method_count):
            rep += spacing + str(i) + ':\t' + acc_flag(method_access_flags, self.methods[i]['access_flags'])
            rep += spacing + '\tNAME: ' + self.const_pool[self.methods[i]['name_index']]['bytes']
            rep += spacing + '\tDESC: ' + self.const_pool[self.methods[i]['descriptor_index']]['bytes']
            rep += spacing + '\tATTR[' + str(self.methods[i]['attribute_count']) + ']='
            for x in range(self.methods[i]['attribute_count']):
                rep += spacing + '\t\t' + str(i) + ': ' + self.const_pool[self.methods[i]['attributes'][x]['name_index']]['bytes'] + ' : ' + str(self.methods[i]['attributes'][x]['len'])
                rep += self.attr_rep(self.methods[i]['attributes'][x], spacing +'\t\t   ')

        return rep

#init
vm = jvm("test.class")
print(vm)