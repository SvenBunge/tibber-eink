
import logging
from waveshare_epd import epd7in5b_V2
from PIL import Image

logging.basicConfig(level=logging.DEBUG)

def schreibe_display():
    epd = None
    try:
        epd = epd7in5b_V2.EPD()
        
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        #logging.info("4.read bmp file on window")
        blk_img = Image.open("charts/chart_blk.png")
        red_img = Image.open("charts/chart_red.png")
        epd.display(epd.getbuffer(blk_img), epd.getbuffer(red_img))
        
    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
    finally:
        epd.sleep()
        epd7in5b_V2.epdconfig.module_exit()


schreibe_display()