import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


class SchwalbeAPIError(RuntimeError):
    pass


def _cache_timeout_seconds() -> int:
    return int(getattr(settings, "SCHWALBE_CACHE_SECONDS", 120))


def _request_json(path: str):
    base_url = getattr(settings, "SCHWALBE_API_BASE", "").rstrip("/")
    if not base_url:
        raise SchwalbeAPIError("SCHWALBE_API_BASE ist nicht gesetzt")

    request = Request(f"{base_url}/{path.lstrip('/')}")
    request.add_header("Accept", "application/json")

    try:
        with urlopen(request, timeout=getattr(settings, "SCHWALBE_TIMEOUT_SECONDS", 10)) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise SchwalbeAPIError(f"Fehler beim Laden von Schwalbe API ({path}): {exc}") from exc


def fetch_offices():
    cache_key = "schwalbe.offices"
    data = cache.get(cache_key)
    if data is None:
        data = _request_json("offices")
        cache.set(cache_key, data, _cache_timeout_seconds())
    return data


def fetch_commitments():
    cache_key = "schwalbe.commitments"
    data = cache.get(cache_key)
    if data is None:
        data = _request_json("commitments")
        cache.set(cache_key, data, _cache_timeout_seconds())
    return data


def _allowed_statuses():
    configured = getattr(settings, "SCHWALBE_COMMITMENT_STATUSES", ["pending"])
    return set(configured)


def _is_candidate(commitment: dict) -> bool:
    return (
        commitment.get("confirmed") is True
        and commitment.get("electionUuid") is not None
        and commitment.get("enterStatus") in _allowed_statuses()
    )


def _office_name_by_uuid() -> dict:
    return {office.get("uuid"): office.get("name") for office in fetch_offices() if office.get("uuid") and office.get("name")}


def get_unique_gremien():
    office_names = _office_name_by_uuid()
    gremien = {
        office_names.get(commitment.get("officeUuid"))
        for commitment in fetch_commitments()
        if _is_candidate(commitment)
    }
    return sorted(name for name in gremien if name)


def get_candidates_for_gremium(gremium_name: str):
    office_names = _office_name_by_uuid()
    kandidaten = []

    for commitment in fetch_commitments():
        if not _is_candidate(commitment):
            continue
        if office_names.get(commitment.get("officeUuid")) != gremium_name:
            continue

        person = commitment.get("person") or {}
        kandidaten.append(
            {
                "first_name": person.get("firstName", ""),
                "last_name": person.get("lastName", ""),
                "candidate_comment": "",
                "lesung": "Daten aus Schwalbe API",
            }
        )

    return kandidaten