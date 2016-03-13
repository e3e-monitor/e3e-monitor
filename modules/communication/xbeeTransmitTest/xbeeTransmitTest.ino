HardwareSerial &XBeePort = Serial3;
  
void setup() {
  XBeePort.begin(9600);

}

void loop() {
  transmitDataSample();
  delay(1000);

}

void transmitDataSample() {
  
  byte frameType = 0x10;
  byte frameID = 0x01;
  byte destAddr[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
  byte deviceAddr[] = {0xFF, 0xFE};
  byte broadcastRadius = 0x00;
  byte options = 0x00;
  byte RF_Data[] = { 'h', 'e', 'l', 'l', 'o' };
  int length = 14+sizeof(RF_Data);                     
  
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
  for (int i = 0; i < sizeof(RF_Data); i++) {packet[17+i] = RF_Data[i];}
  packet[3+length] = calculateChecksum(packet, length);
  
  sendPacket(packet, length+4);
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

  }

}
