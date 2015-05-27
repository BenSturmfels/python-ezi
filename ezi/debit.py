import logging
import urllib

import suds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONNECTION_ERROR_MSG = 'Could not connect to Ezidebit payment service.'

class EzidebitError(RuntimeError):
    pass


class EzidebitClient:
    """Set up Ezidebit Suds SOAP client and handle connection errors."""
    def __init__(self, wsdl):
        self.wsdl = wsdl

    def __enter__(self):
        """Set up Suds SOAP client and handle related connection errors."""
        try:
            client = suds.client.Client(self.wsdl)
        except urllib.error.URLError as err:
            logger.error(err)
            raise EzidebitError(CONNECTION_ERROR_MSG)
        return client

    def __exit__(self, type, value, traceback):
        """Handle any connection errors in context manager body."""
        if type is urllib.error.URLError:
            logger.error(value)
            raise EzidebitError(CONNECTION_ERROR_MSG)


def get_customer_details(user_id, wsdl_pci, key):
    """Show details for an existing Ezidebit account.

    user_id is our reference to the account.

    """
    with EzidebitClient(wsdl_pci) as client:
        details = client.service.GetCustomerDetails(
            # All these fields required to avoid vaugue error message.
            DigitalKey=key,
            EziDebitCustomerID='',
            YourSystemReference=user_id,
        )
    logger.debug(details)
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)
    return details.Data


def add_bank_debit(
        user, payment_ref, cents, due_date, acct_name, bsb, acct_number,
        wsdl_pci, key):
    """Add/update account with Ezidebit and schedule a bank debit.

    Existing accounts and payment methods are updated. Existing scheduled
    payments are retained.

    """
    with EzidebitClient(wsdl_pci) as client:
        details = client.service.AddBankDebit(
            # All these fields required to avoid vaugue error message.
            DigitalKey=key,
            YourSystemReference=user.username,
            YourGeneralReference='',
            LastName=user.last_name,
            FirstName=user.first_name,
            EmailAddress=user.email,
            MobilePhoneNumber='',
            PaymentReference=payment_ref,
            BankAccountName=acct_name,
            BankAccountBSB=bsb,
            BankAccountNumber=acct_number,
            PaymentAmountInCents=cents,
            DebitDate=due_date,
            SmsPaymentReminder='NO',
            SmsFailedNotification='NO',
            SmsExpiredCard='NO',
        )
    logger.debug(details)
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)


def add_card_debit(
        user, payment_ref, cents, due_date, card_name, card_number, card_expiry,
        wsdl_pci, key):
    """Add/update account with Ezidebit and schedule credi card debit.

    Existing accounts and payment methods are updated. Existing scheduled
    payments are retained.

    """
    (month, year) = card_expiry.split('/')
    month = int(month)
    year = int('20' + year) # YYYY
    with EzidebitClient(wsdl_pci) as client:
        details = client.service.AddCardDebit(
            # All these fields required to avoid vaugue error message.
            DigitalKey=key,
            YourSystemReference=user.username,
            YourGeneralReference='',
            LastName=user.last_name,
            FirstName=user.first_name,
            EmailAddress=user.email,
            MobilePhoneNumber='',
            PaymentReference=payment_ref,
            NameOnCreditCard=card_name,
            CreditCardNumber=card_number,
            CreditCardExpiryYear=year,
            CreditCardExpiryMonth=month,
            PaymentAmountInCents=cents,
            DebitDate=due_date,
            SmsPaymentReminder='NO',
            SmsFailedNotification='NO',
            SmsExpiredCard='NO',
        )
    logger.debug(details)
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)


def add_payment(user, payment_ref, cents, due_date, wsdl_nonpci, key):
    """Add additional debit to existing account/payment method."""
    with EzidebitClient(wsdl_nonpci) as client:
        client = suds.client.Client(wsdl_nonpci)
        details = client.service.AddPayment(
            # All these fields required to avoid vaugue error message.
            DigitalKey=key,
            EziDebitCustomerID='',
            YourSystemReference=user.username,
            DebitDate=due_date,
            PaymentAmountInCents=cents,
            PaymentReference=payment_ref,
        )
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)


def clear_schedule(ezi_id, wsdl_nonpci, key):
    """Clear any existing payments."""
    with EzidebitClient(wsdl_nonpci) as client:
        client = suds.client.Client(wsdl_nonpci)
        details = client.service.ClearSchedule(
            DigitalKey=key,
            EziDebitCustomerID=ezi_id,
            YourSystemReference='',
            KeepManualPayments='NO',
        )
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)


def edit_customer_bank_account(
        user_id, acct_name, bsb, acct_number, wsdl_pci, key, update_by=''):
    """Update customer to pay by bank debit.

    Customers with an alternate payment method are switched. Inactive accounts
    are reactivated.

    """
    with EzidebitClient(wsdl_pci) as client:
        client = suds.client.Client(wsdl_pci)
        details = client.service.EditCustomerBankAccount(
            DigitalKey=key,
            EziDebitCustomerID='',
            BankAccountName=acct_name,
            BankAccountBSB=bsb,
            BankAccountNumber=acct_number,
            YourSystemReference=user_id,
            Reactivate='YES',
            Username=update_by,
        )
    logger.debug(details)
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)


def edit_customer_credit_card(
        user_id, card_name, card_number, card_expiry, wsdl_pci, key,
        update_by=''):
    """Update customer to pay by credit card.

    Customers with an alternate payment method are switched. Inactive accounts
    are reactivated.

    """
    (month, year) = card_expiry.split('/')
    month = int(month)
    year = int('20' + year) # YYYY
    with EzidebitClient(wsdl_pci) as client:
        client = suds.client.Client(wsdl_pci)
        details = client.service.EditCustomerCreditCard(
            DigitalKey=key,
            EziDebitCustomerID='',
            NameOnCreditCard=card_name,
            CreditCardNumber=card_number,
            CreditCardExpiryYear=year,
            CreditCardExpiryMonth=month,
            YourSystemReference=user_id,
            Reactivate='YES',
            Username=update_by,
        )
    logger.debug(details)
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)
