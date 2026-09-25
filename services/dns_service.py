"""
CyberMind AI

DNS Service
"""

from __future__ import annotations

import dns.exception
import dns.resolver


class DNSService:

    _cache: dict[str, tuple[float, dict]] = {}

    def __init__(self):

        self.resolver = dns.resolver.Resolver()

        self.timeout = 2.0

        self.resolver.timeout = self.timeout

        self.resolver.lifetime = self.timeout

    def lookup(
        self,
        domain: str,
        record_type: str
    ) -> list:
        """
        DNS lookup.
        """

        try:

            answers = self.resolver.resolve(
                domain,
                record_type
            )

            return [

                answer.to_text()

                for answer in answers

            ]

        except dns.exception.DNSException:

            return []

    def a(
        self,
        domain: str
    ) -> list:

        return self.lookup(
            domain,
            "A"
        )

    def aaaa(
        self,
        domain: str
    ) -> list:

        return self.lookup(
            domain,
            "AAAA"
        )

    def mx(
        self,
        domain: str
    ) -> list:

        return self.lookup(
            domain,
            "MX"
        )

    def ns(
        self,
        domain: str
    ) -> list:

        return self.lookup(
            domain,
            "NS"
        )

    def txt(
        self,
        domain: str
    ) -> list:

        return self.lookup(
            domain,
            "TXT"
        )

    def cname(
        self,
        domain: str
    ) -> list:

        return self.lookup(
            domain,
            "CNAME"
        )

    def soa(
        self,
        domain: str
    ) -> list:

        return self.lookup(
            domain,
            "SOA"
        )

    def ptr(
        self,
        domain: str
    ) -> list:

        return self.lookup(
            domain,
            "PTR"
        )

    def has_mx(
        self,
        domain: str
    ) -> bool:
        """
        Check MX record.
        """

        return len(

            self.mx(domain)

        ) > 0

    def analyze(
        self,
        domain: str
    ) -> dict:
        """
        DNS analysis with in-memory TTL caching and parallel record queries.
        """
        import time
        import copy
        import concurrent.futures

        domain_key = domain.strip().lower()
        now = time.time()
        if domain_key in self._cache:
            ts, cached_val = self._cache[domain_key]
            if now - ts < 600:
                return copy.deepcopy(cached_val)

        types_to_query = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        results: dict[str, list] = {}

        def _query_type(rtype: str):
            return rtype, self.lookup(domain_key, rtype)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(types_to_query)) as executor:
                futures = [executor.submit(_query_type, rt) for rt in types_to_query]
                for future in concurrent.futures.as_completed(futures, timeout=2.5):
                    try:
                        rtype, records = future.result()
                        results[rtype] = records
                    except Exception:
                        pass
        except Exception:
            pass

        a_res = results.get("A", [])
        aaaa_res = results.get("AAAA", [])
        mx_res = results.get("MX", [])
        ns_res = results.get("NS", [])
        txt_res = results.get("TXT", [])
        cname_res = results.get("CNAME", [])
        soa_res = results.get("SOA", [])

        dns_report = {
            "domain": domain,
            "a": a_res,
            "aaaa": aaaa_res,
            "mx": mx_res,
            "mx_records": mx_res,
            "ns": ns_res,
            "txt": txt_res,
            "txt_records": txt_res,
            "cname": cname_res,
            "soa": soa_res
        }
        self._cache[domain_key] = (now, dns_report)
        return copy.deepcopy(dns_report)


dns_service = DNSService()