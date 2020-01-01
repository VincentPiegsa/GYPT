#include <LiquidCrystal.h>
#include <GY906.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
GY906 irt = GY906();

void displayTemperature()
{
  lcd.setCursor(0, 0);
  lcd.print("Object Temp:");

  lcd.setCursor(0, 1):
  lcd.print((String)irt.readObjectTemperature());
}

void setup() 
{
  irt.begin();
  lcd.begin(16, 2);
}

void loop() 
{
  displayTemperature();
  delay(250);
}
