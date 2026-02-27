BOARD   ?= esp32:esp32:esp32
PORT    ?= /dev/ttyUSB0
SKETCH   = esp32/esp32.ino

.PHONY: all build upload clean

all: build

# Generate the embedded HTML header from the web app source.
# Rebuilt automatically whenever index.html or the embed script changes.
esp32/web_app.h: webapp/index.html scripts/embed_webapp.py
	python3 scripts/embed_webapp.py

# Compile the sketch (includes embedding the web app first).
build: esp32/web_app.h
	arduino-cli compile --fqbn $(BOARD) esp32/

# Compile and upload to the connected ESP32.
# Override PORT if your device is on a different serial port:
#   make upload PORT=/dev/tty.usbserial-0001
upload: build
	arduino-cli upload -p $(PORT) --fqbn $(BOARD) esp32/

# Remove all generated artifacts.
clean:
	rm -f esp32/web_app.h
	rm -rf esp32/build
