# Time-Sheet Chatbot

## Idea

This bot is supposed to be bot that helps you to fill and manage your time sheet.

## Features

1. User Registration:

    a. Provide your Employee ID and Name, the bot keeps it in a cookie and will remember you the next time you visit.
    1. Send `register` or `add me` to start the registration
    2. Upon first visit the bot will ask you to register you can send your details there too

2. Responds to generic messages:

    a. Show date-time
    1. Send `time now` to see current time
    2. Send `date today` to see current date
    3. Send `time in {Hours}` to show custom time `Hours` can be negative
    4. Send `date in {days D/weeks W/months M/}` to show needed date `{days D/weeks W/months M}` can be negative or zero but order must be maintained. The identifers `D,W,M` are necessary too.

    b. Show the day and holidays [Needs admin to fill those up] {will not be implemented now}

3. Fill time-sheet:

    a. Send `Give attendance today {Hours}` and it will add add those to your time sheet for today

    b. Send `Give overtime today {Hours}` it will add overtime

    c. Send `Give OOD today {Reason}` it will apply for OOD

    d. Send `Give OOD for {Days} days because of {Reason}` it will ask for the reason in the next chat if not provided, upon getting it will apply for OOD for `{Days}`

    PS: OOD - On Official Duty or Work From Home

4. Apply for leave:

    a. Send `Apply leave today {Reason}` it will apply for leave on the given day.

    b. Send `Apply leave for {Days} days because of {Reason}` it will ask for the reason in the next chat if not provided, upon getting it will apply for leave for the next `{Days}`

5. Undo:

    Send `undo` or `cancel` or `stop` to revert the last command sent

6. Show Stats:

    Send `Show my attendance` or `Show my performance`. It will use the cookie to retrive the users time-sheet filling up progress and also the leaves.

7. Show user info:

    Send `Show user info` or `who am i` it will retieve the user info and show as a message.

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
- [ ] Make the bot await user data like if the user sends `Give attendance` but no `{Hours}` are mentioned send a response asking to send the hours.
- [ ] { "todo": ["Make for days too","Make the js to show the intents and classes", "Integrate the DB","Make inline message forms"] }
  
## Caution

The bot uses tensorflow and will not work on low end devices [As a host], it is accessibe by almost all modern devices.
