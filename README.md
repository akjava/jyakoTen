# JyakoTen
## History
0.2 Totally format Changed(But not release yet)
## how to install
pip install jyakoTen

## What is this
JyakoTen is Japanese Text recognized by Whisper or FasterWhisper

This is mainly whether TTS was able to pronounce the voice correctly. Or to quantify how well the voice chanager has retained the original pronunciation.
The voice data created by TTS/Voice Changer is then recognized by the FasterWhisper tool or other voice recognition tools.
　By comparing the correct text with the created text, the degree to which the voice is correctly pronounced can be quantified.

CER(Character Error Rate) and PER(Phonome Error Rate)

## これは何?(Japanese)
これは、主にTTSが正しく音声を発音できたか。あるいはボイスチャンジャーがどの程度元の発音を保てているかを数値化するためのものです。

TTS/Voice Changerが作成した音声データーをFasterWhisperツール等で音声認識させます。
この作成されたテキストと、正しいテキストを比べることで、どの程度正しく音声が、発音されているかを数値化します。

カナに変換してのCERを取るのと、Phonomeに分解して、Phonome Error Rate風のスコアをSequenceMatcherで取得(EditDistanceは遅かった)しています。
かなり、いいスコアになります。

PERと言い切るのは、もう少し検証と改良が必要です。
## 結果の見方
ja005_2799_recitation_cer-0.065_score(319.805 of 324)_spk_single

これは、ja005というモデルのepoch2799がita-recitation出力したテキストを検証した結果、

CERは0.065
jyako点は、319.8/324 です。(CERも低いし、jyako点は高いので、よく聞き取れる音声です。)

```
index,cer,jyakoten01,transcript_text,detected_text,detected_kana,transcript_phonome,detected_phonome,success_phonome,faild_phonome
001,0.133,0.958,オンナノコガキッキッウレシソー,女の子がきっきぐれしそう,オンナノコガキッキグレシソウ,o N na no ko ga ki cl ki cl u re shi so o,o N n a n o k o g a k i cl k i g u r e sh i s o o,o N o,na no ko ga ki cl ki cl u re shi so
002,0.364,0.903,ツァツォニリョコーシタ,さつおに旅行した,サツオニリョコーシタ,tsa tso ni ryo ko o shi ta,s a ts u o n i ry o k o o sh i t a,o,tsa tso ni ryo ko shi ta
```