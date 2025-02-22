"""
A Python module to interact with the Federal Register API.

This module provides helper functions to query Federal Register documents of
different types (e.g., Executive Orders, Final Rules) with various filters.

The Federal Register API documentation is available at:
https://www.federalregister.gov/developers/api/v1

Example usage:
    # Pull all Executive Orders signed by Donald Trump on or after January 20, 2025
    # (hypothetically, for a second term).
    executive_orders = search_executive_orders(
        president='donald-trump',
        start_date='2025-01-20'
    )

    for eo in executive_orders['results']:
        print(eo['title'], eo['document_number'])

Note: The Federal Register does not require API keys; we just need HTTP requests.
However, the Federal Register may rate-limit if you send too many requests in a
short period. Always use responsibly.
"""

import requests
from typing import Optional, List, Dict

BASE_URL = "https://www.federalregister.gov/api/v1"

def search_documents(
    doc_type: Optional[str] = None,
    presidential_doc_type: Optional[str] = None,
    president: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search_term: Optional[str] = None,
    agencies: Optional[List[str]] = None,
    per_page: int = 20,
    page: int = 1,
) -> Dict:
    """
    Generic search against the Federal Register documents endpoint.

    :param doc_type: The Federal Register doc type:
                     - "RULE" for final rules
                     - "PRORULE" for proposed rules
                     - "NOTICE" for notices
                     - "PRESDOCU" for Presidential documents
    :param presidential_doc_type: If searching for Presidential Documents (PRESDOCU),
                                  specify the subtype here (e.g. "executive_order",
                                  "proclamation", "memorandum", etc.).
    :param president: The slug of the signing president (e.g. "donald-trump", "joe-biden").
    :param start_date: Start publication date in 'YYYY-MM-DD' format (inclusive).
    :param end_date: End publication date in 'YYYY-MM-DD' format (inclusive).
    :param search_term: Full text search term.
    :param agencies: A list of agency slugs, e.g. ["agriculture-department", ...].
    :param per_page: Number of results per page (max 1000). Defaults to 20.
    :param page: Which page of results to return. Defaults to 1.

    :return: A dictionary parsed from the JSON response of the Federal Register API.

    Usage example:
        # Search final rules from the EPA containing "air quality"
        results = search_documents(
            doc_type="RULE",
            search_term="air quality",
            agencies=["environmental-protection-agency"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            per_page=50
        )
    """
    endpoint = f"{BASE_URL}/documents.json"

    params = {
        "per_page": per_page,
        "page": page
    }

    # The Federal Register API uses a nested 'conditions' object in query params
    conditions = {}

    if doc_type:
        # Document type is an array, so we use conditions[type][]
        # e.g., conditions[type][]=PRESDOCU
        conditions["type[]"] = doc_type

    if presidential_doc_type:
        # conditions[presidential_document_type][]=executive_order
        conditions["presidential_document_type[]"] = presidential_doc_type

    if president:
        # conditions[president][]=donald-trump
        conditions["president[]"] = president

    if search_term:
        conditions["term"] = search_term

    if agencies:
        # agencies is an array of slugs
        # e.g. conditions[agencies][]=environmental-protection-agency
        conditions["agencies[]"] = agencies

    # Filter by publication date
    # e.g. conditions[publication_date][gte]=2025-01-20
    #      conditions[publication_date][lte]=2026-01-20
    date_conditions = {}
    if start_date:
        date_conditions["gte"] = start_date
    if end_date:
        date_conditions["lte"] = end_date
    if date_conditions:
        conditions["publication_date"] = date_conditions

    # Incorporate 'conditions' into query params
    # The Federal Register expects e.g. conditions[term], conditions[agencies][],
    # so we must flatten accordingly:
    for key, value in conditions.items():
        if isinstance(value, dict):
            # e.g. conditions['publication_date'] = {"gte":"2025-01-20","lte":"2026-01-20"}
            for subkey, subval in value.items():
                # becomes conditions[publication_date][gte] = ...
                params[f"conditions[{key}][{subkey}]"] = subval
        elif isinstance(value, list):
            # e.g. conditions[agencies[]] = [ 'environmental-protection-agency', ... ]
            # We'll assume all are just "conditions[agencies][]=..."
            # or "conditions[type][]=..."
            # or "conditions[president][]=..."
            # or "conditions[presidential_document_type][]=..."
            # We do multiple entries in the query string
            for val in value:
                params.setdefault(f"conditions[{key}]", [])
                params[f"conditions[{key}]"].append(val)
        else:
            # e.g. conditions['term'] = "climate change"
            # becomes conditions[term] = ...
            if key.endswith("[]"):
                # If the key ends with [] then it's an array
                # e.g. doc_type or president. We'll just store as a single-element list
                params[f"conditions[{key}]"] = [value]
            else:
                params[f"conditions[{key}]"] = value

    # Perform the request
    resp = requests.get(endpoint, params=params)
    resp.raise_for_status()
    return resp.json()


