#include "crasher.h"

void memleak() {
  new int(42);
}
