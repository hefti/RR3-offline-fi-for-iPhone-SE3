/* Local-only RR3 diagnostic helper. No network code and no save/cache writes.
 * fishhook is restricted to the main executable's imports, never other images.
 * Game text pages are never modified at runtime. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <strings.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <sys/stat.h>
#include <dlfcn.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include "fishhook.h"

/* Public CoreFoundation ABI only; no private frameworks or SDK objects bundled. */
typedef const void *CFStringRef;
extern CFStringRef CFStringCreateWithCString(const void *, const char *, unsigned);
extern CFStringRef CFStringCreateWithFormatAndArguments(const void *, const void *, CFStringRef, va_list);
extern long CFStringGetLength(CFStringRef);
extern unsigned char CFStringGetCString(CFStringRef, char *, long, unsigned);
extern void CFRelease(const void *);
#define UTF8 0x08000100U
#define LOG_LIMIT (8U*1024U*1024U)

static int log_fd = -1;
static unsigned long log_bytes;
static pthread_mutex_t log_lock = PTHREAD_MUTEX_INITIALIZER;
static FILE *(*real_fopen)(const char *, const char *);
static int (*real_open)(const char *, int, ...);
static int (*real_access)(const char *, int);
static int (*real_stat)(const char *, struct stat *);
static int (*real_lstat)(const char *, struct stat *);
static void (*real_nslog)(CFStringRef, ...);
static CFStringRef literal_object_format;
static char home_prefix[1024];
static intptr_t game_slide;
static int known_game;

static void log_line(const char *kind, const char *msg) {
    int saved = errno;
    if (log_fd >= 0) {
        char line[8192];
        int n = snprintf(line, sizeof(line), "%lld\t%s\t%s\n", (long long)time(NULL), kind, msg ? msg : "(null)");
        if (n > 0) {
            size_t size = (size_t)n < sizeof(line) ? (size_t)n : sizeof(line)-1;
            if (size && line[size-1] != '\n') line[size-1] = '\n';
            pthread_mutex_lock(&log_lock);
            if (log_bytes + size <= LOG_LIMIT) {
                size_t done=0;
                while (done < size) {
                    ssize_t w=write(log_fd, line+done, size-done);
                    if (w < 0 && errno==EINTR) continue;
                    if (w<=0) break;
                    done+=(size_t)w;
                }
                log_bytes+=(unsigned long)done;
            }
            pthread_mutex_unlock(&log_lock);
        }
    }
    errno = saved;
}

static int asset_path(const char *s) {
    return s && (strstr(s,"gui_assets/") || strstr(s,"asset_list") || strstr(s,"/res/eds/") || strstr(s,"/res/feats/"));
}
static void log_file(const char *api, const char *path, int success, int error) {
    if (!asset_path(path)) return;
    const char *visible=path;
    size_t home_len=strlen(home_prefix);
    if (home_len && strncmp(path,home_prefix,home_len)==0 && path[home_len]=='/') visible=path+home_len;
    char msg[4096];
    snprintf(msg,sizeof(msg),"%s\t%s\terrno=%d\t%s",api,success?"OK":"MISSING_OR_ERROR",success?0:error,visible);
    log_line("FILE",msg);
}
static FILE *tracked_fopen(const char *p, const char *mode) {
    FILE *v=real_fopen(p,mode); int saved=errno;
    log_file("fopen",p,v!=NULL,saved); errno=saved; return v;
}
static int tracked_open(const char *p, int flags, ...) {
    int v;
    if (flags&O_CREAT) { va_list a; va_start(a,flags); int mode=va_arg(a,int); va_end(a); v=real_open(p,flags,mode); }
    else v=real_open(p,flags);
    int saved=errno; log_file("open",p,v>=0,saved); errno=saved; return v;
}
static int tracked_access(const char *p, int mode) {
    int v=real_access(p,mode); int saved=errno; log_file("access",p,v==0,saved); errno=saved; return v;
}
static int tracked_stat(const char *p, struct stat *out) {
    int v=real_stat(p,out); int saved=errno; log_file("stat",p,v==0,saved); errno=saved; return v;
}
static int tracked_lstat(const char *p, struct stat *out) {
    int v=real_lstat(p,out); int saved=errno; log_file("lstat",p,v==0,saved); errno=saved; return v;
}
static int relevant_message(const char *s) {
    if (strcasestr(s,"token") || strcasestr(s,"password") || strcasestr(s,"authorization") || strcasestr(s,"cookie") || strcasestr(s,"receipt")) return 0;
    const char *keys[]={"asset","download","cache","res base","res order","settings file","device description","gui","screen","disk space","initial","2048x1536","960x640","480x320"};
    for(unsigned i=0;i<sizeof(keys)/sizeof(keys[0]);i++) if(strcasestr(s,keys[i])) return 1;
    return 0;
}
static void tracked_nslog(CFStringRef format, ...) {
    int saved=errno;
    va_list args; va_start(args,format);
    CFStringRef rendered=format?CFStringCreateWithFormatAndArguments(NULL,NULL,format,args):NULL;
    va_end(args);
    if(rendered) {
        long length=CFStringGetLength(rendered);
        if(length>=0 && length<=16384) {
            size_t capacity=(size_t)length*4+1;
            char *text=malloc(capacity);
            if(text) {
                if(CFStringGetCString(rendered,text,(long)capacity,UTF8) && relevant_message(text)) log_line("ENGINE",text);
                free(text);
            }
        }
        /* Preserve the engine's existing system logging, with a literal %@ format. */
        if(real_nslog && literal_object_format) real_nslog(literal_object_format,rendered);
        CFRelease(rendered);
    }
    errno=saved;
}

