Release History
---------------

0.3.3 (2016-10-17)
++++++++++++++++++

**Bug fixes**

- Fixed ``AttributeError: 'module' object has no attribute 'client'``.


0.3.2 (2016-03-21)
++++++++++++++++++

**Improvement**

- Change ``get_settled_payments`` to return a list of Payment objects.


0.3.1 (2016-03-21)
++++++++++++++++++

**Bug fixes**

- Add ``get_settled_payments`` to ``ezi/__init__.py``.


0.3 (2016-03-16)
++++++++++++++++

**Improvements**

 - Add a ``get_settled_payments`` function.


0.2.7 (2015-09-14)
++++++++++++++++++

**Improvements**

 - Strip non-digit characters from credit card number.


0.2.6 (2015-08-13)
++++++++++++++++++

**Improvements**

 - Handle ``suds.WebFault`` and translate to an ``EzidebitError``.


0.2.5 (2015-07-31)
++++++++++++++++++

**Improvements**

 - Add ``HISTORY.rst``.


0.2.4 (2015-07-31)
++++++++++++++++++

**Improvements**

 - Add syntax highlighting to ``README.rst``.
