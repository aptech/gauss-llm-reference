Broken References Test Fixture
===============================

This file contains various broken references for testing the fixer module.

Paragraph with broken ref
--------------------------

The :func:`plotbar` function draws a bar chart. Use it for visualization.

The :func:`olsmt` function is correct and should not be flagged.

Seealso directive
-----------------

.. seealso::

   :func:`plotbar` for bar charts
   :func:`olsmt` for regression

Code block (should NOT be fixed)
---------------------------------

Example usage::

   // This is a code block
   x = plotbar(data);
   :func:`plotbar`

.. code-block:: gauss

   // Another code block
   :func:`plotbar`

Table (should NOT be fixed)
---------------------------

+------------+------------------+
| Function   | Description      |
+============+==================+
| :func:`plotbar` | Bar chart   |
+------------+------------------+

No close match
--------------

The :func:`xyznonexistent` function does not exist.

Ambiguous match
---------------

The :func:`plo` function is ambiguous.
