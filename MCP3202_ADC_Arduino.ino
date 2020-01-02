/*
  MCP3202 Analog 2 Digital Converter communication
  @2019 Knowblesse
*/

#include <SPI.h>
int PIN_CS = 10; // this pin can be changed
void setup(){
  Serial.begin(9600);
  SPI.begin(); // mandatory
  //Initialize Chanel Select or Slave Select pin
  pinMode(PIN_CS, OUTPUT);
  digitalWrite(PIN_CS, HIGH);
  delay(100);
}

void loop(){
  // SPI Setting. depends on the device. read the arduino ref.
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
  // Start the communication
  digitalWrite(PIN_CS, LOW); // HIGH : disabled state
  delay(10); 
  // Sending 3 bytes (= 3 * 8 bits)
  byte SignalIn1 = SPI.transfer(0b00000001);
  byte SignalIn2 = SPI.transfer(0b10100000);
  byte SignalIn3 = SPI.transfer(0b00000000);
  // End the communication
  digitalWrite(PIN_CS, HIGH);

  Serial.print("Value : ");
  double temp = (double(SignalIn2 & 0b00001111) / pow(2,4) + double(SignalIn3) / pow(2,12))  * 5;
  Serial.println(temp,5);
}