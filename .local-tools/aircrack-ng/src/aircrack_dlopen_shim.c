#define _GNU_SOURCE

#include <dlfcn.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void *(*real_dlopen_fn)(const char *filename, int flags);

static int is_aircrack_plugin_path(const char *filename) {
  const char *base;

  if (filename == NULL) {
    return 0;
  }

  base = strrchr(filename, '/');
  base = base == NULL ? filename : base + 1;

  if (strncmp(base, "libaircrack-", 12) != 0) {
    return 0;
  }

  return strstr(base, ".so") != NULL;
}

void *dlopen(const char *filename, int flags) {
  const char *root;
  const char *base;
  char rewritten[PATH_MAX];

  if (real_dlopen_fn == NULL) {
    real_dlopen_fn = dlsym(RTLD_NEXT, "dlopen");
    if (real_dlopen_fn == NULL) {
      fputs("aircrack shim: failed to resolve real dlopen\n", stderr);
      abort();
    }
  }

  root = getenv("AIRCRACK_LOCAL_ROOT");
  if (root != NULL && is_aircrack_plugin_path(filename)) {
    base = strrchr(filename, '/');
    base = base == NULL ? filename : base + 1;

    if (snprintf(rewritten, sizeof(rewritten),
                 "%s/usr/lib/x86_64-linux-gnu/%s", root, base) <
        (int)sizeof(rewritten)) {
      return real_dlopen_fn(rewritten, flags);
    }
  }

  return real_dlopen_fn(filename, flags);
}
