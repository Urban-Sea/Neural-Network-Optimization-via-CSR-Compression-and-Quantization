#include <Arduino.h>
#include "model_parameters40.h"
#include "model_parameters_csr_quantized40.h"

// ========== モデル設定 ==========
// 注意: この値は学習時に使用したHIDDEN_DIMと一致させること
#ifndef HIDDEN_DIM
#define HIDDEN_DIM 40  // 隠れ層の次元（学習時の値と一致させる）
#endif
// =================================

// RGB点灯遅延
#define RgbFlashDelay 50 

// ピン割り当て
#define PIN_IN A0
#define led_r_pin 8
#define led_g_pin 6
#define led_b_pin 7
#define buttonInputPin 3
#define buttonMinMaxPin 2

// ボタン押下を検知する変数 (余計な最適化を防ぐため、volatile宣言をしている)
volatile bool buttonInputPressed = false;
volatile bool buttonMinMaxPressed = false;

// RGB読み取り用変数
float r=0, g=0, b=0;
float r_max=512, g_max=512, b_max=512;
float r_min=0, g_min=0, b_min=0;

float rgb[3]{0, 0, 0};
float RGBInput[3]{0, 0, 0};
float RGBOutput[3]{0, 0, 0};

// RGBデータメモリ
int N, M;
float **array;
int n=0, m=0;

int pushed = 0;

void buttonInput() {
    buttonInputPressed = true;
}

void buttonMinMax() {
    buttonMinMaxPressed = true;
}

float **allocateArray(int N, int M) {
    float **array = (float **)malloc(N * sizeof(float *)); // 行ポインタの確保
    if (array == NULL) {
        Serial.println("メモリ確保失敗");
        return NULL;
    }

    for (int i = 0; i < N; i++) {
        array[i] = (float *)malloc(M * sizeof(float)); // 各行のメモリ確保
        if (array[i] == NULL) {
            Serial.println("メモリ確保失敗（部分的）");
            // 確保済みのメモリを解放して終了
            for (int j = 0; j < i; j++) {
                free(array[j]);
            }
            free(array);
            return NULL;
        }
    }
    return array;
}

void read(){
    for(int count = 0 ; count < 3 ; count++){
        if(count == 0){
            analogWrite(led_r_pin, 255);
            analogWrite(led_g_pin,   0);
            analogWrite(led_b_pin,   0);
            delay(RgbFlashDelay);
            rgb[0] = analogRead(PIN_IN);
        }else if(count == 1){
            analogWrite(led_r_pin,   0);
            analogWrite(led_g_pin, 255); 
            analogWrite(led_b_pin,   0);
            delay(RgbFlashDelay);
            rgb[1] = analogRead(PIN_IN);
        }else{
            analogWrite(led_r_pin,   0);
            analogWrite(led_g_pin,   0);
            analogWrite(led_b_pin, 255);
            delay(RgbFlashDelay);     
            rgb[2] = analogRead(PIN_IN);
        }
    }
    analogWrite(led_r_pin, 0);
    analogWrite(led_g_pin, 0);
    analogWrite(led_b_pin, 0);
}

static inline float relu(float x){ return x > 0 ? x : 0; }

// 量子化対応のCSR層（1層目、int8_tデータをfloatに逆量子化しながら計算）
void layer1_csr_quantized_relu(const float x[3], float h1[HIDDEN_DIM]){
	for(int r=0;r<HIDDEN_DIM;++r){
		float s = 0.0f;
		uint16_t start = indptr_1[r];
		uint16_t end   = indptr_1[r+1];
		for(uint16_t p=start;p<end;++p){
			uint16_t c = indices_1[p];
			// int8_tをfloatに逆量子化
			float weight_val = (float)data_1_quantized[p] / scale_factor_1;
			s += weight_val * x[c];
		}
		s += bias_1[r];
		h1[r] = relu(s);
	}
}

// 量子化対応のCSR層（2層目、int8_tデータをfloatに逆量子化しながら計算）
void layer2_csr_quantized_relu(const float h1[HIDDEN_DIM], float h2[HIDDEN_DIM]){
	for(int r=0;r<HIDDEN_DIM;++r){
		float s = 0.0f;
		uint16_t start = indptr_2[r];
		uint16_t end   = indptr_2[r+1];
		for(uint16_t p=start;p<end;++p){
			uint16_t c = indices_2[p];
			// int8_tをfloatに逆量子化
			float weight_val = (float)data_2_quantized[p] / scale_factor_2;
			s += weight_val * h1[c];
		}
		s += bias_2[r];
		h2[r] = relu(s);
	}
}

