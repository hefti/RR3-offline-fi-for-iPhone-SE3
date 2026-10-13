"""Execute the original/patched ARM64 gate in Unicorn; no game code is run natively."""
import argparse,json,pathlib,struct,sys,zipfile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_X29,UC_ARM64_REG_W23,UC_ARM64_REG_W8,UC_ARM64_REG_W9
from patches import patch,BASE,CAVE,SITE
parser=argparse.ArgumentParser(description='Execute 50 original/patched ARM64 GUI-filter cases in an emulator')
parser.add_argument('--input',required=True,type=pathlib.Path)
parser.add_argument('--report',type=pathlib.Path,default=pathlib.Path('build/arm64_gate_tests.json'))
args=parser.parse_args()
with zipfile.ZipFile(args.input) as z:binary=z.read('Payload/RealRacing3.app/RealRacing3')
patched,changes=patch(binary)

def execute(data,screen,family,gui):
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
    u.mem_map(BASE,0x10000);u.mem_write(BASE+CAVE,data[CAVE:CAVE+80])
    page=(BASE+SITE)&~4095;u.mem_map(page,4096);u.mem_write(BASE+SITE,data[SITE:SITE+64])
    u.mem_map(0x103251000,4096);u.mem_write(0x103251f14,struct.pack('<II',*screen))
    stack=0x700000000;u.mem_map(stack,0x4000);frame=stack+0x2000
    u.reg_write(UC_ARM64_REG_X29,frame)
    # scanf writes height first in this stack pair, width second.
    u.mem_write(frame-0x88,struct.pack('<II',family[1],family[0]))
    u.reg_write(UC_ARM64_REG_W23,2 if gui else 0)
    reached=[]
    def stop(uc,address,size,user):
        if address in [BASE+0x680a78,BASE+0x680b4c]:
            reached.append(address);uc.emu_stop()
    u.hook_add(UC_HOOK_CODE,stop)
    u.emu_start(BASE+SITE,BASE+0x680b50,count=40)
    assert len(reached)==1
    return reached[0]==BASE+0x680b4c,(u.reg_read(UC_ARM64_REG_W8),u.reg_read(UC_ARM64_REG_W9))

cases=[]
for screen in [(1334,750),(750,1334),(2048,1536),(2796,1290),(0,0)]:
    for family in [(480,320),(960,640),(2048,1536),(4096,3072),(1440,900)]:
        for gui in [False,True]:
            orig,original_limits=execute(binary,screen,family,gui)
            new,new_limits=execute(patched,screen,family,gui)
            if not gui:
                assert new==orig and new_limits==original_limits,(screen,family)
            else:
                assert new_limits==(2048,1536)
                expected=not(family[0]>2048 and family[1]>1536)
                assert new==expected,(screen,family,new,expected)
            cases.append(dict(screen=screen,family=family,gui=gui,original_admitted=orig,patched_admitted=new))
assert execute(binary,(1334,750),(2048,1536),True)[0] is False
assert execute(patched,(1334,750),(2048,1536),True)[0] is True
bad=bytearray(binary);bad[SITE]^=1
try:patch(bytes(bad));raise AssertionError('Patch must refuse changed instructions')
except ValueError:pass
args.report.parent.mkdir(parents=True,exist_ok=True)
args.report.write_text(json.dumps(dict(cases=len(cases),passed=True,guard_rejection_passed=True,results=cases),indent=2))
print(f'Passed {len(cases)} original/patched ARM64 cases; non-GUI behavior identical; modified-input refusal passed')
