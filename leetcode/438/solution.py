# https://leetcode.com/problems/find-all-anagrams-in-a-string/description/

from typing import List, Counter as CounterType
from collections import Counter


class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        result: List[int] = []
        p_count: CounterType[str] = Counter(p)
        window_count: CounterType[str] = Counter()

        for i in range(len(s)):
            # add current char to the window
            window_count[s[i]] += 1

            # if window size > p, remove the leftmost character
            if i >= len(p):
                if window_count[s[i - len(p)]] == 1:
                    del window_count[s[i - len(p)]]
                else:
                    window_count[s[i - len(p)]] -= 1

            # check if current window is an anagram of p
            if window_count == p_count:
                result.append(i - len(p) + 1)

        return result
