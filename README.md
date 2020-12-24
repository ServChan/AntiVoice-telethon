# AntiVoice-telethon
Anti-voice script for telegram based on telethon

# Installation
1. Download script
2. Change the values in 
```
api_id = 000000
api_hash = ""

selfbot.start("PHONE NUMBER", 'CLOUD PASSWORD')
```
3. Run via console or any IDE

# Optional
1. You can change the length of deleted voice messages by changing the value in the line ```if (event.message.voice) and (event.message.voice.attributes[0].duration < 10):```. Value is 10 seconds by default.
2. You can add users whose messages will not be filtered by inserting their ID in 
```
whitelist = [
        0000000,
        1111111
    ]
```
