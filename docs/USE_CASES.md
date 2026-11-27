\# Use Cases



\## UC1: Create a Check



\### Actor



Owner, Member, or Viewer.



According to the expected access-control rules, only the Owner and Member should be allowed to create a check. During testing, the Viewer was also able to create a check.



\### Preconditions



1\. The user is logged in.

2\. The user has access to a project.

3\. The project dashboard is open.

4\. The user can see the `Add Check` button.



\### Main Flow



1\. The user opens the project dashboard.

2\. The user clicks the `Add Check` button.

3\. The system displays the check creation form.

4\. The user enters a check name.

5\. The user enters a valid URL or endpoint.

6\. The user selects the required period and grace time.

7\. The user submits the form.

8\. The system creates the check.

9\. The new check appears on the project dashboard.



\### Postcondition



A new check is successfully created and displayed in the project check list.



\### Alternative Flows



1\. The user adds tags or labels to the check before submitting the form.

2\. The user changes the period or grace time before creating the check.



\### Exception Flows



1\. The user enters an invalid URL or invalid schedule value. The system should display a validation error and should not create the check.

2\. A Viewer attempts to create a check. The expected behavior is that the system denies the action. However, during testing, the Viewer was able to create a check, which indicates an access-control issue.



\### Test Evidence



\- Owner dashboard and check list: `Screenshot 2026-11-27 143801.png`

\- Member check creation: `Screenshot 2026-11-27 144255.png`

\- Viewer check creation: `Screenshot 2026-11-27 144424.png`

\- Viewer account confirmation: `Screenshot 2026-11-27 144504.png`



\---



\## UC2: Ping a Check and View Its Status



\### Actor



Owner, Member, or Viewer.



\### Preconditions



1\. The user is logged in.

2\. The user has access to the project.

3\. At least one check exists in the project.

4\. The check details page is open.



\### Main Flow



1\. The user opens the project dashboard.

2\. The user selects an existing check.

3\. The system displays the check details page.

4\. The user clicks the `Ping Now` button.

5\. The system sends a request to the check URL.

6\. The system records the ping result.

7\. The system updates the check status and last-ping information.

8\. The user views the updated status on the check details page or dashboard.



\### Postcondition



The check has been pinged, and its latest status and ping information are displayed to the user.



\### Alternative Flows



1\. The user changes the check schedule or grace time and then pings the check again.

2\. The user views the check history or event information after the ping is completed.



\### Exception Flows



1\. The check URL does not respond within the allowed time. The system records a timeout or failure status.

2\. The check URL returns an error or is unavailable. The system displays or records a failed check result.



\### Test Evidence



\- Check details page with `Ping Now` button and schedule information: `Screenshot 2026-11-27 144037.png`

\- Check list displaying status and last-ping information: `Screenshot 2026-11-27 144058.png`

