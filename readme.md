# Time-Sheet Chatbot

## Idea

This bot is supposed to be bot that helps you to fill and manage your time sheet.

## Features

1. User Registration:

    a. Provide your Employee ID and Name, the bot keeps it in a cookie and will remember you the next time you visit.

2. Responds to generic messages:

    a. Show time

    b. Show the day and holidays [Needs admin to fill those up]

3. Fill time-sheet:

    a. Send `Give_attendance {Hours}` and it will add add those to your time sheet for today

    b. Send `Give_overtime {Hours}` it will add overtime

    c. Send `Give_OOD {Reason}` it will apply for OOD

    d. Send `Give_OOD_next {Reason}` it will ask for the reason in the next chat and upon getting it will apply for OOD for `{Days}`

4. Apply for leave:

    a. Send `Apply_leave {Reason}` it will apply for leave on the given day.

    b. Send `Apply_leave_next {Days}` it will ask for the reason in the next chat and upon getting it will apply for leave for the next `{Days}`

5. Undo:

    Send `undo` to revert the last command sent

6. Show Stats:

    It will use the cookie to retrive the users time-sheet filling up progress and also the leaves.

## Libraries Used

 Not Finalized yet.

## TODO

- [X] Make the webpage
- [X] Start the bot
- [ ] Find all the user inputs and the responses that I will need to feed into the training
- [ ] Training and test the model
- [ ] Find out how to use tensor flow to call function
- [ ] Find out how to extract the paramerts form the message and then use them to fill the data like `{Hours},{Reason},{Days}`
- [ ] Make an error message response if the user didn't provide the correct type of data
- [ ] Make the bot await user data like if the user sends `Give_attendance` but no `{Hours}` are mentioned send a response asking to send the hours.

## Caution

The bot uses tensorflow and will not work on low end devices [As a host], it is accessibe by almost all modern devices.
