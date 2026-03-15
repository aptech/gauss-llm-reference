sampleFunc
==========

.. function:: y = sampleFunc(x, n)

   :param x: NxK matrix, input data.
   :type x: matrix
   :param n: scalar, number of samples to draw.
   :type n: scalar

Purpose
-------

Draws a random sample of *n* rows from the input matrix *x*.

Format
------

.. code-block:: gauss

   y = sampleFunc(x, n);

Parameters
----------

*x* -- NxK matrix, the data to sample from.

*n* -- scalar, the number of rows to draw.

Examples
--------

.. code-block:: gauss

   x = rndn(100, 3);
   y = sampleFunc(x, 10);
   print rows(y);
