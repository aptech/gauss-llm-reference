Getting Started with GAUSS
==========================

GAUSS is a matrix programming language designed for statistical analysis,
econometrics, and data science. It has been developed by Aptech Systems
since 1984.

Your First Program
------------------

Let's start with a simple example. Open GAUSS and type the following:

.. code-block:: gauss

   x = { 1 2 3, 4 5 6 };
   print x;

This creates a 2x3 matrix and prints it to the screen.

Working with Procedures
-----------------------

GAUSS uses proc and retp to define and return from functions:

.. code-block:: gauss

   proc (1) = addOne(x);
       retp(x + 1);
   endp;

   y = addOne(5);
   print y;
