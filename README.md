# D_RObot
Discord bot to help with homework tracking. 

Connects to a Google Sheet using the Google Sheets API to read and add due dates. 

To implement: rescheduling due dates, deleting due dates. 

## /ping
Returns your ping
## /link
Gives you the link to the Google Sheet with all the due dates
## /due_dates
Tells you all the due dates for a course
## /due_this_week
Tells you all the assignments for a course that are due this week
## /when_due
Tells you when an assignment is due (make sure to spell the assignment name right)
## /add
Lets you append a row to the spreadsheet. Make sure that date is in the format MM/DD/YYYY, and that you use military time. Example: /add CS145 | 9/15/2020 | 22:00 | A1
