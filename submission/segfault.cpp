#include "crasher.h"

void segfault() {
  int* boom = nullptr;
  *boom = 42;
}
