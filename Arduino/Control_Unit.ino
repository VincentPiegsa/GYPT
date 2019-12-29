/*
Vincent Piegsa (2019)

This program controls a Mitsumi M35SP-7N stepper motor via a ULN2003. Also, the data from
a pair of GY906 infrared thermometers and a DHT11 temperature sensor are collected.
*/
#include <Arduino.h>
#include <Wire.h>
#include <DHT.h>
#include <GY906.h>

#define DHT_PIN 8
#define DHT_TYPE DHT11

const int total_revolutions = 1910;
String cmd;

void tca_select(uint8_t bus);
void forwards(uint8_t revolutions);
void backwards(uint8_t revolutions);
void stepper(uint8_t dir);
void terminate_transmission();
void task(uint8_t index);

DHT dht = DHT(8, DHT11);
GY906 irt1 = GY906();
GY906 irt2 = GY906();

void setup()
{
  Serial.begin(115200);
  dht.begin();
  
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);
}

void loop()
{
  if (Serial.available() > 0)
  {
    cmd = Serial.readString();

    if (cmd.equals("0x00"))
    {
      Serial.println("Stepper Control © Vincent Piegsa 2019");
      terminate_transmission();
    }
    else if (cmd.equals("0x01"))
    {
      stepper(1);
      terminate_transmission();
    }
    else if (cmd.equals("0x02"))
    {
      stepper(0);
      terminate_transmission();
    }
    else if (cmd.equals("0x03"))
    {
      stepper(1);
      stepper(0);
      terminate_transmission();
    }
  }
}

void tca_select(uint8_t bus)
{
  if (bus > 7)
  {
    return;
  }

  Wire.beginTransmission(0x70);
  Wire.write(1 << bus);
  Wire.endTransmission();
}

void forwards(uint8_t revolutions=total_revolutions)
{
  for (int i=0; i<revolutions; i++)
  {
    digitalWrite(9, HIGH);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    delay(5);
  
    digitalWrite(9, LOW);
    digitalWrite(10, HIGH);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    delay(5);
  
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, HIGH);
    digitalWrite(12, LOW);
    delay(5);
  
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, HIGH);
    delay(5);
  }
}

void backwards(uint8_t revolutions=total_revolutions)
{
  for (int i=0; i<revolutions; i++)
  {
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, HIGH);
    delay(5);
  
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, HIGH);
    digitalWrite(12, LOW);
    delay(5);
  
    digitalWrite(9, LOW);
    digitalWrite(10, HIGH);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    delay(5);
  
    digitalWrite(9, HIGH);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    delay(5);
  }
}

void stepper(uint8_t dir)
{
  int stepsize = 25;
  int iterations = total_revolutions / stepsize;

  if (dir == 1)
  {
    for (int i=0; i<iterations; i++)
    {
      forwards(stepsize);

      delay(250);
      task(i);
      delay(250);
    }
  }

  else if (dir == 0)
  {
    for (int i=0; i<iterations; i++)
    {
      backwards(stepsize);

      delay(250);
      task(i);
      delay(250);
    }
  }
}

void terminate_transmission()
{
  Serial.println("0xFF");
}

void task(uint8_t index)
{
  tca_select(0);
  irt1.begin();
  double t1 = irt1.readObjectTemperature();

  tca_select(1);
  irt2.begin();
  double t2 = irt2.readObjectTemperature();
  
  Serial.println((String)index + ";" + (String)dht.readTemperature() + ";" + (String)t1 + ";" + (String)t2);
}
