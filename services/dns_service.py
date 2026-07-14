"""
CyberMind AI

DNS Service
"""

from __future__ import annotations

import dns.exception
import dns.resolver


class DNSService:

    def __init__(self):

        self.resolver = dns.resolver.Resolver()

        self.timeout = 5

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
        DNS analysis.
        """

        mx_res = self.mx(domain)
        txt_res = self.txt(domain)
        return {

            "domain": domain,

            "a": self.a(domain),

            "aaaa": self.aaaa(domain),

            "mx": mx_res,

            "mx_records": mx_res,

            "ns": self.ns(domain),

            "txt": txt_res,

            "txt_records": txt_res,

            "cname": self.cname(domain),

            "soa": self.soa(domain)

        }


dns_service = DNSService()