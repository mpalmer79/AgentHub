from app.workers.backoff import compute_backoff_seconds

def test_backoff_attempts():
    assert compute_backoff_seconds(1) == 15
    assert compute_backoff_seconds(2) == 60
    assert compute_backoff_seconds(3) == 300
    assert compute_backoff_seconds(10) == 300
