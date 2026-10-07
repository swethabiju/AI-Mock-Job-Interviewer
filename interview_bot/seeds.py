"""Seed content for the interview bot. Everything the generator needs is here.
Marker convention: a marker ending in '*' is a prefix (stem) match, otherwise a whole-word/phrase match.
"""

ROLES = [
    {"role": "Backend Software Engineer", "skills": ["python", "sql", "rest apis", "git"]},
    {"role": "Data Analyst", "skills": ["sql", "python", "excel", "statistics"]},
    {"role": "Full Stack Developer", "skills": ["javascript", "react", "databases", "git"]},
    {"role": "Graduate Engineer Trainee", "skills": ["c programming", "data structures", "networks", "linux"]},
    {"role": "Java Developer", "skills": ["java", "oop", "sql", "spring"]},
    {"role": "QA Automation Engineer", "skills": ["python", "testing", "sql", "linux"]},
]

SKILL_TOPIC = {
    "python": "OOP", "java": "OOP", "oop": "OOP", "javascript": "OOP", "react": "OOP", "spring": "OOP",
    "testing": "OOP", "sql": "DBMS", "databases": "DBMS", "excel": "DBMS", "statistics": "DBMS",
    "c programming": "DSA", "data structures": "DSA", "rest apis": "Networks", "networks": "Networks",
    "linux": "OS", "git": "OS",
}

PROJECTS = [
    "a library management system in Java with MySQL", "a sales dashboard using Python and SQL",
    "a chat application using Node.js and sockets", "an attendance tracker with Flask and SQLite",
    "a weather app built with React and a public API", "an inventory system written in C with file handling",
    "a student marks portal using PHP and MySQL", "a to-do web app with Django",
]

ACKS = ["Thanks for sharing that.", "Got it.", "Okay, that helps.", "Understood.", "Thank you."]

GREETS = [
    "Hello, and welcome! This mock interview is for the {role} position, and the role focuses on {s1} and {s2}. {q}",
    "Welcome! Today's mock interview is for {role}, where {s1} and {s2} matter most. Let's begin. {q}",
]

# ---------------------------------------------------------------- HR (STAR)
STAR_ORDER = ["situation", "task", "action", "result"]
STAR_MARKERS = {
    "situation": ["situation", "at that time", "during our", "last semester", "when we were"],
    "task": ["my responsibility", "i was assigned", "my task", "i was responsible"],
    "action": ["so i", "to handle it", "then i", "i decided", "i started"],
    "result": ["as a result", "in the end", "finally", "the outcome", "it improved"],
}
STAR_TEMPLATES = {
    "situation": ["The situation was that {x}.", "At that time, {x}.", "During our project, {x}."],
    "task": ["My responsibility was to {x}.", "I was assigned to {x}.", "My task was to {x}."],
    "action": ["So I {x}.", "To handle it, I {x}.", "Then I {x}."],
    "result": ["As a result, {x}.", "In the end, {x}.", "Finally, {x}."],
}
HR_FILLER = ["I think I handled it quite well.", "Everyone was happy with how it went.",
             "It was a good learning experience for me.", "I try to stay calm and work hard."]
HR_PROBES = {
    "situation": ["Could you set the scene a bit more - what was the situation?",
                  "Can you give me more context about the situation?"],
    "task": ["What exactly was your responsibility in that situation?", "What was your specific task there?"],
    "action": ["What specific actions did you take yourself?", "Walk me through what you personally did."],
    "result": ["What was the result of your actions?", "How did it turn out in the end - what was the outcome?"],
}
HR_PROBE_KEYS = {
    "situation": ["situation", "context", "scene"], "task": ["responsib", "task"],
    "action": ["action", "did"], "result": ["result", "outcome", "turn out"],
}

