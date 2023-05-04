<!-- @format -->

# SmartFridgeAddOn

My Computer Engineering undergraduate capstone project (spanning over two semesters) consisted of a full semester consisting of the research phase, as well as a full semester for the implementation phase. Our project was to design a system of components that could make a fridge smart through ingredient detection and recipe recommendation. In this README I've attempted to summarize our accomplishments over the 2 semesters, focusing primarily on the implementation phase.


_Credits to my capstone group members: @vargheserg, @Brian-kyoudong-lee, @ashwin2310_

Architecture of our device & system:<br/><br/>
<img src="https://user-images.githubusercontent.com/60635737/235825009-8d54c7c8-03c2-4646-8a81-04571b2ad245.png"  width="500" height="400"/>

Demo of our device in a cooler (for proof of concept):

<img src="/demo/SmartFridgeAddOn_demo_img.jpg"/>

Demo video of our device in a cooler (for proof of concept):

(note: still image detection can be seen in this video here by the LED flash as the door closes)

https://user-images.githubusercontent.com/60635737/236096722-07c71b13-e21a-4577-87eb-a6ea1e144cc6.mov

## TLDR/Features

- This project exhibits an add-on gadget that makes any ordinary smart
- **Software**
  - _Web Application_ -> a web application that allows the user to view & count detected ingredients, in addition to view recipe recommendations -- built through React + Firebase Auth + Firestore cloud firestore database ([Web application github](https://github.com/vargheserg/smart-fridge-ui))
  - _Flask server_ -> a flask server that lives on the device that is used to register and deregister fridges for users
    - Once registered, you can access your fridge from anywhere
  - _Still image capture script_ -> a script that captures a still image and feeds this information to Firebase
     - Smart image capture (when the fridge door closes) via still image object detection through Luxonis SDK
  - _Bash scripts_ -> scripts that allow the Flask server and the still image detecting process to commence on startup and graciously exit
- **Machine Learning** -> a custom-trained YOLOv7 model to detect and count ingredients
  - Custom & manually labelled datasets of 6 ingredients with 6000 images in total (over 19,000 labels) including Oranges, Apples, Tomatoes, Strawberries, Green Peppers, Red Peppers
  - Four ingredients (Oranges, Apples, Tomatoes, Strawberries) boast an average precision of 90% when trained on the state-of-the-art YOLOv7 model
  - On-device ML model deployment (able to deploy a 300MB YOLOv7 model on a Raspberry Pi 2 W)
- **Hardware** -> boasts a low-powered device that can run large Neural Networks on-device
  - Boasts a low-powered embedded system, featuring a Raspberry Pi Zero 2 W for minimal power consumption (5.4 Watts) & minimal RAM (512 MB)
  - An Oak-D-Lite camera for on-device Neural Network inferencing and custom-built pipelines
  - A light sensor and an LED for a "smart" image capture functionality
  - Cloud-centralized system, no bluetooth required
  - Initial registration done on LAN
- **Mechanical** -> 2 custom made mounts for the fridge door
- **Team Organization**
  - Team was generally organized through the following tools:
    - Gantt chart
    - Jira

## Overview
Technologies utilizing the Internet of Things (IoT) have been exponentially growing in the technological market over the past several years. Research has shown that businesses who use IoT technologies have starkly increased from 13 percent all the way back in 2014 to approximately 25 percent in 2017 [17]. The IoT market is anticipated to grow from approximately US$ 483.28 billion in 2022 to US$ 2.2 trillion by 2028 [19]. The rising prominence of both IoT and machine learning has enabled us to apply these technological advances to fridges, and our project proposes to make fridges “smart” through a portable device that can easily attach to the fridge with intelligent cloud processing.<br/><br/>
        	This Smart-Fridge Add-on proposes a system that involves a customer facing web application, allowing the user to track ingredients within their fridge, as well as a Raspberry Pi device connected to a camera that allows still image object detection. This device boasts a state-of-the-art object detection model—built on the YOLOv7 (Pytorch) model—and trained using custom built datasets, engineered in-house for optimal performance. The machine learning model is currently capable of detecting ten objects—Apples, Oranges, Tomatoes, Strawberries, Green Peppers, Red Peppers, Bread, Eggs, Lemons, Bananas. The ML model not only detects each image but is able to produce a count of each object, a supplementary feature that will greatly aid in constructing recipes and recipe suggestions.<br/><br/>
        	The Smart-Fridge Add-on also provides a seamless flow with the device being able to initially register itself through local Wi-fi with a specific user on the web application. Shortly after the registration, the device becomes equipped with the capability to perform object detection and dispatch these detected objects to the cloud-deployed database. The web application will then harmoniously update to reflect the database changes on the user-interface.<br/><br/>
        	This project also introduces a novel method to capture objects within the fridge. Instead of real-time object detection that occurs perpetually, creating an unnecessarily large chunk of useless data as well as consuming substantially more power, the Smart-Fridge Add-on will only capture still images and perform object detection on those still images, and only when the fridge’s door is closed. This was implemented using a light sensor and an LED placed near the device, as well as custom developed Python scripts detecting lighting conditions and performing still capture using that.<br/><br/>
            With this simple cloud-based contraption, the end user will be able to coherently turn a normal fridge into a fridge inventory tracker, a recipe constructor, a recipe recommender, a remote fridge monitor, and much more.<br/><br/>

## Technical Design

### Machine Learning

#### Tools utilized:
- Roboflow
- Google Colab
- Python
- Pytorch
- Yolov7
- FiftyOne

#### Machine Learning Model Choice

Although initially YOLOv5 was chosen to be the detection algorithm of choice, the decision was later modified to adopt YOLOv7 as the primary training algorithm due to the higher level of accuracy (higher AP values) and its increased speed (image processing at 155 frames per second as opposed to baseline YOLO’s 45 fps). This model also adopts similar characteristics from the previous generations of the YOLO family and the improvements are present in the backend, thereby making the transition from YOLOv5 to YOLOv7 a seamless process. In terms of testing, the process remains exactly the same, with just an improvement in precision and computation.<br/>
The key improvement for YOLOv7 comes from the use of a new loss function (focal loss). From previous iterations utilizing a standard cross-entropy loss function, this new loss function improves detection of small objects as well-classified examples are down-weighted and the harder examples are given a greater level of emphasis. The image processing is also done at a higher resolution (608 x 608 pixels) when compared to a previous iteration such as YOLOv3 (416 x 416 pixels). This increased resolution also drastically helps the newer model to detect smaller objects with higher accuracy [15]. The following two images below show the layer aggression scheme and the speed improvements for YOLOv7

#### Datasets

For this project, training the datasets in the YOLOv7 Pytorch format needed to first be backed by the creation of a manual dataset. Finding open source and available datasets turned out to be infeasible due to the presence of too many uncontrollable variables. Creation of a manual datasets allows for a much more streamlined training and inference process, allowing adjustments for a specific use case. Specific rules were created for collecting, compiling and verifying datasets, they are as follows:
Rules for dataset collection:
1. No groups - All individual ingredients (ie. an orange) must be labeled in each image
2. Sliced ingredients (ie. half an orange, peeled orange) do not count as an orange (so far)
3. Approximately 800-1500 images must be collected per ingredient
4. Approximately 0-10% of background images (with no ingredients) must be within each dataset

The method used to collect datasets was one that involved Roboflow utilizing Roboflow for the entire data collection and labelling process, as well as using it to export data to the relevant format (in our case PyTorch YOLOv7).

Roboflow was the main application of choice as once the dataset was categorized, the application is able to directly parse through a data.yaml file and assign them into a 70-20-10 train, test and validation percentage split (this split is also customizable via Roboflow). The images can also have augmentations applied and further manually annotated and finally generated into separate versions that could be tested on a YOLOv7 script by using a Roboflow API key. The figures shown below demonstrate how Roboflow displays datasets once finalized and how the user is able to download it.

**Here are the list of datasets that I compiled from other datasets and manually checked and labelled:**

[Apple dataset](https://universe.roboflow.com/deluxeviper/fridge-ingredients-apple)<br/>
[Orange dataset](https://universe.roboflow.com/deluxeviper/orange-fridge-ingredients), sample results for the Orange dataset: 1599 images, trained for 55 epochs using Yolov7, produced 98% mAP@0.5, 96% P, 97% R
<br/>
[Tomato dataset](https://universe.roboflow.com/deluxeviper/tomato-fridge-ingredients)<br/>
[Strawberry dataset](https://universe.roboflow.com/deluxeviper/strawberry-fridge-ingredients)<br/>
[Orange & Apple dataset](https://universe.roboflow.com/deluxeviper/orange-apple-fridge-ingredients)<br/>
[Orange & Apple & Tomato & Strawberry dataset](https://universe.roboflow.com/deluxeviper/orange-apple-tomato-strawberry-fridge-ingredients)<br/>
[Green & Red Peppers dataset](https://universe.roboflow.com/deluxeviper/peppers-makesense)

#### Model Results
The 4 ingredient (Orange, Apple, Tomato, Strawberry) ML Model results
Dataset statistics: 
- 3.8k training images (73%), 876 validation images (19%), 432 testing images (8%) - Trained for 55 epochs
- Results:
   - Precision: 90.5%
   - Recall: 89.7%
   - mAP@0.5: 94.5%
   - mAP@.5:.95: 72.6%

<img src="https://user-images.githubusercontent.com/60635737/236084388-248c0fb1-1a47-4c6c-ad74-3f11ec257e2f.png"  width="300" height="200">

<img src="https://user-images.githubusercontent.com/60635737/236084576-3aee0567-9e2c-4bdd-9317-73c9a7662c1b.png"  width="300" height="200">

<img src="https://user-images.githubusercontent.com/60635737/236084649-582bc15e-3c4f-4084-a2c3-0e959bdc3f2f.png"  width="300" height="200">

The Green + Red Pepper results
Dataset statistics: 
- 726 training images (80%), 132 validation images (15%), 45 testing images (5%)
- Trained for 55 epochs
- Results:
   - Precision: 87.3%
   - Recall: 84.7%
   - mAP@0.5: 90.5%
   - mAP@.5:.95: 68.4%


<img src="https://user-images.githubusercontent.com/60635737/236085144-9565f943-3ab7-496f-bd41-ebdb19f0b07c.png"  width="300" height="200">

<img src="https://user-images.githubusercontent.com/60635737/236085210-8f17c0d9-010f-443b-b5a1-9c3297f3804f.png"  width="300" height="200">

<img src="https://user-images.githubusercontent.com/60635737/236085265-7ec01d27-88bb-4e15-97d9-58a668239e09.png"  width="300" height="200">

Credits to myself for leading the Machine Learning effort.

### Software

#### Tools used:
- Figma
- React
- CSS
- Bootstrap
- Firebase Authentication
- Firebase Cloudstore database
- Python
- Flask
- Luxonis SDK
- Multithreading
- Bash scripts
- Raspbian (Debian Linux)
- Postman

The following block diagram displays the standalone design between a user interface and the smart fridge add-on, as well as the usage of an external API for extended functions.

![Screenshot 2023-05-03 at 7 45 34 PM](https://user-images.githubusercontent.com/60635737/236074587-4a341476-f3f3-459d-a494-4de02c748400.png)

As shown in the diagram, the smart fridge add-on consists of a Raspberry Pi Zero 2 W, connected to an Oak-D-Lite via USB. The Raspberry Pi has the responsibility of communicating with local devices to register the system, as well as transferring the data to an online database. The registration is accomplished using a Flask LAN server. This will allow the device to run a “handshake” protocol intended to link the device to the user’s account that is stored in Firebase by storing the database keys on the device itself. That way, when the device begins to upload data including the contents and ingredients detected, the user would be able to view this data on the web application dashboard page. <br/><br/>
A secondary script will run to listen for the light sensor's signal on the falling edge. This thread’s starting conditions depend on the user credentials that have been stored when the registration endpoint is activated. The script would also begin on startup if the device is restarted via a shell script. The falling edge indicates that the fridge door was previously opened, but then closed with the fridge lights being turned off, causing the environment to be darker than the threshold necessary to pass the signal. When this happens, the Raspberry Pi will listen to the data stream from the Oak-D-Lite to acquire a snapshot of the fridge contents. This snapshot contains both the image and the object detection results. This is sent to the Firebase server, where the data gets overwritten. Having the support to connect multiple devices to an account allows flexibility for further applications such as aggregating ingredients for use-cases such as checking for potential recipes.<br/><br/>
 This application software also interfaces with the USB port to retrieve the data stream from the Oak-D-Lite. The Oak-D-Lite handles both the camera input on its wide stereo perspective, and the object detection analysis. For the design, YOLOv7 was selected for its advantages of only using the image once, and its lightweight and fast processing time. Due to fast response times, we are able to improve the UX of our application by reducing the latency of the responses. Additionally, a lightweight design without image storage will remove the need for a secondary backend server hosted on the cloud. This will include the image, as well as the results of the object detection models. 

The following sequence diagram describes the communication between the actor and the systems in order to acquire the queried data, as well as the initialization process in order to synchronize a user's credentials with a data access token.<br/>
 ![Screenshot 2023-05-03 at 7 47 50 PM](https://user-images.githubusercontent.com/60635737/236074813-9d39bf80-76e7-4a79-9490-0e15451373bd.png)
 

#### Web Application

Login/Authentication page:
![Screenshot 2023-05-03 at 10 25 44 PM](https://user-images.githubusercontent.com/60635737/236097612-0a278383-a9a4-462e-b4c5-7997c71a0b24.png)

Registration page for Fridges:

![Screenshot 2023-05-03 at 9 31 17 PM](https://user-images.githubusercontent.com/60635737/236088958-e5f55a6d-f9f6-4f9d-8b92-c40b399a321c.png)

User Interface Dashboard View:

![Screenshot 2023-05-03 at 9 32 00 PM](https://user-images.githubusercontent.com/60635737/236089013-dab53100-52b8-4680-b115-d362d4adb6a8.png)

Recipe Recommender (proof of concept):
![Screenshot 2023-05-03 at 9 40 55 PM](https://user-images.githubusercontent.com/60635737/236090651-8d680476-07e4-495f-8163-9a32136b51d2.png)

#### Still image object detection 

I created a script using the Luxonis SDK to capture still images upon a certain condition being met, and this condition could have been something such as a keyboard press (in our case it was the light sensor not having detected any light). To create this script, as it had not been done before, I had to utilize a visual graph tool that displays the pipeline of the script (ODL still image yolo detection script linked in the github [2]).<br/>
The pipeline in figure B below depicts the final flow of the still image YOLO detection script. The “XLinkIn” node represents the capture command queue providing an input to the “inputControl” input of the ColorCamera node. The ColorCamera then outputs the still image to an image manipulation node that converts the image size to the correct size (we used 640x640). Then the output image (with a size that correctly corresponds to the detection network) sends the image to the YOLO detection network that then extracts detections from it and produces 2 outputs. The first output is the frame output – this could include bounding boxes for the image – however for our use case only the image was needed for the passthrough output, and the actual output produced detection values that then provided objects that were detected, the count, confidence values, and more.

Initially, a pipeline that looked like this below (figure A) was not working due to input tensor exceeding a certain data range that the detection network accepted.

![Figure A](https://user-images.githubusercontent.com/60635737/236088481-490724d4-0bda-4791-8288-7e353b67521b.png)
Figure A - Initial pipeline (not working)

After much deliberation, simply placing an Image manipulation node between the output of the still image channel and the detection network fixed this issue.

![Figure B](https://user-images.githubusercontent.com/60635737/236088884-9f664a32-903c-477a-a8c9-8c271e661613.png)
Figure B - Final ODL still image pipeline (working)


Credits to my capstone partner @vargheserg for collaborating on the ideation and implementation of the flask server, the firebase communication, as well as the web application. Credits to myself for implementing still image detection on the updater script and briefly assisting with web application + firebase on snapshot update listener.


### Hardware

#### Tools used
- Raspberry Pi Zero 2 W
- Oak-D-Lite
- RS-281x LED strip
- Light Sensor
- Jumper cables
- 3D printer
- Solder

For the hardware component selection, we decided that the main components will be the Oak-D-Lite and the Raspberry Pi Zero 2 W. Although this is a prototype, we thought the combination of components would be the best for commercialization in the future.<br/>
In our hardware selection, we had an emphasis for a compact size, low power usage, and ease of installation to provide our priority on portability. Meanwhile, we also looked for simplistic design, as well as a balance between price, performance, and power for a hypothetical scaling production.<br/>
Our main ML computing module is the Oak-D-Lite. We decided on going with the Oak-D-Lite because the majority of the Raspberry Pi models did not have the processing power for local ML processing. Although the Google Coral and the Nvidia Jetson Nano provide stronger compute options, the Oak-D-Lite can provide comparable processing while providing us with built in stereo cameras. This allows for us to do depth sensing. It’s additionally smaller in comparison to the provided alternatives. In terms of price, the Oak-D-Lite is the cheapest out of all of the competing ML computing devices. Although the power usage could have been an issue, the other alternatives share the same problem so this was not considered in our selection process. <br/>
We decided on using a simple Raspberry Pi Zero 2 W as our interfacing device for communicating the Oak-D-Lite, Firebase, and our UI in the registration process. Out of all the Raspberry Pi’s considered, the Raspberry Pi Zero was the most compact computer with all the features and ports we require for our use case.<br/>

#### Temperature Analysis of the Oak-D-Lite

Taken from the Oak D-Lite Website, “The operating temperature range of the Robotics Vision Core 2 (die temperature) is -40 °C to 105 °C”. The idle temperature is approximately 35 °C and the camera sensor has an operating temperature of -30 °C to 70 °C. The manufacturer's stress test shows that on maximum load the enclosure reaches 55.7°C and the Chip reaches 73.53°C. As we see in the thermal camera image we can see no active cooling being used and Oak-D-Lite doing an acceptable job with dissipating the heat on its own. W

![Screenshot 2023-05-03 at 10 38 22 PM](https://user-images.githubusercontent.com/60635737/236098840-bcd6c46f-db64-4813-83b7-61dd74b8e852.png)


Credit to my capstone partner Brian Lee for choosing the hardware components and to myself for implementing them.

#### Mount Designs
We decided on two different approaches for the mount design (displayed below). One in which there would be a hinge design to attach to the shelf on your fridge door and one where we could attach with double sided tape. Both were designed with the thought of ease of use and installation with functionality being kept in mind.

Initial design to attach to fridge with double sided tape.
![Screenshot 2023-05-03 at 7 49 53 PM](https://user-images.githubusercontent.com/60635737/236075034-72c3e451-ee9f-4434-bb12-754f7c303a3b.png)

Alternative design to hang off shelf of fridge door.
![Screenshot 2023-05-03 at 8 02 09 PM](https://user-images.githubusercontent.com/60635737/236076275-2ab76723-9022-40c9-a747-a7cf094470d3.png)

Credits to my capstone partner @Brian-kyoudong-lee for composing (via AutoCAD) and 3D printing these mount designs.

