var x = 0;
var y = 8;

function print(i) {
} ;

while (x < 10) {
    if (x == y) {
        break;
    }
    x ++ ;
    if (x < 2) {
        continue;
    }
    print(x);
}
