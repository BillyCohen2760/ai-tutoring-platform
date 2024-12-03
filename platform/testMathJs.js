const math = require('mathjs');

// Define the expressions
const expr1 = '5 n m (2 m - 5 n + 3)'; //'4pq(2p + 3q - 1)'; // const expr1 = '2 m n^2 (m^2 - 5 m + 2)';
const expr2 = '5 m n (2 m - 5 n + 3)'; //'4p q(2p + 3q - 1)'; // const expr2 = '2 m (m^2 - 5 m + 2) n^2';

// Simplify both expressions
const simplified1 = math.simplify(expr1);
const simplified2 = math.simplify(expr2);

// Convert the simplified expressions to strings, then split and sort terms
const sorted1 = simplified1.toString().split(' ').sort().join(' ');
const sorted2 = simplified2.toString().split(' ').sort().join(' ');

console.log('Simplified Expr1:', sorted1.toString());
console.log('Simplified Expr2:', sorted2.toString());

// Check if the sorted expressions are equal
const areEqual = sorted1 === sorted2;

console.log('Simplified Expr1:', simplified1.toString());
console.log('Simplified Expr2:', simplified2.toString());
console.log('Are they equal?', areEqual);
