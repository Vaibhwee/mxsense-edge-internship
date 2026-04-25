#include <Arduino_H7_Video.h>
#include <lvgl.h>
#include <TJpg_Decoder.h>
#include "test_image.h"

/* ==== Display ==== */
Arduino_H7_Video Display(800, 480, GigaDisplayShield);

/* ==== Image Size ==== */
#define IMG_W 320
#define IMG_H 240

/* ==== Framebuffer ==== */
static uint16_t imgBuffer[IMG_W * IMG_H];

/* ==== LVGL Canvas ==== */
lv_obj_t *canvas;

/* ==== JPEG Callback ==== */
bool tft_output(int16_t x, int16_t y,
                uint16_t w, uint16_t h,
                uint16_t *bitmap)
{
  for (uint16_t row = 0; row < h; row++)
  {
    memcpy(&imgBuffer[(y + row) * IMG_W + x],
           &bitmap[row * w],
           w * 2);
  }
  return true;
}

void setup()
{
  Serial.begin(115200);

  Display.begin();

  /* Create canvas */
  canvas = lv_canvas_create(lv_scr_act());

  lv_canvas_set_buffer(canvas,
                       imgBuffer,
                       IMG_W,
                       IMG_H,
                       LV_COLOR_FORMAT_RGB565);

  lv_obj_center(canvas);

  /* Setup JPEG decoder */
  TJpgDec.setCallback(tft_output);
  TJpgDec.setJpgScale(1);

  Serial.println("Drawing JPG...");

  /* Clear buffer first */
  memset(imgBuffer, 0, sizeof(imgBuffer));

  /* Draw JPEG */
  TJpgDec.drawJpg(0, 0, test_jpg, test_jpg_len);

  /* Refresh canvas */
  lv_obj_invalidate(canvas);

  Serial.println("Done.");
}

void loop()
{
  lv_timer_handler();
}