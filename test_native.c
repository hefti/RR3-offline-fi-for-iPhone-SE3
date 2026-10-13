#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <assert.h>
extern int rr3_diag_test_start(const char *);
extern int rr3_diag_test_relevant(const char *);
extern const void *CFStringCreateWithCString(const void *,const char *,unsigned);
extern void CFRelease(const void *);
extern void NSLog(const void *,...);
int main(int argc,char **argv) {
    assert(argc==2);
    assert(rr3_diag_test_start(argv[1])==0);
    char path[2048];snprintf(path,sizeof(path),"%s/Documents/gui_assets/missing.pvr.z",argv[1]);
    errno=0;assert(fopen(path,"rb")==NULL);assert(errno==ENOENT);
    errno=0;assert(access(path,F_OK)==-1);assert(errno==ENOENT);
    struct stat st;errno=0;assert(stat(path,&st)==-1);assert(errno==ENOENT);
    snprintf(path,sizeof(path),"%s/Documents/asset_list_test.txt",argv[1]);
    int fd=open(path,O_CREAT|O_WRONLY,0600);assert(fd>=0);assert(write(fd,"ok",2)==2);close(fd);
    FILE *f=fopen(path,"rb");assert(f);assert(fgetc(f)=='o');fclose(f);
    assert(stat(path,&st)==0 && st.st_size==2);
    const void *fmt=CFStringCreateWithCString(NULL,"Asset request %d: gui_assets/960x640/test",0x08000100);
    NSLog(fmt,7);CFRelease(fmt);
    assert(rr3_diag_test_relevant("Downloading assets"));
    assert(!rr3_diag_test_relevant("Asset token=private"));
    assert(!rr3_diag_test_relevant("ordinary unrelated message"));
    puts("Native main-image hooks passed: fopen/open/access/stat/NSLog, errno and file semantics");
    return 0;
}