void layer3_dense(const float h2[HIDDEN_DIM], float y[3]){
	for(int m=0;m<3;++m){
		float s = bias_3[m];
		for(int k=0;k<HIDDEN_DIM;++k) s += weight_3[m*HIDDEN_DIM + k] * h2[k];
		y[m] = s;
	}
}

// 使いやすい forward
static void forward_rgb(const float in_rgb[3], float out_rgb[3]){
	float h1[HIDDEN_DIM], h2[HIDDEN_DIM];
	layer1_csr_quantized_relu(in_rgb, h1);
	layer2_csr_quantized_relu(h1, h2);
	layer3_dense(h2, out_rgb);
}

// Arduino's analog input detects 0-5V with 10-bit values
// https://deviceplus.jp/arduino/arduino_f07/
void readAndProcess(){
    read();
    RGBInput[0] = (float(rgb[0])-r_min)/r_max;
    RGBInput[1] = (float(rgb[1])-g_min)/g_max;
    RGBInput[2] = (float(rgb[2])-b_min)/b_max;
    
    // ニューラルネットで読み込み値を修正
    micros();
    forward_rgb(RGBInput, RGBOutput);
    micros();
    
    // 0-255でクリッピング
    RGBOutput[0] = min(max(RGBOutput[0]*255, 0), 255);
    RGBOutput[1] = min(max(RGBOutput[1]*255, 0), 255);
    RGBOutput[2] = min(max(RGBOutput[2]*255, 0), 255);

    Serial.println("Blue:"+String((int)RGBOutput[2]) + ", Red:"+String((int)RGBOutput[0]) + ", Green:"+ String((int)RGBOutput[1]));
}

void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600);
    pinMode(led_r_pin, OUTPUT);
    pinMode(led_g_pin, OUTPUT);
    pinMode(led_b_pin, OUTPUT);
    analogWrite(led_r_pin, 0);
    analogWrite(led_b_pin, 0);
    analogWrite(led_g_pin, 0);

    pinMode(buttonInputPin, INPUT_PULLUP);pinMode(buttonMinMaxPin, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(buttonInputPin), buttonInput, FALLING);
    attachInterrupt(digitalPinToInterrupt(buttonMinMaxPin), buttonMinMax, FALLING);

    Serial.println("画像の Height（行数）を入力してください: ");
    while (Serial.available() == 0) {
        // 何もせずに待機
    }
    N = Serial.parseInt();
    M = N*3; // RGBの値を入れるために3倍しておく
    Serial.println("Height: " + String(N));
    Serial.println("Width: " + String((int)(M/3)));
    array = allocateArray(N, M);

    if (array == NULL) {
        Serial.println("配列の確保に失敗");
        return;
    }

    // 配列を初期化
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            array[i][j] = 0;
        }
    }
}

void loop() {
  // put your main code here, to run repeatedly:
    readAndProcess();

    if (buttonInputPressed) {
        array[n][m]   = RGBOutput[0];
        array[n][m+1] = RGBOutput[1];
        array[n][m+2] = RGBOutput[2];

        Serial.println(String(n)+" 行目 "+String((int)(m/3))+" 列目 の画素を読み込みました。");

        if((m+=3)>=M){
            m = 0 ;
            if((n+=1)>=N){
                n = 0;
                Serial.println("画像の読み取りが完了しました。");
                Serial.println("以下のテキストを画像ファイル（.ppm）に貼り付けてください。");
                Serial.println("--------------------------------------------------");
                Serial.println("P3");
                Serial.println(String(N)+" "+String((int)(M/3)));
                Serial.println("255");
                for (int i = 0; i < N; i++) {
                    for (int j = 0; j < M; j++) {
                        Serial.print((int)array[i][j]);
                        Serial.print(" ");
                    }
                    Serial.println();
                }
                Serial.println("--------------------------------------------------");
                Serial.println();
                delay(500); 
                NVIC_SystemReset();
            } 
        }
        buttonInputPressed = false;
    }

    if (buttonMinMaxPressed) {
        if(pushed%2==0){
            r_min=rgb[0], g_min=rgb[1], b_min=rgb[2];
            Serial.println("最小値が更新されました："+String(b_min)+","+String(r_min)+","+String(g_min));
        }
        else{
            r_max=rgb[0]-r_min, g_max=rgb[1]-g_min, b_max=rgb[2]-b_min;
            Serial.println("最大値が更新されました："+String(b_max)+","+String(r_max)+","+String(g_max));
        }
        buttonMinMaxPressed = false;  // フラグをリセット
        pushed++;
        delay(500);
    }
}

