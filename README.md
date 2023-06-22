# WatchMyBack

> Update Jun 2023: Free (wannabe) alternative to [Tobii Aware](https://www.tobii.com/products/integration/pc-and-screen-based/tobii-aware) experience of new MSI laptops...

An easy-to-use defense tool against ["Shoulder Surfing"](https://en.wikipedia.org/wiki/Shoulder_surfing_(computer_security)) attacks, which allows you to immediately lock the screen of your computer if someone is behind you or if you move away from the computer without locking it.

It may be useful for students, workers, military personnel in situations where the computer is used in an insecure environment 
or when sensitive information are displayed on the screen and you want that nobody see them.

The program uses Google's [`mediapipe`](https://google.github.io/mediapipe) library for the [face detection](https://google.github.io/mediapipe/solutions/face_detection.html).  
My sincere kudos for the easy-to-use and powerful capabilities of the library 👏

These are functionalities of the program:
 - It detects the **user face** (_the first face detected or the nearest, thus the ones with the larger face detection box area_)
 - If two faces are detected: 
   - It shows an alert notification to the user,
   - Keeps track of the **user face** between the faces detected (_by the euclidean distance between new detections and previous **user face** detection_)
   - Then, if the **user face** moves the nose down (_the 'lock' signal_), the program locks the screen.
 - If no faces are detected, it shows a notification and start a countdown (_~5 seconds_) to automatically lock the screen.

## Demo
Two faces detected:
![Two faces detected](demo/TwoFacesDetected.gif)

No faces detected:  
![No faces detected](demo/NoFaceDetected.gif)
