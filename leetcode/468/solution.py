# https://leetcode.com/problems/validate-ip-address/description/


class Solution:
    def validIPAddress(self, queryIP: str) -> str:
        if "." in queryIP:
            return self.validateIPv4(queryIP)
        elif ":" in queryIP:
            return self.validateIPv6(queryIP)
        else:
            return "Neither"

    def validateIPv4(self, queryIP: str) -> str:
        ip = queryIP.split(".")
        if len(ip) != 4:
            return "Neither"
        for i in ip:
            if not i.isdigit():
                return "Neither"
            if i[0] == "0" and len(i) > 1:
                return "Neither"
            if not 0 <= int(i) <= 255:
                return "Neither"
        return "IPv4"

    def validateIPv6(self, queryIP: str) -> str:
        ip = queryIP.split(":")
        if len(ip) != 8:
            return "Neither"
        for i in ip:
            if len(i) > 4 or len(i) == 0:
                return "Neither"
            for j in i:
                if j.lower() not in "0123456789abcdef":
                    return "Neither"
        return "IPv6"


# Test cases
test = Solution()
print(test.validIPAddress("172.16.254.1"))  # Output: "IPv4"
print(test.validIPAddress("2001:0db8:85a3:0:0:8A2E:0370:7334"))  # Output: "IPv6"
