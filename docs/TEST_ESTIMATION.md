# Test Estimation — Healthchecks

**Course:** SE3002 Software Quality Engineering  
**Project:** Automated Testing of Healthchecks

## 1. Estimation method

Three-point estimation is used for planning. For each activity:

\[
E = \frac{O + 4M + P}{6}
\]

Where:

- **O** = Optimistic estimate (best reasonable case).
- **M** = Most likely estimate.
- **P** = Pessimistic estimate (reasonable case with delays or rework).
- **E** = Expected estimate.

All values must use the same unit, such as working days.

## 2. Estimation assumptions

- Estimates are planning estimates, not proof of work completed.
- The team has access to the repository and local development environment.
- Estimates include implementation and basic verification, but not unexpected major application defects.
- Activities may overlap when different team members work independently.
- The team should replace the example estimates below with estimates it has reviewed and agreed upon.

## 3. Three-point estimate table

The following values are **initial planning examples only**. Confirm or replace them with the team's agreed estimates before submission.

| Activity | O (days) | M (days) | P (days) | Expected E (days) |
|---|---:|---:|---:|---:|
| Test plan, estimation, traceability | 1 | 2 | 3 | 2.00 |
| Risk register and exit criteria | 0.5 | 1 | 2 | 1.08 |
| API and integration testing | 2 | 3 | 5 | 3.17 |
| Automated test-data generation | 1 | 2 | 4 | 2.17 |
| Use-case specification | 0.5 | 1 | 2 | 1.08 |
| Playwright use-case automation | 2 | 3 | 5 | 3.17 |
| Mutation testing and CI completion | 1 | 2 | 4 | 2.17 |
| Usability and accessibility | 1 | 2 | 3 | 2.00 |
| Defensive security testing | 1 | 2 | 4 | 2.17 |
| Performance and recovery testing | 1 | 2 | 4 | 2.17 |
| Defect management and RCA | 1 | 2 | 3 | 2.00 |
| Monitoring and completion report | 1 | 2 | 3 | 2.00 |
| **Total** | **13** | **22** | **42** | **23.18** |

## 4. Calculation example

For API and integration testing:

- O = 2 days
- M = 3 days
- P = 5 days

\[
E = \frac{2 + 4(3) + 5}{6}
= \frac{19}{6}
= 3.17 \text{ days}
\]

## 5. Estimation review

Before final submission, the team should:

1. Review each activity and its O, M, and P values.
2. Confirm the estimates are realistic for the remaining work.
3. Record the date on which the estimates were agreed.
4. Update estimates if the scope changes.
5. Compare planned estimates with actual effort in the completion report.

**Estimation review date:** To be filled by the team.  
**Approved by:** All three team members, after review.
