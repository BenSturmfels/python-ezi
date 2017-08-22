import datetime
import decimal
import unittest

from ezi import debit


class PaymentDecimalTestCase(unittest.TestCase):
    def test_payment_converted_to_decimals(self):
        payment = ObjDict({
            'BankFailedReason': None,
            'BankReceiptID': None,
            'BankReturnCode': '0',
            'CustomerName': 'Paul Person',
            'DebitDate': datetime.datetime(2017, 1, 1, 0, 0, 0),
            'EzidebitCustomerID': '12345678',
            'InvoiceID': '3080698',
            'PaymentAmount': 31.25,
            'PaymentID': 'SCHEDULED123456789',
            'PaymentMethod': 'CR',
            'PaymentReference': 'order-1234',
            'PaymentSource': 'SCHEDULED',
            'PaymentStatus': 'S',
            'ScheduledAmount': 31.25,
            'SettlementDate': datetime.datetime(2017, 1, 1, 0, 0, 0),
            'TransactionFeeClient': 0.88,
            'TransactionFeeCustomer': 0.00,
            'TransactionTime': None,
            'YourGeneralReference': '1234567',
            'YourSystemReference': '1234567'})

        expected = ObjDict({
            'BankFailedReason': None,
            'BankReceiptID': None,
            'BankReturnCode': '0',
            'CustomerName': 'Paul Person',
            'DebitDate': datetime.datetime(2017, 1, 1, 0, 0, 0),
            'EzidebitCustomerID': '12345678',
            'InvoiceID': '3080698',
            'PaymentAmount': decimal.Decimal('31.25'),
            'PaymentID': 'SCHEDULED123456789',
            'PaymentMethod': 'CR',
            'PaymentReference': 'order-1234',
            'PaymentSource': 'SCHEDULED',
            'PaymentStatus': 'S',
            'ScheduledAmount': decimal.Decimal('31.25'),
            'SettlementDate': datetime.datetime(2017, 1, 1, 0, 0, 0),
            'TransactionFeeClient': decimal.Decimal('0.88'),
            'TransactionFeeCustomer': decimal.Decimal('0.00'),
            'TransactionTime': None,
            'YourGeneralReference': '1234567',
            'YourSystemReference': '1234567'})

        fixed_payment = debit._fix_payment_floats(payment)
        self.assertEqual(fixed_payment, expected)


class ObjDict(dict):
    def __init__(self, d):
        self.update(d)

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


if __name__ == '__main__':
    unittest.main()
