# WaterLevelMonitor
Raspberry Pi Python project to monitor water level and send email using AWS SES.

Added for my own backup need. Nothing in particular special about this, but is useable as is if added to a pi and connecting wires to the GPIOs used in the script.

Have to add new config for USERNAME_SMTP and PASSWORD_SMTP to send email using AWS SES, can easily replace with other email service and a lot simpler as well.

What did I make this for? Well.. I live in a place where you have your own sewage system and you have to monitor it every now and then to make sure things look OK (shit). You don't really want the water to rise too much, as it will flow over into chambers and ruin the natural separation that occurs in the system. So.. with this script + a pi (or with tweaks any other small, python capable device) and you can get email notifications if the water rises too much and an additional warning it level is critical. Includes time it took to reach levels and go down levels, which gives a guide on how optimal things are flowing. 

In my case the end step is a trap that after 1-3 years needs switching to maintain a proper water flow. This little project helps me knowing how close to replacement it is! Still have to take a visual peek every now and then...

Obviously you can just monitor nice clean water levels with this as well...
