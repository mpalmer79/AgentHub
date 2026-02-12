from app.workers.failure import classify_failure

def test_classify_rate_limit():
    fi = classify_failure(RuntimeError("429 too many requests"))
    assert fi.code == "RATE_LIMITED"
    assert fi.retryable is True

def test_classify_auth():
    fi = classify_failure(RuntimeError("401 unauthorized"))
    assert fi.code == "AUTH_REQUIRED"
    assert fi.retryable is False

def test_classify_provider_error():
    fi = classify_failure(RuntimeError("503 service unavailable"))
    assert fi.code == "PROVIDER_ERROR"
    assert fi.retryable is True

def test_classify_unknown():
    fi = classify_failure(RuntimeError("something weird happened"))
    assert fi.code == "UNKNOWN"
    assert fi.retryable is False
