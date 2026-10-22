def create_test_patient(client):
    response = client.post(
        "/patients/",
        json={
            "full_name": "Billing Test Patient",
            "date_of_birth": "1995-06-15",
            "gender": "Male",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_test_invoice(client, patient_id, invoice_number="INV-TEST-1001"):
    response = client.post(
        "/billing/invoices",
        json={
            "invoice_number": invoice_number,
            "patient_id": patient_id,
            "description": "Consultation and examination",
            "total_amount_paisa": 100000,
            "due_date": "2026-12-31",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_invoice(client):
    patient_id = create_test_patient(client)
    invoice = create_test_invoice(client, patient_id)

    assert invoice["invoice_number"] == "INV-TEST-1001"
    assert invoice["total_amount_paisa"] == 100000
    assert invoice["amount_paid_paisa"] == 0
    assert invoice["balance_due_paisa"] == 100000
    assert invoice["status"] == "Unpaid"


def test_list_invoices(client):
    patient_id = create_test_patient(client)
    create_test_invoice(client, patient_id)

    response = client.get("/billing/invoices")

    assert response.status_code == 200, response.text
    assert len(response.json()) >= 1


def test_get_invoice_details(client):
    patient_id = create_test_patient(client)
    invoice = create_test_invoice(client, patient_id)

    response = client.get(f"/billing/invoices/{invoice['id']}")

    assert response.status_code == 200, response.text
    assert response.json()["payments"] == []


def test_duplicate_invoice_number_rejected(client):
    patient_id = create_test_patient(client)
    create_test_invoice(client, patient_id)

    response = client.post(
        "/billing/invoices",
        json={
            "invoice_number": "INV-TEST-1001",
            "patient_id": patient_id,
            "description": "Another consultation",
            "total_amount_paisa": 50000,
            "due_date": "2026-12-31",
        },
    )

    assert response.status_code == 409


def test_invoice_for_missing_patient_rejected(client):
    response = client.post(
        "/billing/invoices",
        json={
            "invoice_number": "INV-MISSING-1001",
            "patient_id": 999999,
            "description": "Consultation",
            "total_amount_paisa": 50000,
            "due_date": "2026-12-31",
        },
    )

    assert response.status_code == 404


def test_record_full_payment_marks_invoice_paid(client):
    patient_id = create_test_patient(client)
    invoice = create_test_invoice(client, patient_id)

    response = client.post(
        f"/billing/invoices/{invoice['id']}/payments",
        json={
            "amount_paisa": 100000,
            "payment_method": "Cash",
            "reference": "RECEIPT-1001",
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["invoice_status"] == "Paid"
    assert response.json()["balance_due_paisa"] == 0


def test_partial_payment_updates_invoice_status(client):
    patient_id = create_test_patient(client)
    invoice = create_test_invoice(client, patient_id)

    response = client.post(
        f"/billing/invoices/{invoice['id']}/payments",
        json={
            "amount_paisa": 30000,
            "payment_method": "Card",
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["invoice_status"] == "Partially Paid"
    assert response.json()["amount_paid_paisa"] == 30000
    assert response.json()["balance_due_paisa"] == 70000


def test_overpayment_rejected(client):
    patient_id = create_test_patient(client)
    invoice = create_test_invoice(client, patient_id)

    response = client.post(
        f"/billing/invoices/{invoice['id']}/payments",
        json={
            "amount_paisa": 100001,
            "payment_method": "Cash",
        },
    )

    assert response.status_code == 400


def test_payment_for_missing_invoice_rejected(client):
    response = client.post(
        "/billing/invoices/999999/payments",
        json={
            "amount_paisa": 1000,
            "payment_method": "Cash",
        },
    )

    assert response.status_code == 404


def test_invoice_status_filter(client):
    patient_id = create_test_patient(client)
    invoice = create_test_invoice(client, patient_id)

    payment_response = client.post(
        f"/billing/invoices/{invoice['id']}/payments",
        json={
            "amount_paisa": 100000,
            "payment_method": "Cash",
        },
    )
    assert payment_response.status_code == 201

    response = client.get("/billing/invoices", params={"status": "Paid"})

    assert response.status_code == 200, response.text
    assert any(item["id"] == invoice["id"] for item in response.json())
