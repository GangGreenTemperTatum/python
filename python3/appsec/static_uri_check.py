# // - Given a URI, find out If it's a valid uri by checking the pre-existing configuration

# // ```​
# // Input Example:
# // mail.xyz -> true
# // google.com ->  true

# // live.com   ->  false
# // ​
# // "Domain"  "TLD"
# // mail       xyz
# // google     com
# // news       google
# // dev        io
# // apple      mail
# // ```

allowed_domains = [
    ("mail", "xyz"),
    ("google", "com"),
    ("news", "google"),
    ("dev", "io"),
    ("apple", "mail")
]

def is_valid_uri(uri):
    domain, tld = uri.split(".")

    if (domain, tld)in allowed_domains:
        return True
    else:
        return False
    

print(is_valid_uri('mail.xyz'))  # true
print(is_valid_uri('google.com'))  # true
print(is_valid_uri('live.com'))  # false
