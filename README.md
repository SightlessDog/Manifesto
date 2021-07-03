# Manifesto

This the core of the app, it's written with **Python** and **OpenCv**. What this script does is basically tracking persons moving in front of the camera and assigning them ids, then send those ids to the **Kafka** instance that will send them over to the server.
There is also the Prototxt file which define the model architecture (i.e., the layers themselves) and caffemodel file which contains the weights for the actual layers

# Installation

1. Start by installing the virstual environment by running this command
   for windows:

   - python -m venv .venv

   for macos:

   - pip install virtualenv
   - virtualenv .venv

2. Activate your environment
   - .venv/Scripts/activate for windows
   - .venv/bin/activate for mac
3. Install the required dependencies

   - pip install -r requirements.dev
   - pip install -r requirements.prod

4. To run application copy and paste this line:
   python src/people_counter.py --prototxt=mobilnet/mobilnetSSD_deploy.prototxt --model=mobilnet/MobileNetSSD_deploy.caffemodel

5. Close the running video with the q button
