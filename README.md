## Whats so different about my project???

1. The data format was unusual — The Excel sheets uses a calendar-style layout (days as columns, times as rows, spread across weekly blocks) rather than a standard table. Most tools expect clean long-form data. Getting a parser to reliably read that specific Stevens dining format took careful inspection of the actual file structure. Or i would change it to long form which took plenty of time and mental work honestly so this was great

2. The +1 weekday bug — every single venue had the Weekday column shifted one day ahead of the actual calendar date. That's the kind of subtle data quirk that's easy to miss and causes wrong labels silently without throwing any errors. We caught it by cross-checking against the source images every time.

3. Verification mattered a lot — I uploaded the source images and would checked every single daily total and hourly value against them. That's not just plotting, that's data validation. A tool that just plots without checking would have shown wrong numbers confidently.

4. Libraries like matplotlib/seaborn have a lot of edge cases (column ordering, pivot behavior, annotation formatting) and LLMs in general tend to hallucinate working code that breaks on the specific data. The advantage here was iterating directly on your actual files and verifying outputs rather than generating generic code.


<img width="1470" height="956" alt="Screenshot 2026-02-24 at 10 45 53 PM" src="https://github.com/user-attachments/assets/07b4e60e-d346-46fe-8a30-1225027dea53" />
<img width="1470" height="956" alt="Screenshot 2026-02-24 at 10 45 55 PM" src="https://github.com/user-attachments/assets/e8a88505-dede-4bbc-b036-9145c8b593ca" />
<img width="1470" height="956" alt="Screenshot 2026-02-24 at 10 45 59 PM" src="https://github.com/user-attachments/assets/68f225ac-57c4-4cf2-a89f-ad6ad296a84c" />
