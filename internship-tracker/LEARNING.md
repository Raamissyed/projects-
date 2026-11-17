# Learn by building: internship tracker

This project was scaffolded with AI assistance so I can practise by reading, running, testing, and modifying it. **Do not claim you wrote every line independently; be ready to explain what the code does and what you changed.**

## Understand these five concepts

1. **Database schema**: CREATE TABLE describes which fields each application stores. The id primary key identifies one record.
2. **SQL parameters**: the ? placeholders separate user-entered text from SQL commands. This reduces SQL injection risk.
3. **CRUD**: add_application does INSERT, get_applications does SELECT, and update_application does UPDATE.
4. **Command-line arguments**: argparse turns commands like --status applied into values passed to functions.
5. **Automated tests**: the tests use an in-memory database to check expected outcomes without touching real applications.

## Practice missions (do these yourself)

- [ ] Run all tests and explain what test_parameterized_sql_keeps_quotes_and_sql_text_safe checks.
- [ ] Add two fictional applications, update one, and export the results.
- [ ] Add a --company filter to list using a parameterized LIKE query. Add at least two tests.
- [ ] Add a delete command that asks for explicit confirmation before deleting. Test both confirmation and cancellation.
- [ ] Explain the difference between saved and applied and why the database might store a NULL date.
- [ ] Improve the status model to track stage history without losing previous interview progress.

## Interview practice

**Question:** Why did you choose SQLite?

**Answer to develop in your own words:** It stores structured records locally, supports SQL queries and joins, and doesn't require deploying a database server for a small CLI app.

**Question:** How do you handle malicious input?

**Answer to develop in your own words:** SQL placeholders treat user input as data. The CSV export also prefixes values that could become spreadsheet formulas. This is a small local prototype rather than a security-audited product.

**Question:** What would you improve if you had another week?

Pick one practice mission above, implement it yourself, and explain its tradeoffs in a pull request.
