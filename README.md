# Manifesto | Installation

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
