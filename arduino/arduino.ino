float value;
float voltage;
int x = 0;
void setup(){
  Serial.begin(9600);
  pinMode(6, OUTPUT);
}

void loop(){
  
  value = analogRead(A7);
  voltage = value*(5.0/1023.0);
  x = Serial.readString().toInt();
  analogWrite(6,x);
  Serial.println(voltage);
  delay(500);
}
