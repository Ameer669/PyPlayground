#include <iostream>

class A {
public:
    void showA() { std::cout << "Class A\n"; }
};

class B : public A {
public:
    void showB() { std::cout << "Class B\n"; }
};

class C : public B {
public:
    void showC() { std::cout << "Class C\n"; }
};

int main() {
    C c;
    c.showA();
    c.showB();
    c.showC();
    
    // Keep the console window open
    std::cout << "\nPress Enter to exit...";
    std::cin.get();
    return 0;
}