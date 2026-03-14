
myabs
==============================================

Purpose
----------------

Returns the absolute value of *x*.

Format
----------------
.. function:: y = myabs(x)

    :param x: Input data.
    :type x: NxK matrix

    :return y: Contains the absolute values of *x*.

    :rtype y: NxK matrix

Examples
----------------

::

    x = { -1, 2, -3 };
    y = myabs(x);

The code above assigns *y* to:

::

    y = 1
        2
        3
