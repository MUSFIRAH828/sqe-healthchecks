Q1. Why does TIMEOUT\_CASES include 59, 60, 61 and 31535999, 31536000, 31536001?

Answer:



These values are used for Boundary Value Analysis (BVA). The test checks values below, at, and above the allowed minimum and maximum limits.

\- 59: Below minimum → Expected 400.

\- 60: At minimum → Expected 201.

\- 61: Above minimum → Expected 201.

\- 31,535,999: Below maximum → Expected 201.

\- 31,536,000: At maximum → Expected 201.

\- 31,536,001: Above maximum → Expected 400.

This verifies that the API accepts valid timeout values and rejects values outside the allowed range.

Q2. What does test\_repeated\_create\_with\_unique\_name\_makes\_no\_duplicate check?

Answer:



This test checks duplicate prevention when creating a check with the unique: \["name"] option.

\- First API request creates the check and returns status 201.

\- Second request with the same name returns status 200, meaning the existing check is returned.

\- Both responses contain the same UUID.

\- The total number of checks increases by only one.

This confirms that repeated requests do not create duplicate checks with the same unique name.

Q3. Why call list\_checks() or get\_check() after each test?

Answer:



These methods verify the actual stored database records after an API request.

\- list\_checks() checks whether the total number of records changed as expected.

\- get\_check() verifies the saved check's details, such as name, timeout, grace, and status.

\- After a rejected request, list\_checks() confirms that no unwanted record was stored.

This ensures that tests verify both the API response and the actual database state.

