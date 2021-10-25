# Matrix Clock

The matrix clock is a set of two vertically stacked 64x32 matrices built using the rpi-rgb-led-matrix library and controlled through a telegram bot. The clock displays the current day, date, time, and the weather and contains a couple other exciting features to let you get the most out of your matrix.

### Features
- Telegram bot button interface for easy customization and control
- Clock automatically switches itself to night mode (red text for less eye strain) as it gets later, then goes back to normal colors during the day
- Write text onto the screen (full or half screen) to set reminders for yourself
    - Change the font size to make words bigger or fit more words on the screen
	- Change the font color for easy customization
- Send photos to the bot to display them on the matrix (automatically scales), and even overlay text to create quick images.

### Example Pictures
Matrix on day colors with weather displayed:


![Day colors](https://i.imgur.com/1ETmAOj.jpg "Day colors")

Matrix on night colors with weather displayed:


![Night colors](https://i.imgur.com/OOEOef5.jpg "Night colors")

Matrix with a reminder:


![Reminder](https://i.imgur.com/9ZzBVqw.jpg "Reminder")

Interface:


![Interface](https://i.imgur.com/oVwr6uQ.jpg "Interface")

### Commands
##### /help
Displays all the commands the bot can do with their usage

##### /buttons
Generates the control buttons for the bot

##### /ping
Pings the bot to ensure it is functioning

##### /ip
Displays the IP of the raspberry pi (for easy SSH reference)

##### /text [text]
Displays the text you input on the bottom half of the matrix
It will automatically split your words based on length into 3 lines (10 characters per line), use | (pipe) as a newline character to override this or use an empty line as an offset

##### /textf [text]
Works the same as text, but utilizes the full screen of the matrix

##### /textc [color] or /textc [r] [g] [b]
Set the color of the text on the matrix
Available colors: red, orange, yellow, green, blue, purple, pink, brown, gray, white, black
For a custom color use /textc [red] [green] [blue]

### How it Works
The bot runs in the python directory in the rpi-rgb-led-matrix library, and requires one to fill in their bot API key, weather API link, and username (for authentication purposes). Afterwards run the bot in a screen to ensure it is consistently on. Every second the bot polls the system for the time and weather, then displays what is necessary on the screen. If there is no text or image, it will display the full date and weather. For half text it will display the date, time, and text on the bottom half. Full text and images take up the full matrix display.

### Referenced Libraries
- [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix "rpi-rgb-led-matrix")
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot "python-telegram-bot")
