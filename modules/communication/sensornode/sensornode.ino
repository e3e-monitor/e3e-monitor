#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>
#include <Wire.h>

/* Assign a unique ID to this sensor at the same time */
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345);
char magnetometerString[50];
char GPSTimeString[20];
char GPSLongitudeString[25];
char GPSLatitudeString[25];
char temperatureString[20];
String eventData = String("");
String eventFinalData = String("");
String data = String("");
float temperature = 0.0;
float lambda = 0.01;
int counter = 0;
int watchDog = 0;

boolean newEvent = false;
boolean debug = true;

//   Connect the GPS TX (transmit) pin to Arduino RX1
//   Connect the GPS RX (receive) pin to matching TX1
Adafruit_GPS GPS(&Serial1);

// this keeps track of whether we're using the interrupt
// off by default!
boolean usingInterrupt = false;
void useInterrupt(boolean); // Func prototype keeps Arduino 0023 happy

//Temp sensor Data
int tempSensorPin     = A0;
float tempSensorValue = 0;

HardwareSerial &debugPort       = Serial2;
HardwareSerial &raspberryPiPort = Serial;
HardwareSerial &XBeePort        = Serial3;

void setup()  
{      
  debugPort.begin(9600);

  // Initialise the magnetometer sensor
  if(!mag.begin())
  {
    debugPort.println("Magnetometer not detected !");
  }
  else
  {
    debugPort.println("Magnetometer OK.");
  }

  // 9600 NMEA is the default baud rate
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_ALLDATA);
  
  // Set the update rate to 1Hz
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PMTK_API_SET_FIX_CTL_1HZ);

  // Request updates on antenna status, comment out to keep quiet
  GPS.sendCommand(PGCMD_ANTENNA);
  
  useInterrupt(true);
  debugPort.println("GPS READY.");

  //init temp value
  temperature = (((float)(analogRead(tempSensorPin))*5000/1023)-500)/10;
  debugPort.println("Temperature Sensor initialised.");

  //Init raspberry PI Communication port 
  raspberryPiPort.begin(9600);

  //Init XBee Communication port 
  XBeePort.begin(9600);
  debugPort.println("Communication Ports initialised.");
}

// Interrupt is called once a millisecond, looks for any new GPS data, and stores it
SIGNAL(TIMER0_COMPA_vect) 
{
  char c = GPS.read();

  if (GPS.newNMEAreceived())
  { 
    GPS.parse(GPS.lastNMEA());
  }

// If there are Event data from the Raspberry PI 
  if (raspberryPiPort.available()) 
  {
    char c = raspberryPiPort.read();
    
    //if it is the beginning of the event frame
    if (c == '$')
    {
      eventData = "";
    }
    //if it is the end of the event frame
    else if (c == '#')
    {
      useInterrupt(false); 
      eventFinalData = eventData;
      newEvent = true;
      watchDog = 0;
    }
    else
    {
      //new char to add to the string
      eventData = eventData + c;
    }
  }

  //refresh temps at 10Hz
  if (counter > 100)
  {
    readTemperature();
    counter = 0;
  }

  if (watchDog > 2000)
  {
    useInterrupt(false); 
    eventFinalData = "";
    newEvent = true;
    watchDog = 0;
  }
  watchDog++;
  
  counter++;
}

void useInterrupt(boolean v) 
{
  if (v) 
   {
      // Timer0 is already used for millis() - we'll just interrupt somewhere
      // in the middle and call the "Compare A" function above
      OCR0A = 0xAF;
      TIMSK0 |= _BV(OCIE0A);
      usingInterrupt = true;
    } 
    else
    {
      // do not call the interrupt function COMPA anymore
      TIMSK0 &= ~_BV(OCIE0A);
      usingInterrupt = false;
    }
}

void readMagnetometer()
{
  /* Get a new sensor event */ 
  sensors_event_t event; 
  mag.getEvent(&event);
  char mx[15], my[15], mz[15]; 
  dtostrf(event.magnetic.x, 7, 2, mx);
  dtostrf(event.magnetic.y, 7, 2, my);
  dtostrf(event.magnetic.z, 7, 2, mz);
  sprintf(magnetometerString, "(%s:%s:%s)", mx, my, mz);
}

