import os
import re
import validators
import requests
import argparse

from datetime import datetime, date
from dotenv import load_dotenv
from hashlib import md5
from rdflib import Graph, URIRef, Literal, XSD, RDF, OWL, Namespace
from urllib.parse import urljoin


SCHEMA = Namespace("http://schema.org/")
NON_ROCRATE_PROFILES = [
    URIRef("https://codemeta.github.io/terms/"),
    URIRef("https://w3id.org/codemeta/3.0"),
    URIRef("http://www.w3.org/ns/json-ld#flattened"),
    URIRef("https://bioschemas.org/profiles/ComputationalWorkflow/1.0-RELEASE"),
    URIRef("https://bioschemas.org/profiles/FormalParameter/1.0-RELEASE")
]

def map_sameas_uri(uri):
        id = md5(uri.encode('utf-8')).hexdigest()
        new_uri = URIRef(f"https://profiles.ro-crate.org/data/profile/{id}")
        return new_uri

def main(dry_run):
    g = Graph()
    profile_class = URIRef("http://www.w3.org/ns/dx/prof/Profile")

    with open("profile_urls.txt", "r") as file:
        profile_urls = [line.strip() for line in file if line.strip()]

    for url in profile_urls:
        if not validators.url(url):
            raise ValueError(f"{url} is not an URL")

        headers = {
            "Accept": "application/ld+json, application/json"
        }

        try:
            response = requests.head(url, headers=headers, allow_redirects=True)
        except requests.RequestException as e:
            raise ValueError(f"Unable to reach {url} (Error: {e})")
        
        # Fallback
        if response.status_code >= 400:
            response = requests.get(url, headers=headers)

        content_type = response.headers.get("Content-Type", "").lower()
        if "json" not in content_type:
            raise ValueError(f"{url} does not return JSON-LD (Content type: {content_type})")

        temp_g = Graph()
        base_iri = urljoin(url, '.') if url.endswith("ro-crate-metadata.json") else f"{url.rstrip('/')}/"
        temp_g.parse(url, format="json-ld", publicID=base_iri)
        if any(temp_g.subjects(RDF.type, profile_class)):
            g += temp_g
        else:
            raise ValueError(f"No profile entity found in {url}")

    g.parse("gaps.ttl", format="turtle")

    datetime_pattern = re.compile(r"^-?\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$")
    date_pattern = re.compile(r"^-?\d{4}-\d{2}-\d{2}$")
    time_pattern = re.compile(r"^\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$")

    for s, p, o in g.triples((None, None, None)):
        typed_o = None

        if datetime_pattern.match(o):
            typed_o = Literal(o, datatype=XSD.dateTime)
        elif date_pattern.match(o):
            typed_o = Literal(o, datatype=XSD.date)
        elif time_pattern.match(o):
            typed_o = Literal(o, datatype=XSD.time)

        # Add type to datetime, date and time data
        if typed_o is not None:
            g.add((s, p, typed_o))
            g.remove((s, p, o))

        # Create profile URI for use in the profile portal
        if p == RDF.type and o == profile_class and s not in NON_ROCRATE_PROFILES:
            new_s = map_sameas_uri(s)
            g.add((new_s, RDF.type, o))
            g.add((new_s, OWL.sameAs, s))

        # Add triple <new profile URI> schema:datePublished "yyyy-mm-dd"^^xsd:date
        if (p == SCHEMA.datePublished and typed_o is not None
            and (s, RDF.type, profile_class) in g and s not in NON_ROCRATE_PROFILES):
            value = typed_o.toPython()
            if isinstance(value, datetime):
                new_s = map_sameas_uri(s)
                g.add((new_s, p, Literal(value.date(), datatype=XSD.date)))
            if isinstance(value, date):
                new_s = map_sameas_uri(s)
                g.add((new_s, p, Literal(value.isoformat(), datatype=XSD.date)))

    ttl_data = g.serialize(format="turtle")
    if not dry_run:
        FUSEKI_ENDPOINT = os.getenv('FUSEKI_UPLOAD_ENDPOINT')
        FUSEKI_PASSWORD = os.getenv('FUSEKI_PASSWORD')

        response = requests.post(FUSEKI_ENDPOINT, data=ttl_data, 
                                headers={"Content-Type": "text/turtle"}, 
                                auth=("admin", FUSEKI_PASSWORD))
        response.raise_for_status()

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Parse profile Ro Crate and upload graph to Jena Fuseki instance")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(args.dry_run)
