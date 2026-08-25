from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


class IosisError(Exception):
    def __init__(self, status, body):
        self.status = status
        self.code = body.get("error", "unknown")
        self.message = body.get("message", "")
        super().__init__(f"[{status}] {self.code}: {self.message}")


class IosisClient:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.environ.get("IOSIS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Pass api_key= or set IOSIS_API_KEY."
            )
        self.base_url = (
            base_url
            or os.environ.get("IOSIS_BASE_URL")
            or "https://tryiosis.vercel.app"
        ).rstrip("/")

    def _request(self, method, path, body=None, content_type=None, headers=None):
        url = f"{self.base_url}{path}"
        req_headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        if content_type:
            req_headers["Content-Type"] = content_type
        if headers:
            req_headers.update(headers)

        req = urllib.request.Request(
            url, data=body, headers=req_headers, method=method
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                ct = resp.headers.get("Content-Type", "")
                if "application/json" in ct or "text/json" in ct:
                    return json.loads(data)
                return data
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read())
            except Exception:
                err_body = {"error": "http_error", "message": str(e)}
            raise IosisError(e.code, err_body) from None

    def _yaml_body(self, yaml):
        p = str(yaml)
        if os.path.isfile(p):
            with open(p, "rb") as f:
                return f.read()
        return p.encode("utf-8")

    def submit_run(self, yaml, idempotency_key=None):
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        else:
            headers["Idempotency-Key"] = str(uuid.uuid4())

        return self._request(
            "POST",
            "/api/runs",
            body=self._yaml_body(yaml),
            content_type="application/yaml",
            headers=headers,
        )

    def get_run(self, run_id):
        return self._request("GET", f"/api/runs/{run_id}")

    def wait_for_run(self, run_id, max_wait=300, initial_delay=2, max_delay=30):
        delay = initial_delay
        elapsed = 0.0
        while elapsed < max_wait:
            run = self.get_run(run_id)
            status = run.get("run", {}).get("status")
            if status in ("succeeded", "failed"):
                return run
            time.sleep(delay)
            elapsed += delay
            delay = min(delay * 2, max_delay)
        raise TimeoutError(
            f"Run {run_id} did not complete within {max_wait}s"
        )

    def get_charts(self, run_id):
        return self._request("GET", f"/api/runs/{run_id}/charts")

    def list_datasets(self):
        return self._request("GET", "/api/datasets")

    def list_dataset_manifests(self):
        return self._request("GET", "/api/datasets/manifest")

    def lookup_dataset(self, name, version="latest"):
        name_enc = urllib.parse.quote(name, safe="")
        ver_enc = urllib.parse.quote(version, safe="")
        return self._request(
            "GET",
            f"/api/datasets/lookup?name={name_enc}&data_version={ver_enc}",
        )

    def list_tsfns(self):
        return self._request("GET", "/api/tsfns")

    def render_graph(self, yaml):
        raw = self._request(
            "POST",
            "/api/graphs/render",
            body=self._yaml_body(yaml),
            content_type="application/yaml",
        )
        return raw.decode("utf-8") if isinstance(raw, bytes) else raw
