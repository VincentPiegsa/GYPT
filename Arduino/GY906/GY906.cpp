#include "Arduino.h"
#include "GY906.h"

GY906::GY906(uint8_t i2caddr)
{
  _addr = i2caddr;
}

boolean GY906::begin()
{
  Wire.begin();

  return true;
}

double GY906::readAmbientTemperature()
{
  return readTemp(T_AMB);
}

double GY906::readObjectTemperature()
{
  return readTemp(T_OBJ1);
}

double GY906::readObjectTemperature2()
{
  return readTemp(T_OBJ2);
}

double GY906::readTemp(uint8_t reg)
{
  float temp;

  temp = read16(reg);
  temp *= 0.02;
  temp -= 273.15;

  return temp;
}

uint16_t GY906::read16(uint8_t a)
{
  uint16_t ret;

  Wire.beginTransmission(_addr);
  Wire.write(a);
  Wire.endTransmission(false);

  Wire.requestFrom(_addr, (uint8_t)3);
  ret = Wire.read();
  ret |= Wire.read() << 8;

  uint8_t pec = Wire.read();

  return ret;
}
