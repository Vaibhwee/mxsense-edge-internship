#include <Arduino_H7_Video.h>
#include <lvgl.h>

Arduino_H7_Video Display(800, 480, GigaDisplayShield);

void setup() {
  Display.begin();

  // Get active screen
  lv_obj_t * screen = lv_scr_act();

  // Set background color to RED
  lv_obj_set_style_bg_color(screen, lv_color_hex(0xFF0000), 0);
  lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, 0);
}

void loop() {
  lv_timer_handler();
  delay(5);
}
