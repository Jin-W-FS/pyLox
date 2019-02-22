# pyLox
Implement [the Lox Language](http://www.craftinginterpreters.com/the-lox-language.html) in python.

Data-flow graph:
```
                                          Interpreter
                                         +-----------> interpreting
                                         |
                                         |                  ^
                                         |                  |
+--------+ Scanner +--------+ Parser +-----+ Resolver +------------+
| Source |-------->| Tokens |------->+ AST |--------->|  Bindings  |
+--------+         +--------+        +-----+          +------------+
                                         |                  |
                                         |                  v
                                         |  Compiler  +-----------+ VM
                                         +----------->+ Byte Code |----> running
                                                      +-----------+
```

Language features and examples:
```c++
// base types: boolean, number and string
assert true == !false;
assert 2 - 1 >= 0;
assert "cat" != "dog";

// variables and assignments
var imAVariable = "here is my value";
var iAmNil;
imAVariable = -5;
print imAVariable;	// -5

// conditional statement and loops
var i = 0;
while (i < 10) {
  for (var j = 0; j < 10; j = j + 1) {
    if (i == j) continue;
    if (i + j == 10) printf("%d + %d == 10\n", i, j);
  }
  i = i + 1;
}

// functions and closures
fun odd; // early declaration
fun even(i) {
  if (i < 0) return even(-i);
  if (i == 0) return true;
  return odd(i - 1);
}
fun odd(i) {
  return even(i - 1);
}
print even(10);		// true

fun fib(i) {
  if (i < 0) return 0;
  if (i <= 1) return 1;
  return fib(i - 1) + fib(i - 2);
}
print fib(5);		// 8

fun counter(i) {
  fun count() {
    i = i + 1;
    return i;
  }
  return count;
}
var cnt1 = counter(0);
for (var i = 0; i < 3; i = i + 1) {
	print cnt1();		// 1 2 3
}

print lambda(a, b) { a + b } (5, 7);	// 12

// classes
class Breakfast {
  init(meat, bread) {
    this.meat = meat;
    this.bread = bread;
  }
  cook() {
    print "Cook done!";
  }
  serve(who) {
    print "Enjoy your " + this.meat + " and " +
        this.bread + ", " + who + ".";
  }
}

var baconAndToast = Breakfast("bacon", "toast");
baconAndToast.serve("Dear Reader");	// "Enjoy your bacon and toast, Dear Reader."

class Brunch < Breakfast {
  init(meat, bread, drink) {
    super.init(meat, bread);
    this.drink = drink;
  }
  cook() {
    print "Eggs a-fryin'!";
  }
  askDrink() {
    print "How about a Blood Mary?";
  }
}

var benedict = Brunch("ham", "toast", "English muffin");
benedict.serve("Noble Reader");	// "Enjoy your ham and toast, Noble Reader."
benedict.cook();				// "Eggs a-fryin'!"
benedict.askDrink();			// "How about a Blood Mary?"
```
