
addition
==============================================

Purpose
----------------

Adds two matrices, vectors, or scalars element-by-element.

Format
----------------

::

    y = a + b

Parameters
----------------

    :param a: Left operand.
    :type a: matrix, vector, or scalar

    :param b: Right operand.
    :type b: matrix, vector, or scalar

Returns
----------------

    :return y: Element-by-element sum of *a* and *b*.

    :rtype y: matrix

Examples
----------------

::

    a = { 1, 2, 3 };
    b = { 10, 20, 30 };
    y = a + b;

Remarks
-------

- If both operands are matrices, they must be conformable.
