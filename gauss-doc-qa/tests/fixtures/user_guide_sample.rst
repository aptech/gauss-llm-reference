Data Handling in GAUSS
=====================

This chapter covers how to load, manipulate, and save data in GAUSS.

Loading Data
------------

GAUSS can load data from many file formats including CSV, Excel, and
Stata files. Use the ``loadd`` function to read data:

.. code-block:: gauss

   data = loadd("myfile.csv");

The ``loadd`` function automatically detects the file format based on
the file extension.

Filtering and Selection
-----------------------

Once data is loaded, you can filter rows using ``selif``. For example,
to run OLS on a subset of the data, first filter it:

.. code-block:: gauss

   subset = selif(data, data[., "Age"] .>= 18);

You can then pass the subset to your estimation procedure.

Saving Results
--------------

After running your analysis, save results with ``saved``:

.. code-block:: gauss

   saved(results, "output.csv");
