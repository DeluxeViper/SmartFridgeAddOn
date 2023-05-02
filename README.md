# SmartFridgeAddOn
My Computer Engineering undergraduate capstone project - A device that can make a fridge smart through ingredient detection and recipe recommendation.

Credits to my capstone group members: @vargheserg (TODO: add other members)

## TLDR
- This project exhibits an add-on gadget that makes any ordinary smart
- **Web Application** -> allows you to register and monitor a fridge through the gadget
- **Software**
   - *Web Application* -> a web application that allows the user to view & count detected ingredients, in addition to view recipe recommendations -- built through React + Firebase Auth + Firestore cloud firestore database
   - *Flask server* -> a flask server that lives on the device that is used to register and deregister fridges for users
   - *Still image capture script* -> a script that captures a still image and feeds this information to Firebase 
   - *Bash scripts* -> scripts that allow the Flask server and the still image detecting process to commence on startup and graciously exit
- **Machine Learning** -> a custom-trained YOLOv7 model to detect and count ingredients
   - Manually labelled datasets of 6 ingredients with 6000 images in total (over 19,000 labels) including Oranges, Apples, Tomatoes, Strawberries, Green Peppers, Red Peppers
   - Four ingredients (Oranges, Apples, Tomatoes, Strawberries) boast an average precision of 90% when trained on the state-of-the-art YOLOv7 model
- **Hardware** -> boasts a low-powered device that can run large Neural Networks on-device
   - Uses a Raspberry Pi Zero 2 W for minimal power consumption (5.4 Watts)
   - An Oak-D-Lite camera for on-device Neural Network inferencing and custom-built pipelines
   - A light sensor and an LED for a "smart" image capture functionality
- **Mechanical** -> a custom made mount for the fridge door


