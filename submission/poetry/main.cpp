#include <iostream>

int main(int argc, char** argv) {
  if(argc != 2) {
    std::cout << "USAGE: " << argv[0] << " [style]\n";
    std::exit(1);
  }

  std::string op(argv[1]);
  if(op == "limerick") {
    std::cout
    << "There wis a young lassie named Menzies,\n"
    << "That askit her aunt whit this thenzies.\n"
    << "  Said her aunt wi a gasp,\n"
    << "  \"Ma dear, it's a wasp,\n"
    << "An you're haudin the end whaur the stenzies!\"\n";

  }
  else if(op == "sonnet") {
    std::cout
    << "Let me not to the marriage of true minds\n"
    << "Admit impediments, love is not love\n"
    << "Which alters when it alteration finds,\n"
    << "Or bends with the remover to remove.\n"
    << "O no, it is an ever fixed mark\n"
    << "That looks on tempests and is never shaken;\n"
    << "It is the star to every wand'ring bark,\n"
    << "Whose worth's unknown although his height be taken.\n"
    << "Love's not time's fool, though rosy lips and cheeks\n"
    << "Within his bending sickle's compass come,\n"
    << "Love alters not with his brief hours and weeks,\n"
    << "But bears it out even to the edge of doom:\n"
    << "  If this be error and upon me proved,\n"
    << "  I never writ, nor no man ever loved.\n";
  }
  else {
    std::cerr << "I don't do " << op << "s.\n";
  }

  return 0;
}
