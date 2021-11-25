#include "crasher.h"

#include <iostream>


int main(int argc, char** argv) {
  if(argc != 2) {
    std::cout << "USAGE: " << argv[0] << " segfault|doublefree\n";
    std::exit(1);
  }

  std::string op(argv[1]);
  if(op == "doublefree") {
    doublefree();
  }
  else if(op == "segfault") {
    segfault();
  }
  else if(op == "memleak") {
    memleak();
  }
  else {
    std::cout << "Unknown operation: " << op << "\n";
    return 1;
  }

  return 0;
}
