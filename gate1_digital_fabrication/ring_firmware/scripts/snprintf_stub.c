#include <stddef.h>
int ring_snprintf_stub(char *buf, size_t n, const char *fmt, ...) {
  (void)fmt;
  if (!buf || n==0) return 0;
  const char *s = "ok"; size_t i=0;
  for (; s[i] && i+1<n; i++) buf[i]=s[i];
  buf[i]=0; return (int)i;
}
