import logging
import urllib

import suds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONNECTION_ERROR_MSG = 'Could not connect to Ezidebit payment service.'

class EzidebitError(RuntimeError):
    pass


def get_customer_details(user_id, wsdl_pci, key):
    """Show details for an existing Ezidebit account.

    user_id is our reference to the account.

    """
    try:
        client = suds.client.Client(wsdl_pci)
        details = client.service.GetCustomerDetails(
            # All these fields required to avoid vaugue error message.
            DigitalKey=key,
            EziDebitCustomerID='',
            YourSystemReference=user_id,
        )
    except urllib.error.URLError as err:
        logger.error(err)
        raise EzidebitError(CONNECTION_ERROR_MSG)
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
    try:
        client = suds.client.Client(wsdl_pci)
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
    except urllib.error.URLError as err:
        logger.error(err)
        raise EzidebitError(CONNECTION_ERROR_MSG)
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
    try:
        client = suds.client.Client(wsdl_pci)
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
    except urllib.error.URLError as err:
        logger.error(err)
        raise EzidebitError(CONNECTION_ERROR_MSG)
    logger.debug(details)
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)


def add_payment(user, payment_ref, cents, due_date, wsdl_nonpci, key):
    """Add additional debit to existing account/payment method."""
    try:
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
    except urllib.error.URLError as err:
        logger.error(err)
        raise EzidebitError(CONNECTION_ERROR_MSG)
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)


def clear_schedule(ezi_id, wsdl_nonpci, key):
    """Clear any existing payments."""
    try:
        client = suds.client.Client(wsdl_nonpci)
        details = client.service.ClearSchedule(
            DigitalKey=key,
            EziDebitCustomerID=ezi_id,
            YourSystemReference='',
            KeepManualPayments='NO'
        )
    except urllib.error.URLError as err:
        logger.error(err)
        raise (CONNECTION_ERROR_MSG)
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)
