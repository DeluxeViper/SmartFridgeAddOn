
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time

from rpi_ws281x import Color, PixelStrip, ws

# LED strip configuration:

LED_COUNT = 8        # Number of LED pixels.
LED_PIN = 12          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0 
#LED_STRIP = ws.SK6812_STRIP_RGBW
#LED_STRIP = ws.SK6812W_STRIP
LED_STRIP = ws.WS2812_STRIP
def wheel(pos):
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -=85
        return Color(255-pos*3, 0, pos*3)
    else:
        pos -= 170
        return Color(0, pos*3, 255-pos*3)
def rainbow():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    strip.begin()
    for j in range(256*5):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j)&255))
        strip.show()
        time.sleep(50.0/1000.0)

# Define functions which animate LEDs in various ways.  
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def turnOnLight():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP) # Intialize the library (must be called once before other functions).
    strip.begin()
    #colorWipe(strip, Color(0, 0, 0, 0), 0)
    #time.sleep(2)
    colorWipe(strip, Color(255, 255, 200, 255))  # Composite White + White LED wipe
    #colorWipe(strip, Color(0, 0, 0, 0), 0)

def turnOffLight():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    #colorWipe(strip, Color(0, 0, 0, 0), 0)
    colorWipe(strip, Color(0, 0, 0, 0))  # Composite White + White LED wipe #time.sleep(2)
    #colorWipe(strip, Color(0, 0, 0, 0), 0)

def loadingUpdateProcessLights():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    strip.begin()
    for j in range(5):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, Color(127, 127, 127))
            strip.show()
            time.sleep(50.0 / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0) 

def theaterChaseRainbow():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    strip.begin()

    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i+j)%255))
            strip.show()
            time.sleep(50.0 / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

def unregistered_lights():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 10, LED_CHANNEL, LED_STRIP)   
    strip.begin()
    colorWipe(strip, Color(255, 0, 0), 150)
    time.sleep(500.0/1000.0)
    turnOffLight()

def loading_update_process_lights():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 10, LED_CHANNEL, LED_STRIP)   
    strip.begin() 
    colorWipe(strip, Color(255, 150, 0), 150)
    time.sleep(500.0/1000.0)
    turnOffLight()

def odl_ready_lights():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 10, LED_CHANNEL, LED_STRIP)   
    strip.begin()
    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, Color(0, 255, 0))
    strip.show()

def odl_error_lights():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 10, LED_CHANNEL, LED_STRIP)   
    strip.begin()
    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, Color(255, 0,0))
    strip.show()
    
    

# Main program logic follows:
if __name__ == '__main__': #    turnOnLight()
#    time.sleep(2)
#    turnOffLight()
#    loadingUpdateProcessLights()
#    theaterChaseRainbow()
#    rainbow()
#    colorWipe(strip, Color(255, 150,0), 150)
#    unregistered_lights()
#    loading_update_process_lights()
    odl_ready_lights()
    time.sleep(3)
#    unregistered_lights()
    #turnOffLight()
