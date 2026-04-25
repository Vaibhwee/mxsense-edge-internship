#include <Arduino_H7_Video.h>
#include <Arduino_GigaDisplayTouch.h>
#include <lvgl.h>

Arduino_H7_Video Display(800, 480, GigaDisplayShield);
Arduino_GigaDisplayTouch Touch;

lv_obj_t * value_label;
int sensorValue = 0;

void setup() {
  Display.begin();
  Touch.begin();
  lv_init();

  lv_obj_t * screen = lv_scr_act();
  lv_obj_set_style_bg_color(screen, lv_color_hex(0xF0F0F0), 0);

  lv_obj_t * title = lv_label_create(screen);
  lv_label_set_text(title, "Sensor Dashboard");
  lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 20);

  value_label = lv_label_create(screen);
  lv_obj_set_style_text_font(value_label, &lv_font_montserrat_14, 0);
  lv_label_set_text(value_label, "0");
  lv_obj_align(value_label, LV_ALIGN_CENTER, 0, 0);
}

void loop() {
  lv_timer_handler();

  static unsigned long lastUpdate = 0;

  if (millis() - lastUpdate > 500) {
    lastUpdate = millis();

    sensorValue = random(0, 100);

    char buffer[10];
    sprintf(buffer, "%d", sensorValue);
    lv_label_set_text(value_label, buffer);
  }

  delay(5);
}