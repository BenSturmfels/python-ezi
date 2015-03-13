===========
 Python Ezi
===========

`ezi` is a Python interface to the Ezidebit payment gateway.

Note that the current API relies on a Django-like User object. We'll remove that
requirement in future releases.

Example
-------

To add a new direct debit by bank account or credit card::

    >>> from ezi import add_bank_debit, add_card_debit, add_payment, clear_schedule
    >>> from django.contrib.auth.models import User
    >>> user = User.objects.get(pk=399998)

    >>> add_bank_debit(
    ...     user, 'invoice-99', '200', '2015-03-01', 'Mr Example', '111111',
    ...     '123456',
    ...    'https://api.demo.ezidebit.com.au/v3-3/pci?singleWsdl',
    ...    'YOUR DIGITAL KEY')

    >>> add_card_debit(
    ...     user, 'invoice-99', '200', '2015-03-01', 'Mr Example',
    ...     '4444333322221111', '01/16',
    ...    'https://api.demo.ezidebit.com.au/v3-3/pci?singleWsdl',
    ...    'YOUR DIGITAL KEY')

    >>> clear_schedule(
    ...     608725,
    ...    'https://api.demo.ezidebit.com.au/v3-3/nonpci?singleWsdl',
    ...    'YOUR DIGITAL KEY')

    >>> add_payment(
    ...     user, 'invoice-99', '200', '2015-03-01',
    ...    'https://api.demo.ezidebit.com.au/v3-3/nonpci?singleWsdl',
    ...    'YOUR DIGITAL KEY')
