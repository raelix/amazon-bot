from tld import get_tld

DOMAINS={
    'de': 'https://www.amazon.de',
    'fr': 'https://www.amazon.fr',
    'es': 'https://www.amazon.es',
    'it': 'https://www.amazon.it'
}

def __get_portal(url):
    return DOMAINS[get_tld(url.strip())]

def get_unique_domains(URLs):
    full_domains = []
    for url in URLs:
        full_domains.append(__get_portal(url))
    return set(full_domains)