HR_QS = [
    {"id": "h1", "q": "Tell me about a time you worked in a team and handled a disagreement.",
     "ctx": "two of us disagreed about how to design our final-year project module",
     "goal": "get the team to agree on one design",
     "acts": ["listened to both ideas and compared them on a small prototype",
              "set up a short meeting and wrote the pros and cons on a shared sheet"],
     "out": "we picked the simpler design and finished the module a week early"},
    {"id": "h2", "q": "Describe a situation where you had to meet a tight deadline.",
     "ctx": "our project demo was moved up by five days", "goal": "finish the reporting feature before the demo",
     "acts": ["broke the work into daily tasks and cut the optional features",
              "asked a teammate to review my code each evening so bugs were caught early"],
     "out": "we delivered a working demo on time"},
    {"id": "h3", "q": "Tell me about a mistake you made and what you learned from it.",
     "ctx": "I pushed a change without testing and it broke the login page",
     "goal": "fix the problem before others were affected",
     "acts": ["rolled back the change and wrote tests for the login flow",
              "told my team immediately and found the root cause"],
     "out": "the page was restored within an hour and we added a test step to our process"},
    {"id": "h4", "q": "Give an example of a time you took initiative.",
     "ctx": "our college club had no system to track event registrations",
     "goal": "build something simple to track registrations",
     "acts": ["built a small web form linked to a spreadsheet",
              "asked the members what fields they needed and built exactly that"],
     "out": "the club used it for every event after that"},
    {"id": "h5", "q": "Tell me about a time you had to learn something new quickly.",
     "ctx": "I had to use a framework I had never used for an internship task",
     "goal": "build a working feature within two weeks",
     "acts": ["followed the official tutorial and built a tiny practice app first",
              "asked a senior for a short code review of my first version"],
     "out": "I delivered the feature and my mentor used it in the release"},
    # held-out (test only)
    {"id": "h6", "q": "How do you respond to criticism? Share an example.", "test_only": True,
     "ctx": "my professor said my report was poorly structured", "goal": "improve the report before final submission",
     "acts": ["asked for specific examples and rewrote the report with a clear outline",
              "collected sample reports and compared their structure with mine"],
     "out": "my final report received a much better grade"},
    {"id": "h7", "q": "Describe a time you led a group.", "test_only": True,
     "ctx": "I was made the leader of a four-member hackathon team", "goal": "keep everyone aligned for a 24-hour build",
     "acts": ["split tasks by strengths and held a short check-in every four hours",
              "set up a shared board so everyone saw progress"],
     "out": "we finished the prototype and placed in the top five"},
]

# ---------------------------------------------------------------- TECH
TECH_FILLER = ["I have heard of this but I am not very sure how it works.",
               "I think it is something related to this topic but I do not remember the details."]


def kp(label, markers, sent):
    return {"label": label, "markers": markers, "sent": sent}


