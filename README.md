## Whats so different about my project???

1. The data format was unusual — The Excel sheets uses a calendar-style layout (days as columns, times as rows, spread across weekly blocks) rather than a standard table. Most tools expect clean long-form data. Getting a parser to reliably read that specific Stevens dining format took careful inspection of the actual file structure. Or i would change it to long form which took plenty of time and mental work honestly so this was great

2. The +1 weekday bug — every single venue had the Weekday column shifted one day ahead of the actual calendar date. That's the kind of subtle data quirk that's easy to miss and causes wrong labels silently without throwing any errors. We caught it by cross-checking against the source images every time.

3. Verification mattered a lot — I uploaded the source images and would checked every single daily total and hourly value against them. That's not just plotting, that's data validation. A tool that just plots without checking would have shown wrong numbers confidently.

4. Libraries like matplotlib/seaborn have a lot of edge cases (column ordering, pivot behavior, annotation formatting) and LLMs in general tend to hallucinate working code that breaks on the specific data. The advantage here was iterating directly on your actual files and verifying outputs rather than generating generic code.

 ##  Note: Below is just an example ofthe data without revealing any real data 


<img width="2533" height="1472" alt="image" src="https://github.com/user-attachments/assets/65c80106-2160-4620-8e23-04160d5dc9ce" />


<img width="2461" height="1474" alt="image" src="https://github.com/user-attachments/assets/3d4bb252-b972-4b3b-8ae0-2082cf05a52e" />


<img width="2469" height="1476" alt="image" src="https://github.com/user-attachments/assets/add78eb1-4ed5-4db1-a90d-1a208a67b86e" />

<img width="1470" height="956" alt="Screenshot 2026-02-24 at 11 00 33 PM" src="https://github.com/user-attachments/assets/f6099ce2-aac2-435a-ad9d-ee45fccfdb4a" />

