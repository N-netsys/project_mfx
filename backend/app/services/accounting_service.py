"""
Service for handling all double-entry accounting logic.
"""
from sqlalchemy.orm import Session
from decimal import Decimal
import uuid
from .. import models

# Standard account codes. A real app would allow tenants to configure these.
CASH_ACCOUNT = "1010"
LOANS_RECEIVABLE_ACCOUNT = "1100"
INTEREST_REVENUE_ACCOUNT = "4010"

def get_account(db: Session, account_code: str, tenant_id: uuid.UUID) -> models.accounting.ChartOfAccount:
    """Fetches an account from the Chart of Accounts."""
    account = db.query(models.accounting.ChartOfAccount).filter(
        models.accounting.ChartOfAccount.account_code == account_code,
        models.accounting.ChartOfAccount.tenant_id == tenant_id
    ).first()
    if not account:
        raise Exception(f"Accounting misconfiguration: Account '{account_code}' not found for tenant.")
    return account

def post_transaction(
    db: Session, 
    tenant_id: uuid.UUID, 
    description: str,
    debit_account_code: str,
    credit_account_code: str,
    amount: Decimal
):
    """
    Posts a balanced, two-legged transaction to the General Ledger.
    This is the heart of the accounting system.
    """
    transaction_id = str(uuid.uuid4())
    debit_account = get_account(db, debit_account_code, tenant_id)
    credit_account = get_account(db, credit_account_code, tenant_id)

    # Create Debit Entry
    debit_entry = models.accounting.GeneralLedgerEntry(
        transaction_id=transaction_id,
        description=description,
        account_id=debit_account.id,
        debit=amount,
        credit=Decimal("0.00"),
        tenant_id=tenant_id
    )
    # Create Credit Entry
    credit_entry = models.accounting.GeneralLedgerEntry(
        transaction_id=transaction_id,
        description=description,
        account_id=credit_account.id,
        debit=Decimal("0.00"),
        credit=amount,
        tenant_id=tenant_id
    )

    db.add(debit_entry)
    db.add(credit_entry)
    # The commit will happen in the calling service function