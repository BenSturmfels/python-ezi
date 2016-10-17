import logging

import suds
import suds.client

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
        except OSError as err:
            logger.error(err)
            raise EzidebitError(CONNECTION_ERROR_MSG) from err
        return client

    def __exit__(self, type, value, traceback):
        """Handle any connection errors in context manager body."""
        if type and issubclass(type, OSError):
            logger.error(value)
            raise EzidebitError(CONNECTION_ERROR_MSG) from value
        elif type == suds.WebFault:
            logger.error(value)
            raise EzidebitError(CONNECTION_ERROR_MSG) from value


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
    if not getattr(details, 'Data', False):
        raise EzidebitError(details.ErrorMessage)
    return details.Data


def add_bank_debit(
        user_id, first_name, last_name, email, payment_ref, cents, due_date,
        acct_name, bsb, acct_number, wsdl_pci, key):
    """Add/update account with Ezidebit and schedule a bank debit.

    Existing accounts and payment methods are updated. Existing scheduled
    payments are retained.

    This API call will reactivate an account marked 'Hold' or 'Cancelled', but
    not 'Cancelled - Pick up Card'.

    """
    with EzidebitClient(wsdl_pci) as client:
        details = client.service.AddBankDebit(
            # All these fields required to avoid vaugue error message.
            DigitalKey=key,
            YourSystemReference=user_id,
            YourGeneralReference='',
            LastName=last_name,
            FirstName=first_name,
            EmailAddress=email,
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
    if not getattr(details, 'Data', False):
        raise EzidebitError(details.ErrorMessage)


def add_card_debit(
        user_id, first_name, last_name, email, payment_ref, cents, due_date,
        card_name, card_number, card_expiry, wsdl_pci, key):
    """Add/update account with Ezidebit and schedule credi card debit.

    Existing accounts and payment methods are updated. Existing scheduled
    payments are retained.

    This API call will reactivate an account marked 'Hold' or 'Cancelled', but
    not 'Cancelled - Pick up Card'.

    """
    # Strip non-digits from card_number.
    card_number = ''.join(i for i in card_number if i.isdigit())
    try:
        month, year = card_expiry.split('/')
        month = int(month)
        year = int('20' + year) # YYYY
    except ValueError:
        month, year = '', ''
    with EzidebitClient(wsdl_pci) as client:
        details = client.service.AddCardDebit(
            # All these fields required to avoid vaugue error message.
            DigitalKey=key,
            YourSystemReference=user_id,
            YourGeneralReference='',
            LastName=last_name,
            FirstName=first_name,
            EmailAddress=email,
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
    if not getattr(details, 'Data', False):
        raise EzidebitError(details.ErrorMessage)


def add_payment(user_id, payment_ref, cents, due_date, wsdl_nonpci, key):
    """Add additional debit to existing account/payment method."""
    with EzidebitClient(wsdl_nonpci) as client:
        client = suds.client.Client(wsdl_nonpci)
        details = client.service.AddPayment(
            # All these fields required to avoid vaugue error message.
            DigitalKey=key,
            EziDebitCustomerID='',
            YourSystemReference=user_id,
            DebitDate=due_date,
            PaymentAmountInCents=cents,
            PaymentReference=payment_ref,
        )
    if not getattr(details, 'Data', False):
        raise EzidebitError(details.ErrorMessage)


def clear_schedule(user_id, wsdl_nonpci, key):
    """Clear any existing payments."""
    with EzidebitClient(wsdl_nonpci) as client:
        client = suds.client.Client(wsdl_nonpci)
        details = client.service.ClearSchedule(
            DigitalKey=key,
            EziDebitCustomerID='',
            YourSystemReference=user_id,
            KeepManualPayments='NO',
        )
    if not getattr(details, 'Data', False):
        raise EzidebitError(details.ErrorMessage)


def edit_customer_bank_account(
        user_id, acct_name, bsb, acct_number, wsdl_pci, key, update_by=''):
    """Update customer to pay by bank debit.

    Customers with an alternate payment method are switched. Inactive accounts
    are reactivated, but only from 'Hold' statuses, not from 'Cancelled'
    variants.

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
    if not getattr(details, 'Data', False):
        raise EzidebitError(details.ErrorMessage)


def edit_customer_credit_card(
        user_id, card_name, card_number, card_expiry, wsdl_pci, key,
        update_by=''):
    """Update customer to pay by credit card.

    Customers with an alternate payment method are switched. Inactive accounts
    are reactivated, but only from 'Hold' statuses, not from 'Cancelled'
    variants.

    """
    # Strip non-digits from card_number.
    card_number = ''.join(i for i in card_number if i.isdigit())
    try:
        month, year = card_expiry.split('/')
        month = int(month)
        year = int('20' + year) # YYYY
    except ValueError:
        month, year = '', ''
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
    if not getattr(details, 'Data', False):
        raise EzidebitError(details.ErrorMessage)


def get_settled_payments(date_from, date_to, wsdl_nonpci, key):
    """Fetches settled payments, from 'date_from' and up to 'date_to'.

    This includes both successful and dishonoured payments.

    Args:
        date_from: string YYYY-MM-DD
        date_to: string YYYY-MM-DD
        wsdl_nonpci: as above
        key: as above

    Returns:
        A list of Suds Payment objects.
          eg. payments[0].PaymentAmount.

    """
    with EzidebitClient(wsdl_nonpci) as client:
        details = client.service.GetPayments(
            DigitalKey=key,
            PaymentType='ALL',
            PaymentMethod='ALL',
            PaymentSource='ALL',
            DateFrom=date_from,
            DateTo=date_to,
            DateField='SETTLEMENT',
        )
    logger.debug(details)
    if details.Error != 0:
        raise EzidebitError(details.ErrorMessage)
    if details.Data:
        return details.Data.Payment
    else:
        return []
