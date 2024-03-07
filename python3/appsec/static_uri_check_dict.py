# // - Given a URI, find out If it's a valid uri by checking the pre-existing configuration
# Input Example:
# mail.com -> true
# google.com ->  true
# mail.xyz -> true

# live.com   ->  false

# "Domain"  "TLD"
# yahoo      net
# mail       com
# google     com
# mail       google
# news       google
# google     ca
# www        xyz
# mail       xyz
# www        mail
# ```

allowed_domains_dict = {
    'com': ['mail', 'google'],
    'xyz': ['mail']
}

def is_valid_uri(uri):
    domain, tld = uri.split(".")
    #print(domain)
    #print(tld)
    if domain in allowed_domains_dict[tld]:
        return True
    else:
        return False

print(is_valid_uri('mail.com'))  # true
print(is_valid_uri('google.com'))  # true
print(is_valid_uri('mail.xyz'))  # true
print(is_valid_uri('live.com'))  # false
