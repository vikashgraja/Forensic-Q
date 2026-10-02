"""
Q-Bank Presentation & View Controllers
Thin controllers routing requests, coordinating selectors & services, and rendering Cotton templates.
"""

import io
from decimal import Decimal
from pathlib import Path

import openpyxl
from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .backend.statement_parser import format_inr
from .selectors import (
    fuzzy_search_transactions,
    get_all_audited_persons,
    get_all_bank_accounts,
    get_audited_person_by_id,
    get_bank_account_by_id,
    get_bank_dashboard_metrics,
    get_cdm_transactions,
    get_frequent_counterparties,
    get_frequent_transactions_breakdown,
    get_hyundai_details,
    get_paginated_bank_transactions,
    get_yearwise_breakdown,
)
from .services import (
    create_audited_person,
    delete_audited_person,
    delete_bank_account,
    ingest_bank_statement_file,
)


@require_GET
def bank_dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Main Q-Bank Forensic Financial Dashboard.
    Presents the Audited Persons Directory as the primary operational entry point.
    """
    metrics = get_bank_dashboard_metrics()
    persons = get_all_audited_persons()
    accounts = get_all_bank_accounts()
    frequent_entities = get_frequent_counterparties(limit=10)

    context = {
        "metrics": metrics,
        "persons": persons,
        "accounts": accounts,
        "frequent_entities": frequent_entities,
    }
    return render(request, "q_bank/dashboard.html", context)


@require_GET
def person_detail_view(request: HttpRequest, person_id: str) -> HttpResponse:
    """
    Forensic Workspace for a specific Audited Person.
    Displays all linked bank accounts, statement files, combined/per-account metrics,
    the Data Overview grid, and the Streamlit st.tab forensic analysis engine.
    """
    person = get_audited_person_by_id(person_id)
    if not person:
        raise Http404("Audited Person profile not found.")

    accounts = list(person.bank_accounts.all().order_by("-created_at"))

    selected_account_id = request.GET.get("account_id", "").strip() or None
    selected_account = None
    if selected_account_id:
        selected_account = next((a for a in accounts if str(a.id) == selected_account_id), None)

    # Scoped calculations (either specific account or all statements of the person combined)
    query_account_id = selected_account.id if selected_account else None
    query_person_id = None if selected_account else person.id

    frequent_entities = get_frequent_counterparties(
        account_id=query_account_id, person_id=query_person_id, limit=50
    )
    frequent_breakdown = get_frequent_transactions_breakdown(
        account_id=query_account_id, person_id=query_person_id, min_transactions=2
    )
    yearwise = get_yearwise_breakdown(account_id=query_account_id, person_id=query_person_id)
    hyundai_details = get_hyundai_details(account_id=query_account_id, person_id=query_person_id)
    cdm_rows = get_cdm_transactions(account_id=query_account_id, person_id=query_person_id)

    # Calculate summary metrics for active view
    if selected_account:
        view_txns = selected_account.total_transactions
        view_debit = selected_account.total_debit
        view_credit = selected_account.total_credit
        view_cdm_count = selected_account.cash_deposit_count
        view_hyundai_count = selected_account.hyundai_count
        last_txn = selected_account.transactions.order_by("-txn_date", "-created_at").first()
        closing_balance = last_txn.closing_balance if last_txn else Decimal("0.00")
    else:
        view_txns = sum(a.total_transactions for a in accounts)
        view_debit = sum(a.total_debit for a in accounts)
        view_credit = sum(a.total_credit for a in accounts)
        view_cdm_count = sum(a.cash_deposit_count for a in accounts)
        view_hyundai_count = sum(a.hyundai_count for a in accounts)
        closing_balance = Decimal("0.00")
        for a in accounts:
            last_txn = a.transactions.order_by("-txn_date", "-created_at").first()
            if last_txn:
                closing_balance += last_txn.closing_balance

    context = {
        "person": person,
        "accounts": accounts,
        "selected_account": selected_account,
        "selected_account_id": str(selected_account.id) if selected_account else "",
        "view_metrics": {
            "total_transactions": view_txns,
            "total_debit": view_debit,
            "total_debit_formatted": format_inr(view_debit),
            "total_credit": view_credit,
            "total_credit_formatted": format_inr(view_credit),
            "cash_deposit_count": view_cdm_count,
            "hyundai_count": view_hyundai_count,
            "closing_balance": closing_balance,
            "closing_balance_formatted": format_inr(closing_balance),
        },
        "frequent_entities": frequent_entities,
        "frequent_breakdown": frequent_breakdown,
        "yearwise": yearwise,
        "hyundai": hyundai_details,
        "cdm_rows": cdm_rows,
    }
    return render(request, "q_bank/person_detail.html", context)


@require_GET
def account_detail_view(request: HttpRequest, account_id: str) -> HttpResponse:
    """
    Direct link to a specific bank account; ensures it is linked to an AuditedPerson
    and redirects directly to the Person Multi-Statement Forensic Workspace.
    """
    account = get_bank_account_by_id(account_id)
    if not account:
        raise Http404("Bank account audit record not found.")

    if not account.person_id:
        from .models import AuditedPerson

        person, _ = AuditedPerson.objects.get_or_create(
            full_name=account.account_holder or "Auditee Custodian",
            defaults={"department": "General Auditee"},
        )
        account.person = person
        account.save(update_fields=["person"])

    return redirect(f"/bank/person/{account.person_id}/?account_id={account.id}")


@require_POST
def create_person_view(request: HttpRequest) -> HttpResponse:
    """
    Creates a new Audited Person profile.
    """
    full_name = request.POST.get("full_name", "").strip()
    if not full_name:
        messages.error(request, "Person full name is required.")
        return redirect("q_bank:dashboard")

    person = create_audited_person(
        full_name=full_name,
        employee_id=request.POST.get("employee_id", "").strip(),
        department=request.POST.get("department", "").strip(),
        designation=request.POST.get("designation", "").strip(),
        pan_number=request.POST.get("pan_number", "").strip(),
        email=request.POST.get("email", "").strip(),
        phone=request.POST.get("phone", "").strip(),
        notes=request.POST.get("notes", "").strip(),
    )
    messages.success(request, f"Created audited profile for '{person.full_name}'.")
    return redirect("q_bank:person_detail", person_id=person.id)


@require_POST
def delete_person_view(request: HttpRequest, person_id: str) -> HttpResponse:
    """
    Deletes an audited person profile and all associated bank accounts.
    """
    success = delete_audited_person(person_id)
    if success:
        messages.success(request, "Audited person profile deleted successfully.")
    else:
        messages.error(request, "Target person profile could not be found.")
    return redirect("q_bank:dashboard")


@require_GET
def transactions_api_view(request: HttpRequest) -> JsonResponse:
    """
    High-performance server-side paginated JSON endpoint for Tabulator ledger grid.
    Supports scoping by account_id OR person_id.
    """
    try:
        page = int(request.GET.get("page", 1))
    except (ValueError, TypeError):
        page = 1

    try:
        page_size = int(request.GET.get("size", 25))
    except (ValueError, TypeError):
        page_size = 25

    account_id = request.GET.get("account_id", "").strip() or None
    person_id = request.GET.get("person_id", "").strip() or None
    search = request.GET.get("search") or request.GET.get("q") or ""
    filter_type = request.GET.get("filter_type", "all").strip()
    party_name = request.GET.get("party_name", "").strip()

    sort_field = (
        request.GET.get("sort[0][field]")
        or request.GET.get("sort_by")
        or request.GET.get("sort")
        or "txn_date"
    )
    sort_dir = request.GET.get("sort[0][dir]") or request.GET.get("dir") or "desc"

    result = get_paginated_bank_transactions(
        account_id=account_id,
        person_id=person_id,
        page=page,
        page_size=page_size,
        search=search,
        filter_type=filter_type,
        party_name=party_name,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )
    return JsonResponse(result)


@require_GET
def fuzzy_search_api_view(request: HttpRequest) -> JsonResponse:
    """
    Live fuzzy sequence search endpoint for rapid narration text matching.
    """
    account_id = request.GET.get("account_id", "").strip() or None
    person_id = request.GET.get("person_id", "").strip() or None
    keywords = request.GET.get("keywords", "trust, sarla").strip()
    try:
        threshold = int(request.GET.get("threshold", 80))
    except (ValueError, TypeError):
        threshold = 80

    matches = fuzzy_search_transactions(
        account_id=account_id,
        person_id=person_id,
        keywords_str=keywords,
        threshold=threshold,
    )
    return JsonResponse({"status": "ok", "total_matches": len(matches), "matches": matches})


@require_POST
def upload_statement_view(request: HttpRequest) -> HttpResponse:
    """
    Receives and processes uploaded bank statement files (Excel, CSV, Word, PDF).
    Associates the statement with a specific person.
    """
    if "statement_file" not in request.FILES:
        messages.error(request, "No bank statement file uploaded.")
        return redirect("q_bank:dashboard")

    uploaded_file = request.FILES["statement_file"]
    person_id = request.POST.get("person_id", "").strip() or None
    account_holder = request.POST.get("account_holder", "").strip() or Path(uploaded_file.name).stem
    bank_name = request.POST.get("bank_name", "").strip()
    statement_label = (
        request.POST.get("statement_label", "").strip() or "Bank Statement Investigation"
    )
    account_number = request.POST.get("account_number", "").strip()

    try:
        account = ingest_bank_statement_file(
            file_obj_or_path=uploaded_file,
            filename=uploaded_file.name,
            account_holder=account_holder,
            bank_name=bank_name,
            statement_label=statement_label,
            account_number=account_number,
            person_id=person_id,
        )
        messages.success(
            request,
            f"Successfully imported {account.total_transactions:,} transactions for '{account.account_holder}' ({account.bank_name}).",
        )
        if account.person_id:
            return redirect(f"/bank/person/{account.person_id}/?account_id={account.id}")
        return redirect("q_bank:account_detail", account_id=account.id)
    except Exception as e:
        messages.error(request, f"Failed to parse and import bank statement: {e}")
        return redirect("q_bank:dashboard")


@require_POST
def delete_account_view(request: HttpRequest, account_id: str) -> HttpResponse:
    """
    Deletes a single bank statement/account audit and its transactions.
    """
    account = get_bank_account_by_id(account_id)
    person_id = account.person_id if account else None

    success = delete_bank_account(account_id)
    if success:
        messages.success(request, "Bank statement audit deleted successfully.")
    else:
        messages.error(request, "Target bank account could not be found.")

    if person_id:
        return redirect("q_bank:person_detail", person_id=person_id)
    return redirect("q_bank:dashboard")


def export_ledger_excel_view(request: HttpRequest) -> HttpResponse:
    """
    Exports filtered bank transactions to a native Excel workbook stream.
    """
    account_id = request.GET.get("account_id", "").strip() or None
    person_id = request.GET.get("person_id", "").strip() or None
    filter_type = request.GET.get("filter_type", "all").strip()

    result = get_paginated_bank_transactions(
        account_id=account_id,
        person_id=person_id,
        page=1,
        page_size=50000,
        filter_type=filter_type,
    )
    rows = result.get("data", [])

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transaction Ledger"

    headers = [
        "Txn Date",
        "Account Holder",
        "Bank Name",
        "Counterparty Name",
        "Narration",
        "Direction",
        "Debit Amount (INR)",
        "Credit Amount (INR)",
        "Closing Balance (INR)",
        "Cash Deposit (CDM)",
        "Hyundai Match",
        "Risk Score",
        "Risk Level",
        "Txn Ref ID",
    ]
    ws.append(headers)

    for r in rows:
        ws.append(
            [
                r.get("txn_date", ""),
                r.get("account_holder", ""),
                r.get("bank_name", ""),
                r.get("party_name", ""),
                r.get("narration", ""),
                r.get("direction_label", ""),
                r.get("debit_amount", 0.0),
                r.get("credit_amount", 0.0),
                r.get("closing_balance", 0.0),
                "YES" if r.get("is_cash_deposit") else "NO",
                "YES" if r.get("is_hyundai_related") else "NO",
                r.get("risk_score", 0),
                r.get("risk_level", ""),
                r.get("txn_ref", ""),
            ]
        )

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="forensiq_bank_ledger.xlsx"'
    return response


def export_frequent_excel_view(request: HttpRequest) -> HttpResponse:
    """
    Exports frequent counterparties analysis to Excel.
    """
    account_id = request.GET.get("account_id", "").strip() or None
    person_id = request.GET.get("person_id", "").strip() or None
    frequent = get_frequent_counterparties(account_id=account_id, person_id=person_id, limit=500)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Frequent Counterparties"

    headers = ["Counterparty Name", "Total Interactions", "Total Debit (INR)", "Total Credit (INR)"]
    ws.append(headers)

    for f in frequent:
        ws.append([f["party_name"], f["total_interactions"], f["debit_total"], f["credit_total"]])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="forensiq_frequent_counterparties.xlsx"'
    return response