TECH_QS = [
    {"id": "o1", "topic": "OOP", "diff": 1, "q": "What is encapsulation in object-oriented programming?", "kps": [
        kp("data hiding", ["hid*", "private"], "It means hiding the internal data of an object and keeping it private."),
        kp("bundling", ["bundl*", "together", "wrap*"], "It bundles data and the methods that work on it together in one class."),
        kp("controlled access", ["getter*", "setter*", "public method*"], "Access to the data is controlled through public methods like getters and setters.")]},
    {"id": "o2", "topic": "OOP", "diff": 2, "q": "What is the difference between an abstract class and an interface?", "kps": [
        kp("partial implementation", ["partial*", "concrete method*"], "An abstract class can have some concrete methods, so it can provide partial implementation."),
        kp("multiple inheritance", ["multiple"], "A class can implement multiple interfaces but usually extend only one abstract class."),
        kp("contract", ["contract*", "signature*"], "An interface mainly declares a contract of method signatures without the implementation.")]},
    {"id": "o3", "topic": "OOP", "diff": 3, "test_only": True, "q": "Explain method overriding versus method overloading and when each is resolved.", "kps": [
        kp("overriding", ["subclass*", "child class*"], "Overriding is when a subclass provides its own version of a parent method."),
        kp("overloading", ["same name", "different parameter*"], "Overloading means methods with the same name but different parameters in one class."),
        kp("resolution time", ["runtime", "run time", "compile time"], "Overriding is resolved at runtime while overloading is resolved at compile time.")]},
    {"id": "d1", "topic": "DBMS", "diff": 1, "q": "What is a primary key?", "kps": [
        kp("uniqueness", ["unique*"], "A primary key uniquely identifies each row in a table."),
        kp("not null", ["null"], "It cannot contain null values."),
        kp("one per table", ["only one", "single", "one primary"], "A table can have only one primary key, though it may span several columns.")]},
    {"id": "d2", "topic": "DBMS", "diff": 2, "q": "What is normalization and why is it used?", "kps": [
        kp("redundancy", ["redundan*"], "Normalization reduces data redundancy by splitting data into related tables."),
        kp("anomalies", ["anomal*"], "It avoids insert, update and delete anomalies."),
        kp("normal forms", ["1nf", "normal form*"], "It is done in steps called normal forms such as 1NF, 2NF and 3NF.")]},
    {"id": "d3", "topic": "DBMS", "diff": 3, "q": "Explain database indexing and its trade-offs.", "kps": [
        kp("faster reads", ["faster", "speed*", "full table scan"], "An index speeds up searches by avoiding a full table scan."),
        kp("data structure", ["b-tree", "b tree", "hash"], "Indexes are usually stored as a B-tree or a hash structure."),
        kp("write cost", ["slower write*", "extra storage"], "The trade-off is extra storage and slower writes because the index must be updated.")]},
    {"id": "d4", "topic": "DBMS", "diff": 2, "test_only": True, "q": "What is the difference between INNER JOIN and LEFT JOIN?", "kps": [
        kp("inner join", ["only matching", "matching rows", "match in both"], "INNER JOIN returns only the rows that match in both tables."),
        kp("left join", ["left table"], "LEFT JOIN returns all rows from the left table even when there is no match."),
        kp("nulls", ["null"], "Unmatched columns from the right table are filled with NULL.")]},
    {"id": "s1", "topic": "OS", "diff": 1, "q": "What is a process and how is it different from a thread?", "kps": [
        kp("process", ["own memory", "address space", "separate memory"], "A process is a running program with its own memory space."),
        kp("threads share", ["share*"], "Threads inside a process share the same memory."),
        kp("lightweight", ["lightweight", "light weight", "cheaper"], "Threads are lightweight so creating and switching them is cheaper.")]},
    {"id": "s2", "topic": "OS", "diff": 3, "q": "What is a deadlock and what are the conditions for it?", "kps": [
        kp("circular wait", ["circular"], "A deadlock is when processes wait on each other in a circular wait and none can proceed."),
        kp("four conditions", ["mutual exclusion", "hold and wait", "no preemption"], "The four conditions are mutual exclusion, hold and wait, and no preemption, plus a closed chain of waiting processes."),
        kp("prevention", ["prevent*", "fixed order"], "It can be prevented by breaking one condition, for example by acquiring locks in a fixed order.")]},
    {"id": "n1", "topic": "Networks", "diff": 1, "q": "What is the difference between TCP and UDP?", "kps": [
        kp("reliable", ["reliab*"], "TCP is reliable and ordered, using acknowledgements and retransmission."),
        kp("connectionless", ["connectionless", "no connection"], "UDP is connectionless and does not guarantee delivery."),
        kp("use cases", ["streaming", "gaming", "dns"], "UDP suits streaming, gaming and DNS lookups where speed matters most.")]},
    {"id": "n2", "topic": "Networks", "diff": 2, "q": "What happens when you type a URL into a browser?", "kps": [
        kp("dns", ["dns"], "The browser first resolves the domain name to an IP address using DNS."),
        kp("connection", ["tcp", "handshake", "tls"], "It then opens a TCP connection and does a TLS handshake for HTTPS."),
        kp("request and response", ["http request", "response"], "It sends an HTTP request and the server returns a response that the browser renders.")]},
    {"id": "a1", "topic": "DSA", "diff": 1, "q": "What is the difference between an array and a linked list?", "kps": [
        kp("random access", ["random access", "by index", "o(1)"], "Arrays give fast random access by index in constant time."),
        kp("insertion", ["insert*", "delet*"], "Linked lists make insertion and deletion easier because no shifting is needed."),
        kp("memory", ["contiguous", "pointer*"], "Arrays use contiguous memory while linked lists need extra memory for pointers.")]},
    {"id": "a2", "topic": "DSA", "diff": 2, "q": "How does a hash table work and how are collisions handled?", "kps": [
        kp("hash function", ["hash function"], "A hash function maps a key to an index in an array of buckets."),
        kp("collisions", ["collision*"], "A collision happens when two keys map to the same index."),
        kp("resolution", ["chaining", "open addressing", "probing"], "Such clashes are handled with chaining or open addressing.")]},
    {"id": "a3", "topic": "DSA", "diff": 3, "test_only": True, "q": "Compare BFS and DFS and when you would use each.", "kps": [
        kp("data structures", ["queue*", "stack*"], "BFS uses a queue while DFS uses a stack or recursion."),
        kp("shortest path", ["shortest"], "BFS finds the shortest path in an unweighted graph."),
        kp("complexity", ["o(v + e)", "o(v+e)"], "Both run in O(V + E) time.")]},
]

