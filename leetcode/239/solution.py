# https://leetcode.com/problems/sliding-window-maximum/description/
from collections import deque
from typing import List, Deque


class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        result = []
        window: Deque[int] = deque()

        for i, num in enumerate(nums):
            # remove indices out of current window
            if window and window[0] <= i - k:
                window.popleft()

            # remove smaller elements from back of window
            while window and nums[window[-1]] < num:
                window.pop()

            window.append(i)

            # when window is full, add to result
            if i >= k - 1:
                result.append(nums[window[0]])

        return result
