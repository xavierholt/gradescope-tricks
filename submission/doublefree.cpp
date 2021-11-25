#include "crasher.h"

void doublefree() {
  int* ptr = new int(42);
  delete ptr;
  delete ptr;
}
