import dns.resolver
import re

ADDRESS_REGEX = r'([a-z0-9.-]+)@(([a-z0-9.-]+)\.([a-z]+))'

def get_host(domain):
    try:
        cname = dns.resolver.resolve("mail."+domain, "CNAME")
        return cname[0].to_text()
    except:
        return None

def parse_mail(address):
    if address.count("@") > 1:
        raise SyntaxError("Too many at symbol")
    
    if len(address) > 255:
        raise ValueError("Address too long (> 255)")
    
    match = re.search(ADDRESS_REGEX, address)
    
    return match.group(1), match.group(2)

if __name__ == "__main__":
    user, domain = parse_mail("mathias@mathiasd.fr")
    print(user, domain)