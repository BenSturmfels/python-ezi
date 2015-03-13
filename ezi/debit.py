import logging

import suds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EzidebitError(RuntimeError):
    pass


def add_bank_debit(
        user, payment_ref, cents, due_date, acct_name, bsb, acct_number,
        wsdl_pci, key):
    """Add/update account with Ezidebit and schedule a bank debit.

    Existing accounts and payment methods are updated. Existing scheduled
    payments are retained.

    """
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
    client = suds.client.Client(wsdl_pci)
    (month, year) = card_expiry.split('/')
    month = int(month)
    year = int('20' + year) # YYYY
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
    client = suds.client.Client(wsdl_nonpci)
    details = client.service.ClearSchedule(
        DigitalKey=key,
        EziDebitCustomerID=ezi_id,
        YourSystemReference='',
        KeepManualPayments='NO'
    )
    if not details.Data:
        raise EzidebitError(details.ErrorMessage)