def search_executive_orders(
    president: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search_term: Optional[str] = None,
    agencies: Optional[List[str]] = None,
    per_page: int = 20,
    page: int = 1,
) -> Dict:
    """
    Search for Presidential Executive Orders in the Federal Register.

    :param president: The slug of the signing president (e.g. "donald-trump", "joe-biden").
    :param start_date: Start publication date in 'YYYY-MM-DD' format (inclusive).
    :param end_date: End publication date in 'YYYY-MM-DD' format (inclusive).
    :param search_term: Full text search term.
    :param agencies: A list of agency slugs, e.g. ["commerce-department"].
    :param per_page: Number of results per page (max 1000). Defaults to 20.
    :param page: Which page of results to return. Defaults to 1.

    :return: A dictionary representing the JSON response from the Federal Register API.

    Example usage:
        # Pull all Executive Orders signed by Donald Trump on or after January 20, 2025
        # (hypothetically for a second term).
        eos = search_executive_orders(
            president='donald-trump',
            start_date='2025-01-20'
        )
    """
    return search_documents(
        doc_type="PRESDOCU",
        presidential_doc_type="executive_order",
        president=president,
        start_date=start_date,
        end_date=end_date,
        search_term=search_term,
        agencies=agencies,
        per_page=per_page,
        page=page,
    )


def search_final_rules(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search_term: Optional[str] = None,
    agencies: Optional[List[str]] = None,
    per_page: int = 20,
    page: int = 1,
) -> Dict:
    """
    Search for Final Rules (RULE) in the Federal Register.

    :param start_date: Start publication date in 'YYYY-MM-DD' format (inclusive).
    :param end_date: End publication date in 'YYYY-MM-DD' format (inclusive).
    :param search_term: Full text search term.
    :param agencies: A list of agency slugs, e.g. ["labor-department"].
    :param per_page: Number of results per page (max 1000). Defaults to 20.
    :param page: Which page of results to return. Defaults to 1.

    :return: A dictionary representing the JSON response from the Federal Register API.

    Example usage:
        # Search final rules from the Environmental Protection Agency (EPA) about "air quality"
        rules = search_final_rules(
            agencies=['environmental-protection-agency'],
            search_term='air quality',
            start_date='2025-01-01'
        )
    """
    return search_documents(
        doc_type="RULE",
        start_date=start_date,
        end_date=end_date,
        search_term=search_term,
        agencies=agencies,
        per_page=per_page,
        page=page,
    )


def main():
    """
    Demonstration of using the above functions.
    This is just a sample usage and is not necessarily
    intended for direct execution in a production environment.
    """

    # Example: Retrieve final rules from Jan 1, 2024 to Dec 31, 2024,
    # searching for "clean water" from the EPA:
    final_rules = search_final_rules(
        start_date="2024-01-01",
        end_date="2024-12-31",
        search_term="clean water",
        agencies=["environmental-protection-agency"],
        per_page=5
    )
    print("Final Rules from EPA about 'clean water' in 2024:")
    for rule in final_rules.get("results", []):
        print(f"Title: {rule.get('title')}")
        print(f"Document Number: {rule.get('document_number')}")
        print(f"Publication Date: {rule.get('publication_date')}")
        print("---")

    # Example: Retrieve executive orders from Donald Trump, starting 2025-01-20
    # (hypothetically if he had a second term):
    executive_orders = search_executive_orders(
        president='donald-trump',
        start_date='2025-01-20',
        per_page=3
    )
    print("Executive Orders from Donald Trump on or after 2025-01-20:")
    for eo in executive_orders.get("results", []):
        print(f"Title: {eo.get('title')}")
        print(f"Document Number: {eo.get('document_number')}")
        print(f"Publication Date: {eo.get('publication_date')}")
        print("---")


if __name__ == "__main__":
    main()