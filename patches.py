"""Exact-build static ARM64 change, restricted to GUI manifest entries."""
import struct

UUID=bytes.fromhex('06ed5b50c44c3b69a5840701b8a88451')
SITE=0x680b24
CAVE=0x3800
BASE=0x100000000
RETURN=BASE+0x680b38

def branch(pc,target):
    delta=target-pc
    assert delta%4==0 and -(1<<27)<=delta<(1<<27)
    return 0x14000000|((delta//4)&0x3ffffff)

def adrp(pc,target,rd):
    pages=((target&~4095)-(pc&~4095))//4096
    assert -(1<<20)<=pages<(1<<20)
    value=pages&0x1fffff
    return 0x90000000|((value&3)<<29)|((value>>2)<<5)|rd

def words(values):return struct.pack('<'+'I'*len(values),*values)

def stub():
    pc=BASE+CAVE
    # First five instructions reproduce the original loads and argument read.
    code=[adrp(pc,0x103251000,8),0xb94f1508,
          adrp(pc+8,0x103251000,9),0xb94f1929,0x296f4fb5,
          0x71000aff] # cmp w23,#2; scanf returned two GUI dimensions?
    ne_pc=pc+len(code)*4
    # Conditional branches have only a 1 MiB reach: skip the two MOVs locally.
    local_exit=pc+9*4
    code.append(0x54000001|(((local_exit-ne_pc)//4&0x7ffff)<<5))
    code += [0x52800000|(2048<<5)|8,0x52800000|(1536<<5)|9]
    code.append(branch(pc+len(code)*4,RETURN))
    return words(code)

def macho_uuid(binary):
    assert struct.unpack_from('<I',binary)[0]==0xfeedfacf
    off=32
    for _ in range(struct.unpack_from('<I',binary,16)[0]):
        cmd,size=struct.unpack_from('<II',binary,off)
        if cmd==0x1b:return binary[off+8:off+24]
        off+=size
    raise ValueError('No UUID')

def patch(binary,hd=True):
    if macho_uuid(binary)!=UUID:raise ValueError('Unsupported executable UUID')
    expected=words([adrp(BASE+SITE,0x103251000,8),0xb94f1508,
                    adrp(BASE+SITE+8,0x103251000,9),0xb94f1929,0x296f4fb5])
    if binary[SITE:SITE+len(expected)]!=expected:
        raise ValueError('GUI filter original instructions do not match')
    out=bytearray(binary);changes=[]
    if hd:
        data=stub()
        if any(binary[CAVE:CAVE+len(data)]):raise ValueError('Code cave is not unused zero padding')
        header_end=32+struct.unpack_from('<I',binary,20)[0]
        if header_end+128>CAVE:raise ValueError('Insufficient load-command/code separation')
        replacement=words([branch(BASE+SITE,BASE+CAVE)])
        for offset,before,after,label in [(SITE,binary[SITE:SITE+4],replacement,'GUI manifest threshold detour'),(CAVE,binary[CAVE:CAVE+len(data)],data,'GUI-only 2048x1536 ceiling; non-GUI original thresholds')]:
            out[offset:offset+len(after)]=after
            changes.append(dict(offset=hex(offset),original=before.hex(),replacement=after.hex(),description=label))
    return bytes(out),changes

def inject_dependency(binary,name):
    out=bytearray(binary)
    ncmds,sizeofcmds=struct.unpack_from('<II',out,16)
    encoded=name.encode()+b'\0';size=(24+len(encoded)+7)&~7
    command=struct.pack('<IIIIII',0xc,size,24,0,0x10000,0x10000)+encoded
    command+=b'\0'*(size-len(command))
    end=32+sizeofcmds
    if end+size>CAVE or any(out[end:end+size]):raise ValueError('No safe header space for dependency')
    out[end:end+size]=command
    struct.pack_into('<II',out,16,ncmds+1,sizeofcmds+size)
    return bytes(out),dict(offset=hex(end),size=size,dependency=name)

def eds_crypt(data):
    key=bytes.fromhex('a535b3b1e843e7cf');s=list(range(256));j=0
    for i in range(256):
        j=(j+s[i]+key[i%8])&255;s[i],s[j]=s[j],s[i]
    j=0
    for i in range(1,134):j=(j+s[i])&255;s[i],s[j]=s[j],s[i]
    i=133;out=bytearray()
    for b in data:
        i=(i+1)&255;j=(j+s[i])&255;s[i],s[j]=s[j],s[i]
        out.append(b^s[(s[i]+s[j])&255])
    return bytes(out)
