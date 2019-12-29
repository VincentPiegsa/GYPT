#include <Arduino.h>
#include <Wire.h>

#define i2caddr 0x5A
#define T_AMB 0x06
#define T_OBJ1 0x07
#define T_OBJ2 0x08

class GY906
{
  public:
    GY906(uint8_t addr=i2caddr);
    boolean begin();
    double readAmbientTemperature(void);
    double readObjectTemperature(void);
    double readObjectTemperature2(void);
   private:
    double readTemp(uint8_t reg);
    uint16_t read16(uint8_t addr);
    uint8_t _addr;
};
