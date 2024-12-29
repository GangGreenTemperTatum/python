# https://leetcode.com/problems/minimum-window-substring/description/

from collections import Counter


class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if not t or not s:
            return ""

        # dictionary to keep count of all unique chars
        dict_t = Counter(t)

        # number of unique chars in t
        required = len(dict_t)

        # left right pointers
        l, r = 0, 0

        # keep track of how many unique chars in t are in current window
        formed = 0

        # dictionary to keep a count of all unique chars in current window
        window_counts = {}

        # ans tuple of the form (window length, left, right)
        ans = float("inf"), None, None

        while r < len(s):
            # append a char from the right to the window
            character = s[r]
            window_counts[character] = window_counts.get(character, 0) + 1

            if character in dict_t and window_counts[character] == dict_t[character]:
                formed += 1

            # try to contract the window
            while l <= r and formed == required:
                character = s[l]

                # update the smallest window
                if r - l + 1 < ans[0]:
                    ans = (r - l + 1, l, r)

                # remove the leftmost character
                window_counts[character] -= 1
                if character in dict_t and window_counts[character] < dict_t[character]:
                    formed -= 1

                l += 1

            # move right pointer ahead for new window
            r += 1

        return "" if ans[0] == float("inf") else s[ans[1] : ans[2] + 1]