static int verify_game(const struct mach_header_64 *h) {
    static const unsigned char uuid[16]={0x06,0xed,0x5b,0x50,0xc4,0x4c,0x3b,0x69,0xa5,0x84,0x07,0x01,0xb8,0xa8,0x84,0x51};
    if(!h || h->magic!=MH_MAGIC_64 || h->sizeofcmds>65536) return 0;
    const unsigned char *p=(const unsigned char *)(h+1),*end=p+h->sizeofcmds;
    for(unsigned i=0;i<h->ncmds;i++) {
        if(p+8>end) return 0;
        const struct load_command *c=(const struct load_command *)p;
        if(c->cmdsize<8 || p+c->cmdsize>end) return 0;
        if(c->cmd==LC_UUID && c->cmdsize>=24) return memcmp(p+8,uuid,16)==0;
        p+=c->cmdsize;
    }
    return 0;
}

static void *snapshot_worker(void *unused) {
    (void)unused;
    volatile uint8_t *enable=(volatile uint8_t *)(game_slide+0x1031d0f18ULL);
    volatile uint32_t *limits=(volatile uint32_t *)(game_slide+0x103251f14ULL);
    uint32_t old_w=~0U,old_h=~0U;
    for(unsigned i=0;i<120;i++) {
        *enable=1; /* Only the existing engine log gate; no developer/cheat flags. */
        uint32_t w=limits[0],h=limits[1];
        if(w!=old_w || h!=old_h || i==119) {
            char msg[256];snprintf(msg,sizeof(msg),"frame-derived asset limits=%ux%u; elapsed=%us; HD ceiling is local to GUI list filter",w,h,i);
            log_line("STATE",msg);old_w=w;old_h=h;
        }
        sleep(1);
    }
    log_line("STATE","startup snapshot complete; file and engine tracing remain active (8 MiB limit)");
    return NULL;
}

static int start_logging(const char *root) {
    if(!root || strlen(root)>900) return -1;
    snprintf(home_prefix,sizeof(home_prefix),"%s",root);
    char documents[1200],folder[1200],path[1400];
    snprintf(documents,sizeof(documents),"%s/Documents",root); mkdir(documents,0700);
    snprintf(folder,sizeof(folder),"%s/RR3-Diagnostics",documents); mkdir(folder,0700);
    snprintf(path,sizeof(path),"%s/session-%lld-%d.log",folder,(long long)time(NULL),getpid());
    log_fd=open(path,O_WRONLY|O_CREAT|O_APPEND,0600);
    if(log_fd<0) return -1;
    real_fopen=dlsym(RTLD_DEFAULT,"fopen"); real_open=dlsym(RTLD_DEFAULT,"open");
    real_access=dlsym(RTLD_DEFAULT,"access"); real_stat=dlsym(RTLD_DEFAULT,"stat"); real_lstat=dlsym(RTLD_DEFAULT,"lstat");
    real_nslog=dlsym(RTLD_DEFAULT,"NSLog");
    literal_object_format=CFStringCreateWithCString(NULL,"%@",UTF8);
    if(!real_fopen || !real_open || !real_access || !real_stat || !real_lstat || !real_nslog || !literal_object_format) {
        log_line("ERROR","required public symbol unavailable; import hooks disabled");return -1;
    }
    struct rebinding hooks[]={
        {"fopen",tracked_fopen,NULL},{"open",tracked_open,NULL},{"access",tracked_access,NULL},
        {"stat",tracked_stat,NULL},{"lstat",tracked_lstat,NULL},{"NSLog",tracked_nslog,NULL}
    };
    int result=rebind_symbols_image((void *)_dyld_get_image_header(0),_dyld_get_image_vmaddr_slide(0),hooks,sizeof(hooks)/sizeof(hooks[0]));
    log_line("START","RR3 SE3 test v1; main-image file/NSLog tracing requested; no network uploads");
    return result;
}

#ifdef RR3_DIAG_TEST
int rr3_diag_test_start(const char *root) { return start_logging(root); }
int rr3_diag_test_relevant(const char *s) { return relevant_message(s); }
#else
__attribute__((constructor)) static void init_rr3_diagnostics(void) {
    const struct mach_header_64 *header=(const struct mach_header_64 *)_dyld_get_image_header(0);
    known_game=verify_game(header);
    if(!known_game) return;
    game_slide=_dyld_get_image_vmaddr_slide(0);
    if(start_logging(getenv("HOME"))<0) return;
    char mode[128];
    uint32_t instruction=*(const uint32_t *)(game_slide+0x100680b24ULL);
    snprintf(mode,sizeof(mode),"GUI filter site=%08x; %s",instruction,(instruction&0xfc000000U)==0x14000000U?"HD detour present":"original filter (control)");
    log_line("BUILD",mode);
    *(volatile uint8_t *)(game_slide+0x1031d0f18ULL)=1;
    pthread_t t;
    if(pthread_create(&t,NULL,snapshot_worker,NULL)==0) pthread_detach(t);
    else log_line("ERROR","snapshot worker unavailable; file/engine hooks remain active");
}
#endif
