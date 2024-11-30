const math = require('mathjs');

// Define the expressions
const expr1 = '3x + 4';
const expr2 = '4 + 3x';

// Simplify both expressions
const simplified1 = math.simplify(expr1).toString();
const simplified2 = math.simplify(expr2).toString();

// Compare the simplified forms
const areEqual = simplified1 === simplified2;

console.log('Simplified Expr1:', simplified1); // 3 * x + 4
console.log('Simplified Expr2:', simplified2); // 3 * x + 4
console.log('Are they equal?', areEqual);      // true
