"""Build reviewable, unsigned-for-device diagnostic/control and HD test IPAs.
Never opens a device or writes the original inputs. Re-sign with the user's
normal sideloading tool before an explicitly approved installation.
"""
import copy,hashlib,json,os,pathlib,plistlib,struct,subprocess,sys,zipfile
from patches import patch,inject_dependency,eds_crypt,macho_uuid,UUID,SITE,CAVE,stub

ROOT=pathlib.Path(__file__).resolve().parent
BUILD=ROOT/'build'
STUBS=BUILD/'stubs'
OUTPUT=ROOT/'dist'
INPUT=None
APP='Payload/RealRacing3.app/'
EXPECTED_MAIN_SHA256='066a4d304a35bcfbd87847189fbbb2af8e9bac0ca7a02d38ac420952d0701378'
EXPECTED_EDS_SHA256='dfd454078eb77509ef3a48ded309aece63cc03338775a8aea712e11c3a9cb19a'
SOURCE_SHA256=None
SDK=None

def run(args):
    r=subprocess.run(args,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if r.stdout:print(r.stdout.rstrip(),flush=True)
    return r.stdout

def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def compile_helper():
    flags=['xcrun','clang','-target','arm64-apple-ios13.0','-isysroot',SDK,'-I',str(ROOT),'-Wno-incompatible-sysroot','-fno-stack-protector','-fno-builtin','-O2','-fvisibility=hidden']
    objects=[]
    for source in [ROOT/'diagnostics.c',ROOT/'fishhook.c']:
        obj=BUILD/(source.stem+'.o');run(flags+['-c',str(source),'-o',str(obj)]);objects.append(obj)
    undefined=run(['nm','-u','-j',*map(str,objects)]).splitlines()
    symbols=sorted({s for s in undefined if s.startswith('_') and s!='_rebind_symbols_image'})
    cf=[s for s in symbols if s.startswith('_CF')];system=[s for s in symbols if not s.startswith('_CF')]+['dyld_stub_binder']
    for name,install,exports in [('libSystem','/usr/lib/libSystem.B.dylib',system),('CoreFoundation','/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation',cf)]:
        tbd=('--- !tapi-tbd\ntbd-version: 4\ntargets: [ arm64-ios ]\ninstall-name: '+repr(install)+'\ncurrent-version: 1.0\ncompatibility-version: 1.0\nexports:\n  - targets: [ arm64-ios ]\n    symbols: [ '+', '.join(exports)+' ]\n...\n')
        (STUBS/f'{name}.tbd').write_text(tbd)
    dylib=BUILD/'RR3Diagnostics.dylib'
    run(flags+['-dynamiclib','-nostdlib',*map(str,objects),str(STUBS/'libSystem.tbd'),str(STUBS/'CoreFoundation.tbd'),'-Wl,-install_name,@rpath/RR3Diagnostics.dylib','-Wl,-platform_version,ios,13.0,13.0','-o',str(dylib)])
    run(['codesign','--force','--sign','-','--timestamp=none',str(dylib)])
    run(['codesign','--verify','--strict',str(dylib)])
    # A target-platform check, not a claim of an iPhone execution test.
    raw=dylib.read_bytes();off=32;platforms=[]
    for _ in range(struct.unpack_from('<I',raw,16)[0]):
        cmd,size=struct.unpack_from('<II',raw,off)
        if cmd==0x32:platforms.append(struct.unpack_from('<III',raw,off+8))
        off+=size
    assert platforms and platforms[0][0]==2,platforms
    (BUILD/'helper_link_report.json').write_text(json.dumps(dict(platforms=platforms,undefined_symbols=symbols,dependencies=run(['otool','-L',str(dylib)]),sha256=sha(dylib)),indent=2))
    return dylib

def native_test():
    exe=BUILD/'test_native'
    run(['xcrun','clang','-isysroot',SDK,'-I',str(ROOT),'-DRR3_DIAG_TEST','-fno-builtin','-O2',str(ROOT/'diagnostics.c'),str(ROOT/'fishhook.c'),str(ROOT/'test_native.c'),'-framework','Foundation','-o',str(exe)])
    fixture=BUILD/'native-fixture-verified';fixture.mkdir(exist_ok=True)
    run([str(exe),str(fixture)])
    logs=sorted((fixture/'Documents/RR3-Diagnostics').glob('*.log'),key=lambda p:p.stat().st_mtime)
    text=logs[-1].read_text()
    for needle in ['fopen\tMISSING_OR_ERROR\terrno=2','access\tMISSING_OR_ERROR\terrno=2','stat\tMISSING_OR_ERROR\terrno=2','open\tOK','fopen\tOK','stat\tOK','ENGINE\tAsset request 7']:
        assert needle in text,needle
    assert 'private' not in text
    (BUILD/'native_test_report.json').write_text(json.dumps(dict(passed=True,log=str(logs[-1]),checks=['real main-image import rebinding','missing-file errors preserved','open creation and file contents preserved','stat result preserved','NSLog format/varargs captured','message filtering']),indent=2))

def raw_copy(source,target,info,end_offset):
    """Preserve each unchanged ZIP local record, including its compressed data."""
    copied=copy.copy(info);target.fp.seek(target.start_dir);copied.header_offset=target.fp.tell()
    target._writecheck(copied)
    source.fp.seek(info.header_offset);remaining=end_offset-info.header_offset
    while remaining:
        block=source.fp.read(min(4*1024*1024,remaining))
        if not block:raise EOFError('Truncated original ZIP record')
        target.fp.write(block);remaining-=len(block)
    target.filelist.append(copied);target.NameToInfo[copied.filename]=copied
    target.start_dir=target.fp.tell();target._didModify=True

def make_ipa(helper,mode):
    hd=mode=='HD';name=f'RR3-SE3-{mode}-Test-v1.ipa';out=OUTPUT/name
    if out.exists():raise FileExistsError(f'Refusing to overwrite existing output: {out}')
    manifest=dict(mode=mode,experimental=True,source_ipa_sha256=SOURCE_SHA256,original_bundle_identifier=None,game_uuid=UUID.hex(),helper_sha256=sha(helper),device_tested=False,requires_user_signing=True,phone_modified=False)
    with zipfile.ZipFile(INPUT) as source:
        original=source.read(APP+'RealRacing3');assert macho_uuid(original)==UUID
        changed,ops=patch(original,hd=hd)
        changed,dependency=inject_dependency(changed,'@executable_path/Frameworks/RR3Diagnostics.dylib')
        binary=BUILD/f'RealRacing3-{mode}';binary.write_bytes(changed);binary.chmod(0o755)
        run(['codesign','--force','--sign','-','--timestamp=none',str(binary)])
        run(['codesign','--verify','--strict',str(binary)])
        modified={APP+'RealRacing3':binary.read_bytes()}
        info=plistlib.loads(source.read(APP+'Info.plist'))
        manifest['original_bundle_identifier']=info['CFBundleIdentifier']
        info['CFBundleDisplayName']='RR3 SE3 HD Test' if hd else 'RR3 SE3 Diag Test'
        info['UIFileSharingEnabled']=True;info['LSSupportsOpeningDocumentsInPlace']=True
        modified[APP+'Info.plist']=plistlib.dumps(info,sort_keys=False)
        added={APP+'Frameworks/RR3Diagnostics.dylib':helper.read_bytes()}
        if hd:
            key=APP+'res/eds/iPhone.plist';plain=eds_crypt(source.read(key));profile=plistlib.loads(plain)
            assert profile['GUI_ATLAS_OVERRIDE']=='' and profile['PLIST_IDENTIFIER']=='iPad6,8'
            old=b'<key>GUI_ATLAS_OVERRIDE</key>\n\t<string></string>'
            assert plain.count(old)==1
            updated=plain.replace(old,b'<key>GUI_ATLAS_OVERRIDE</key>\n\t<string>2048x1536</string>')
            new_profile=plistlib.loads(updated)
            assert {k for k in profile if profile[k]!=new_profile[k]}=={'GUI_ATLAS_OVERRIDE'}
            encoded=eds_crypt(updated);assert eds_crypt(encoded)==updated
            modified[key]=encoded
            direct=APP+'res/eds/iPhone14,6.plist';assert direct not in source.namelist();added[direct]=encoded
            manifest['eds_changes']={'GUI_ATLAS_OVERRIDE':'2048x1536','fallback_modified':True,'direct_profile_added':'iPhone14,6.plist','internal_identity_preserved':'iPad6,8','other_settings_changed':False}
        manifest['binary_patch_operations']=ops;manifest['dependency']=dependency
        # The app bundle's old resource seal is invalid after these edits; the
        # user's signing tool must generate a fresh device-authorized signature.
        omitted=[n for n in source.namelist() if n.startswith(APP+'_CodeSignature/')]
        manifest['removed_stale_resource_seals']=omitted
        added[APP+'RR3-SE3-Test.json']=json.dumps(manifest,indent=2).encode()
        added[APP+'RR3Diagnostics-Fishhook-LICENSE.txt']=(ROOT/'LICENSE.fishhook').read_bytes()
        infos=source.infolist();ordered=sorted(infos,key=lambda i:i.header_offset)
        ends={info.filename:(ordered[n+1].header_offset if n+1<len(ordered) else source.start_dir) for n,info in enumerate(ordered)}
        with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as target:
            target.comment=source.comment
            for item in infos:
                if item.filename in omitted:continue
                if item.filename in modified:target.writestr(copy.copy(item),modified[item.filename])
                else:raw_copy(source,target,item,ends[item.filename])
            for path,data in added.items():
                item=zipfile.ZipInfo(path,(2026,10,13,12,0,0));item.compress_type=zipfile.ZIP_DEFLATED
                item.create_system=3;item.external_attr=(0o100755 if path.endswith('.dylib') else 0o100644)<<16
                target.writestr(item,data)
        print(f'Created {name}; verifying archive and entry preservation...',flush=True)
        with zipfile.ZipFile(out) as result:
            assert result.testzip() is None
            expected_names=(set(source.namelist())-set(omitted))|set(added)
            assert len(result.namelist())==len(expected_names) and set(result.namelist())==expected_names
            preserved=0
            for item in infos:
                n=item.filename
                if n in omitted or n in modified:continue
                got=result.getinfo(n)
                assert (got.CRC,got.file_size,got.compress_size)==(item.CRC,item.file_size,item.compress_size),n
                preserved+=1
            for path,data in (modified|added).items():assert result.read(path)==data,path
            verify_binary=result.read(APP+'RealRacing3')
            assert macho_uuid(verify_binary)==UUID
            if hd:assert verify_binary[CAVE:CAVE+len(stub())]==stub()
            assert result.read(APP+'Frameworks/AppData.dylib')==source.read(APP+'Frameworks/AppData.dylib')
            assert result.read(APP+'Frameworks/iPASTORERR3Fix.dylib')==source.read(APP+'Frameworks/iPASTORERR3Fix.dylib')
        manifest['verification']={'zip_crc':'passed','unchanged_entries_preserved':preserved,'modified_and_added_bytes_verified':True,'main_adhoc_signature':'verified','helper_adhoc_signature':'verified','original_import_helpers_preserved':True}
    manifest['output_file']=name;manifest['output_size']=out.stat().st_size;manifest['output_sha256']=sha(out)
    (OUTPUT/(name+'.report.json')).write_text(json.dumps(manifest,indent=2))
    return manifest

def main():
    import argparse
    global INPUT,OUTPUT,BUILD,STUBS,SDK,SOURCE_SHA256
    parser=argparse.ArgumentParser(description='Build the exact-build RR3 iPhone SE 3 GUI resource fix. Original files are never modified.')
    parser.add_argument('--input',required=True,type=pathlib.Path,help='Original RR3 DevOps v1.0 Production Quality IPA (before re-signing)')
    parser.add_argument('--output-dir',type=pathlib.Path,default=ROOT/'dist')
    parser.add_argument('--build-dir',type=pathlib.Path,default=ROOT/'build')
    parser.add_argument('--variant',choices=['hd','diagnostic','both'],default='hd')
    parser.add_argument('--check-only',action='store_true',help='Validate the input and run native/ARM64 tests without building an IPA')
    args=parser.parse_args()
    INPUT=args.input.expanduser().resolve()
    OUTPUT=args.output_dir.expanduser().resolve()
    BUILD=args.build_dir.expanduser().resolve();STUBS=BUILD/'stubs'
    if not INPUT.is_file():raise FileNotFoundError(INPUT)
    if INPUT.parent==OUTPUT:raise ValueError('Use a separate output directory, not the input directory')
    with zipfile.ZipFile(INPUT) as z:
        binary=z.read(APP+'RealRacing3')
        if hashlib.sha256(binary).hexdigest()!=EXPECTED_MAIN_SHA256:
            raise ValueError('Unsupported executable: use the exact original RR3 DevOps v1.0 Production Quality IPA, not a re-signed or already patched copy')
        if macho_uuid(binary)!=UUID:raise ValueError('Unsupported Mach-O UUID')
        if hashlib.sha256(z.read(APP+'res/eds/iPhone.plist')).hexdigest()!=EXPECTED_EDS_SHA256:
            raise ValueError('Unsupported fallback EDS profile')
        if plistlib.loads(z.read(APP+'Info.plist')).get('CFBundleShortVersionString')!='14.0.1':
            raise ValueError('Unsupported game version')
    modes=['HD'] if args.variant=='hd' else ['Diagnostic'] if args.variant=='diagnostic' else ['Diagnostic','HD']
    if not args.check_only:
        for mode in modes:
            p=OUTPUT/f'RR3-SE3-{mode}-Test-v1.ipa'
            if p.exists():raise FileExistsError(f'Refusing to overwrite existing output: {p}')
    SOURCE_SHA256=sha(INPUT)
    SDK=run(['xcrun','--sdk','macosx','--show-sdk-path']).strip()
    BUILD.mkdir(parents=True,exist_ok=True);STUBS.mkdir(exist_ok=True)
    print('Input executable, EDS profile and version verified.',flush=True)
    native_test()
    run([sys.executable,str(ROOT/'test_patch.py'),'--input',str(INPUT),'--report',str(BUILD/'arm64_gate_tests.json')])
    if args.check_only:
        print('All checks passed. No IPA produced.');return
    helper=compile_helper();OUTPUT.mkdir(parents=True,exist_ok=True)
    results=[make_ipa(helper,mode) for mode in modes]
    if sha(INPUT)!=SOURCE_SHA256:raise RuntimeError('Input integrity changed')
    (OUTPUT/'SHA256SUMS.txt').write_text(''.join(f'{r["output_sha256"]}  {r["output_file"]}\n' for r in results))
    print(json.dumps([dict(file=r['output_file'],size=r['output_size'],sha256=r['output_sha256'],verified=r['verification']) for r in results],indent=2))

if __name__=='__main__':main()