void readGPS()
{
  readGPSTime();
  readGPSLatitude();
  readGPSLongitude();
}
void readGPSTime()
{
    sprintf(GPSTimeString, "%d:%d:%d.%d", GPS.hour, GPS.minute, GPS.seconds, GPS.milliseconds);
}

void readGPSLatitude()
{
      char latitudeDegrees[15]; 
      dtostrf(GPS.latitudeDegrees, 10, 4, latitudeDegrees);
      sprintf(GPSLatitudeString, "%s%c", latitudeDegrees, GPS.lat);
}

void readGPSLongitude()
{
      char longitudeDegrees[15]; 
      dtostrf(GPS.longitudeDegrees, 10, 4, longitudeDegrees);
      sprintf(GPSLongitudeString, "%s%c", longitudeDegrees, GPS.lon);
}

void readTemperature()
{
  temperature = lambda * (((float)(analogRead(tempSensorPin))*5000/1023)-500)/10 + (1 - lambda) * temperature;
  dtostrf(temperature, 4, 4, temperatureString);
}

void transmitData() 
{
  readMagnetometer();
  readGPS();
  
  String txdata = "";

  if (eventFinalData.length() > 0)
  {
   txdata = "[e,";
  txdata += String(GPSTimeString) + ", ";
  txdata += String(GPSLongitudeString) + ", ";
  txdata += String(GPSLatitudeString) + ", ";
  txdata += String(temperatureString) + ", ";
  txdata += String(magnetometerString) + ", ";
  txdata += String(eventFinalData);
  txdata += "]";
  }
  else
  {
    txdata = "[u,";
    txdata += String(GPSTimeString) + ", ";
    txdata += String(GPSLongitudeString) + ", ";
    txdata += String(GPSLatitudeString);
    txdata += "]";
  }

  int tmp_length = txdata.length();
  String tmp = "";
  for (int i = 0; i < tmp_length; i++) 
  {
     char c = txdata.charAt(i);
     if( c != ' ')
     {
        tmp = tmp + c;
     }
  }

  txdata = tmp;
//  debugPort.println(txdata);
  
  int datalength = txdata.length();

  byte frameType = 0x10;
  byte frameID = 0x01;
  byte destAddr[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
  byte deviceAddr[] = {0xFF, 0xFE};
  byte broadcastRadius = 0x00;
  byte options = 0x00;
  
  byte *RF_Data = new byte[datalength];
  txdata.getBytes(RF_Data, datalength+1); 
 
  //int length = 14+sizeof(RF_Data);                     
  int length = 14 + datalength;
  
  byte packet[length+4];
  packet[0] = 0x7E;
  packet[1] = (length >> 8) & 0xff;
  packet[2] = length & 0xff;
  packet[3] = frameType;
  packet[4] = frameID;
  for (int i = 0; i < 8; i++) {packet[5+i] = destAddr[i];}
  for (int i = 0; i < 2; i++) {packet[13+i] = deviceAddr[i];}
  packet[15] = broadcastRadius;
  packet[16] = options;
  for (int i = 0; i < datalength; i++) {packet[17+i] = RF_Data[i];}
  packet[3+length] = calculateChecksum(packet, length);
  
  sendPacket(packet, length+4);

  delete RF_Data;
}

byte calculateChecksum(byte packet[], int length) {
  // length - length of bytes between the length and checksum fields
  int sum = 0;
  for (int i = 0; i < length; i++) {sum += packet[3+i];}
  return (0xFF - (sum & 0xFF));
}

void sendPacket(byte packet[], int length) {
  for (int i = 0; i < length; i++) {
    XBeePort.write(packet[i]);
//    Serial.print(packet[i], HEX);
//    Serial.print(" ");
  }
//  Serial.println();
}

void loop()
{
  if (newEvent)
  {
    newEvent = false;
    transmitData();
    useInterrupt(true); 
  }
  else
  {
    delay(1000);
  }
}