# ---------------------------------------------------------------- CODE
# tests are (args_tuple, category); expected values are computed from the reference solution.
CODE_PROBLEMS = [
    {"id": "c1", "fn": "reverse_words", "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write reverse_words(s) that gives back the words of s in reverse order, separated by single spaces.",
     "hint2": "Think about what str.split() does when you call it with no arguments.",
     "hint3": "Outline: split the string into words, reverse the list of words, then join with single spaces.",
     "ref": "def reverse_words(s):\n    return ' '.join(s.split()[::-1])",
     "bugs": ["def reverse_words(s):\n    return ' '.join(s.split(' ')[::-1])", "def reverse_words(s):\n    return s[::-1]"],
     "tests": [(("hello world",), "basic"), (("one",), "single word"), (("",), "empty input"),
               (("  a   b ",), "extra spaces"), (("the quick brown fox",), "basic")]},
    {"id": "c2", "fn": "is_palindrome", "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write is_palindrome(s) that says whether s reads the same backwards, ignoring case and any non-alphanumeric characters.",
     "hint2": "Clean the string first: keep only letters and digits and ignore case.",
     "hint3": "Outline: build a cleaned lowercase list of alphanumeric characters, then compare it with its reverse.",
     "ref": "def is_palindrome(s):\n    t = [c.lower() for c in s if c.isalnum()]\n    return t == t[::-1]",
     "bugs": ["def is_palindrome(s):\n    t = [c for c in s if c.isalnum()]\n    return t == t[::-1]",
              "def is_palindrome(s):\n    t = s.lower()\n    return t == t[::-1]"],
     "tests": [(("racecar",), "basic"), (("A man, a plan, a canal: Panama",), "punctuation and case"),
               (("hello",), "not a palindrome"), (("",), "empty input"), (("Aa",), "mixed case")]},
    {"id": "c3", "fn": "two_sum", "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write two_sum(nums, target) that gives back the sorted list of two different indices whose values add up to target, or an empty list if none exist.",
     "hint2": "Remember each number you have seen so far so you can look up the missing partner quickly.",
     "hint3": "Outline: walk through the list keeping a dictionary of value to index; for each number check whether target minus the number is already stored.",
     "ref": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return sorted([seen[target - n], i])\n        seen[n] = i\n    return []",
     "bugs": ["def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []",
              "def two_sum(nums, target):\n    seen = set()\n    for n in nums:\n        if target - n in seen:\n            return sorted([target - n, n])\n        seen.add(n)\n    return []"],
     "tests": [(([2, 7, 11, 15], 9), "basic"), (([3, 2, 4], 6), "pair not at the start"), (([3, 3], 6), "duplicate values"),
               (([1, 2, 3], 7), "no solution")]},
    {"id": "c4", "fn": "count_vowels", "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write count_vowels(s) that gives back how many vowels (a, e, i, o, u, any case) appear in s.",
     "hint2": "Remember that vowels can be uppercase too, and every occurrence should be counted.",
     "hint3": "Outline: lowercase the string, loop over the characters, and count those found in 'aeiou'.",
     "ref": "def count_vowels(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')",
     "bugs": ["def count_vowels(s):\n    return sum(1 for c in s if c in 'aeiou')",
              "def count_vowels(s):\n    return len(set(c for c in s.lower() if c in 'aeiou'))"],
     "tests": [(("hello",), "basic"), (("",), "empty input"), (("AEIOU",), "uppercase letters"),
               (("rhythm",), "no vowels"), (("banana",), "repeated letters")]},
    {"id": "c5", "fn": "max_subarray", "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write max_subarray(nums) that gives back the largest sum of any contiguous, non-empty part of nums.",
     "hint2": "Think about the best sum of a subarray that ends at each position.",
     "hint3": "Outline: keep a running sum; at each element decide whether to extend the current subarray or start a new one; track the best sum seen.",
     "ref": "def max_subarray(nums):\n    best = cur = nums[0]\n    for n in nums[1:]:\n        cur = max(n, cur + n)\n        best = max(best, cur)\n    return best",
     "bugs": ["def max_subarray(nums):\n    best = cur = 0\n    for n in nums:\n        cur = max(0, cur + n)\n        best = max(best, cur)\n    return best",
              "def max_subarray(nums):\n    return max(nums)"],
     "tests": [(([1, 2, 3],), "all positive"), (([-2, 1, -3, 4, -1, 2, 1, -5, 4],), "mixed values"),
               (([-3, -1, -2],), "all negative"), (([5],), "single element")]},
    {"id": "c6", "fn": "fizzbuzz_list", "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write fizzbuzz_list(n) that gives back a list of strings for 1..n: 'Fizz' for multiples of 3, 'Buzz' for 5, 'FizzBuzz' for both, else the number as text.",
     "hint2": "Check the multiple-of-15 case before the multiple-of-3 and multiple-of-5 cases.",
     "hint3": "Outline: loop i from 1 to n inclusive; if divisible by 15 add FizzBuzz, else by 3 add Fizz, else by 5 add Buzz, else the number as text.",
     "ref": "def fizzbuzz_list(n):\n    out = []\n    for i in range(1, n + 1):\n        if i % 15 == 0:\n            out.append('FizzBuzz')\n        elif i % 3 == 0:\n            out.append('Fizz')\n        elif i % 5 == 0:\n            out.append('Buzz')\n        else:\n            out.append(str(i))\n    return out",
     "bugs": ["def fizzbuzz_list(n):\n    out = []\n    for i in range(1, n + 1):\n        if i % 3 == 0:\n            out.append('Fizz')\n        elif i % 5 == 0:\n            out.append('Buzz')\n        elif i % 15 == 0:\n            out.append('FizzBuzz')\n        else:\n            out.append(str(i))\n    return out",
              "def fizzbuzz_list(n):\n    out = []\n    for i in range(1, n):\n        if i % 15 == 0:\n            out.append('FizzBuzz')\n        elif i % 3 == 0:\n            out.append('Fizz')\n        elif i % 5 == 0:\n            out.append('Buzz')\n        else:\n            out.append(str(i))\n    return out"],
     "tests": [((5,), "small n"), ((15,), "multiple of 15"), ((1,), "n equals one"), ((0,), "n equals zero")]},
    {"id": "c7", "fn": "first_unique_char", "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write first_unique_char(s) that gives back the index of the first character that appears only once in s, or -1 if there is none.",
     "hint2": "Count how many times each character appears before deciding which one is unique.",
     "hint3": "Outline: build a frequency count, then scan the string left to right and give back the first index whose count is 1, else -1.",
     "ref": "def first_unique_char(s):\n    counts = {}\n    for c in s:\n        counts[c] = counts.get(c, 0) + 1\n    for i, c in enumerate(s):\n        if counts[c] == 1:\n            return i\n    return -1",
     "bugs": ["def first_unique_char(s):\n    counts = {}\n    for c in s:\n        counts[c] = counts.get(c, 0) + 1\n    for i, c in enumerate(s):\n        if counts[c] == 1:\n            return c\n    return -1",
              "def first_unique_char(s):\n    counts = {}\n    for c in s:\n        counts[c] = counts.get(c, 0) + 1\n    for i, c in enumerate(s):\n        if counts[c] == 1:\n            return i"],
     "tests": [(("leetcode",), "basic"), (("aabb",), "no unique character"), (("",), "empty input"),
               (("z",), "single character"), (("loveleetcode",), "unique appears later")]},
    {"id": "c8", "fn": "valid_parentheses", "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write valid_parentheses(s) that says whether the brackets ()[]{} in s are balanced and correctly nested.",
     "hint2": "The most recently opened bracket must be the first one closed - which data structure behaves like that?",
     "hint3": "Outline: push opening brackets on a stack; for a closing bracket check the top matches; at the end the stack must be empty.",
     "ref": "def valid_parentheses(s):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    stack = []\n    for c in s:\n        if c in '([{':\n            stack.append(c)\n        elif not stack or stack.pop() != pairs[c]:\n            return False\n    return not stack",
     "bugs": ["def valid_parentheses(s):\n    return s.count('(') == s.count(')') and s.count('[') == s.count(']') and s.count('{') == s.count('}')",
              "def valid_parentheses(s):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    stack = []\n    for c in s:\n        if c in '([{':\n            stack.append(c)\n        elif not stack or stack.pop() != pairs[c]:\n            return False\n    return True"],
     "tests": [(("()[]{}",), "basic"), (("(]",), "wrong bracket type"), ((")(",), "wrong order"), (("",), "empty input"),
               (("((",), "unclosed brackets"), (("{[]}",), "nested brackets")]},
    # held-out (test only)
    {"id": "c9", "fn": "merge_sorted", "test_only": True, "cx": ["o(n+m)", "o(m+n)", "linear"], "cx_text": "O(n + m)",
     "statement": "Write merge_sorted(a, b) that merges two sorted lists into one sorted list.",
     "hint2": "Use one pointer for each list and always take the smaller current element.",
     "hint3": "Outline: advance two pointers comparing the current elements, append the smaller one, then append whatever remains of either list.",
     "ref": "def merge_sorted(a, b):\n    i = j = 0\n    out = []\n    while i < len(a) and j < len(b):\n        if a[i] <= b[j]:\n            out.append(a[i])\n            i += 1\n        else:\n            out.append(b[j])\n            j += 1\n    return out + a[i:] + b[j:]",
     "bugs": ["def merge_sorted(a, b):\n    return a + b",
              "def merge_sorted(a, b):\n    i = j = 0\n    out = []\n    while i < len(a) and j < len(b):\n        if a[i] <= b[j]:\n            out.append(a[i])\n            i += 1\n        else:\n            out.append(b[j])\n            j += 1\n    return out"],
     "tests": [(([1, 3, 5], [2, 4, 6]), "interleaved"), (([], [1, 2]), "first list empty"), (([1, 2], []), "second list empty"),
               (([1, 2, 3], [7, 8]), "leftover items"), (([1, 1], [1]), "duplicates")]},
    {"id": "c10", "fn": "fibonacci", "test_only": True, "cx": ["o(n)", "linear"], "cx_text": "O(n)",
     "statement": "Write fibonacci(n) that gives back the n-th Fibonacci number, where fibonacci(0) is 0 and fibonacci(1) is 1.",
     "hint2": "Check which value your loop gives back and how the starting cases for 0 and 1 are defined.",
     "hint3": "Outline: keep two variables starting at 0 and 1; repeat n times updating both; finish with the first variable.",
     "ref": "def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
     "bugs": ["def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return b",
              "def fibonacci(n):\n    if n <= 2:\n        return 1\n    a, b = 1, 1\n    for _ in range(n - 2):\n        a, b = b, a + b\n    return b"],
     "tests": [((0,), "zero"), ((1,), "one"), ((10,), "basic"), ((32,), "large input")]},
]
