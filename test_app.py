from app import app, calculate_bmi, get_bmi_category
from unittest.mock import patch, MagicMock


def test_health():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"


def test_programs():
    client = app.test_client()
    resp = client.get("/programs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Fat Loss (FL)" in data


def test_create_client_no_json():
    client = app.test_client()
    response = client.post(
        "/clients",
        data="invalid",
        content_type="application/json"
    )
    assert response.status_code == 400


# BMI Calculation Tests
def test_calculate_bmi_normal():
    """Test BMI calculation for normal weight."""
    bmi = calculate_bmi(weight=70, height=1.80)
    assert bmi == 21.6


def test_calculate_bmi_overweight():
    """Test BMI calculation for overweight."""
    bmi = calculate_bmi(weight=85, height=1.75)
    assert bmi == 27.76


def test_calculate_bmi_underweight():
    """Test BMI calculation for underweight."""
    bmi = calculate_bmi(weight=50, height=1.70)
    assert bmi == 17.3


def test_calculate_bmi_obese():
    """Test BMI calculation for obese."""
    bmi = calculate_bmi(weight=100, height=1.70)
    assert bmi == 34.6


def test_calculate_bmi_invalid_height():
    """Test BMI calculation with zero height."""
    bmi = calculate_bmi(weight=70, height=0)
    assert bmi is None


def test_calculate_bmi_negative_height():
    """Test BMI calculation with negative height."""
    bmi = calculate_bmi(weight=70, height=-1.80)
    assert bmi is None


# BMI Category Tests
def test_bmi_category_underweight():
    """Test BMI category classification for underweight."""
    assert get_bmi_category(18.0) == "Underweight"


def test_bmi_category_normal():
    """Test BMI category classification for normal."""
    assert get_bmi_category(22.5) == "Normal"


def test_bmi_category_overweight():
    """Test BMI category classification for overweight."""
    assert get_bmi_category(27.5) == "Overweight"


def test_bmi_category_obese():
    """Test BMI category classification for obese."""
    assert get_bmi_category(32.0) == "Obese"


def test_bmi_category_boundary_underweight_normal():
    """Test BMI category at boundary between underweight and normal."""
    assert get_bmi_category(18.5) == "Normal"


def test_bmi_category_boundary_normal_overweight():
    """Test BMI category at boundary between normal and overweight."""
    assert get_bmi_category(25.0) == "Overweight"


def test_bmi_category_boundary_overweight_obese():
    """Test BMI category at boundary between overweight and obese."""
    assert get_bmi_category(30.0) == "Obese"


def test_bmi_category_none():
    """Test BMI category with None value."""
    assert get_bmi_category(None) == "Unknown"


# BMI Groups Endpoint Tests
@patch("app.get_supabase")
def test_bmi_groups_empty(mock_supabase):
    """Test BMI groups endpoint with no clients."""
    mock_response = MagicMock()
    mock_response.data = []
    mock_execute = mock_supabase.return_value.table.return_value
    mock_execute.select.return_value.execute.return_value = mock_response

    client = app.test_client()
    resp = client.get("/clients/bmi-groups")
    assert resp.status_code == 200
    data = resp.get_json()

    assert "Underweight" in data
    assert "Normal" in data
    assert "Overweight" in data
    assert "Obese" in data
    assert "Unknown" in data

    assert data["Underweight"] == []
    assert data["Normal"] == []


@patch("app.get_supabase")
def test_bmi_groups_with_clients(mock_supabase):
    """Test BMI groups endpoint with clients."""
    mock_response = MagicMock()
    mock_response.data = [
        {
            "id": 1,
            "name": "John",
            "age": 30,
            "weight": 70,
            "height": 1.80,
            "bmi": 21.6,
            "program": "Muscle Gain",
            "calories": 2450
        },
        {
            "id": 2,
            "name": "Jane",
            "age": 28,
            "weight": 85,
            "height": 1.65,
            "bmi": 31.2,
            "program": "Fat Loss",
            "calories": 1870
        },
        {
            "id": 3,
            "name": "Bob",
            "age": 35,
            "weight": 50,
            "height": 1.75,
            "bmi": 16.3,
            "program": "Beginner",
            "calories": 1300
        },
        {
            "id": 4,
            "name": "Alice",
            "age": 25,
            "weight": None,
            "height": None,
            "bmi": None,
            "program": "Fat Loss",
            "calories": 0
        }
    ]
    mock_execute = mock_supabase.return_value.table.return_value
    mock_execute.select.return_value.execute.return_value = mock_response

    client = app.test_client()
    resp = client.get("/clients/bmi-groups")
    assert resp.status_code == 200
    data = resp.get_json()

    # Check that Normal category has John
    assert len(data["Normal"]) == 1
    assert data["Normal"][0]["name"] == "John"
    assert data["Normal"][0]["bmi"] == 21.6

    # Check that Obese category has Jane
    assert len(data["Obese"]) == 1
    assert data["Obese"][0]["name"] == "Jane"

    # Check that Underweight category has Bob
    assert len(data["Underweight"]) == 1
    assert data["Underweight"][0]["name"] == "Bob"

    # Check that Unknown category has Alice
    assert len(data["Unknown"]) == 1
    assert data["Unknown"][0]["name"] == "Alice"


# Delete Client Tests
@patch("app.get_supabase")
def test_delete_client_success(mock_supabase):
    """Test successful deletion of a client."""
    mock_check_response = MagicMock()
    mock_check_response.data = [
        {
            "id": 1,
            "name": "John",
            "age": 30,
            "weight": 70,
            "height": 1.80,
            "bmi": 21.6,
            "program": "Muscle Gain",
            "calories": 2450
        }
    ]

    mock_delete_response = MagicMock()
    mock_delete_response.data = []

    mock_table = mock_supabase.return_value.table.return_value
    mock_table.select.return_value.eq.return_value.execute.return_value = (
        mock_check_response
    )
    mock_table.delete.return_value.eq.return_value.execute.return_value = (
        mock_delete_response
    )

    client = app.test_client()
    resp = client.delete("/clients/John")
    assert resp.status_code == 200
    data = resp.get_json()

    assert "message" in data
    assert "John" in data["message"]
    assert data["deleted_count"] == 1


@patch("app.get_supabase")
def test_delete_client_not_found(mock_supabase):
    """Test deletion of non-existent client."""
    mock_response = MagicMock()
    mock_response.data = []

    mock_table = mock_supabase.return_value.table.return_value
    mock_table.select.return_value.eq.return_value.execute.return_value = (
        mock_response
    )

    client = app.test_client()
    resp = client.delete("/clients/NonExistent")
    assert resp.status_code == 404
    data = resp.get_json()

    assert data["error"] == "client not found"


def test_delete_client_invalid_name():
    """Test deletion with invalid name parameter."""
    client = app.test_client()
    resp = client.delete("/clients/")
    # This will 404 because Flask won't match the route without a name
    assert resp.status_code == 404


def test_list_clients_custom_pagination(mock_supabase):
    """Test list clients with custom pagination."""
    mock_response = MagicMock()
    mock_response.data = [
        {"name": "John", "age": 30, "weight": 70}
    ]

    mock_table = mock_supabase.return_value.table.return_value
    mock_table.select.return_value.execute.return_value = mock_response
    mock_table.select.return_value.range = MagicMock(
        return_value=mock_table.select.return_value
    )

    client = app.test_client()
    resp = client.get("/clients?page=2&limit=5")
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["page"] == 2
    assert data["limit"] == 5


def test_list_clients_invalid_page():
    """Test list clients with invalid page parameter."""
    client = app.test_client()
    resp = client.get("/clients?page=0")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "page and limit must be >= 1" in data["error"]


def test_list_clients_invalid_limit():
    """Test list clients with invalid limit parameter."""
    client = app.test_client()
    resp = client.get("/clients?limit=101")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "limit cannot exceed 100" in data["error"]


@patch("app.get_supabase")
def test_list_clients_default_pagination(mock_supabase):
    """Test list clients with default pagination."""
    mock_response = MagicMock()
    mock_response.data = [
        {
            "name": "John",
            "age": 30,
            "weight": 70,
            "program": "Muscle Gain"
        },
        {
            "name": "Jane",
            "age": 28,
            "weight": 65,
            "program": "Fat Loss"
        }
    ]

    mock_table = mock_supabase.return_value.table.return_value
    mock_table.select.return_value.execute.return_value = mock_response
    mock_table.select.return_value.range = MagicMock(
        return_value=mock_table.select.return_value
    )

    client = app.test_client()
    resp = client.get("/clients")
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["page"] == 1
    assert data["limit"] == 10
    assert "total_count" in data
    assert "total_pages" in data
    assert "data" in data
