# JyakoTen
## History
0.2 Totally format Changed(But not release yet)
## how to install
pipのは古い。更新が多くてUpdateできない

```
git clone https://github.com/akjava/jyakoTen
cd jyakoTen
pip install .
```

## What is this
JyakoTen is Japanese Text recognized by Whisper or FasterWhisper

This is mainly whether TTS was able to pronounce the voice correctly. Or to quantify how well the voice chanager has retained the original pronunciation.
The voice data created by TTS/Voice Changer is then recognized by the FasterWhisper tool or other voice recognition tools.
　By comparing the correct text with the created text, the degree to which the voice is correctly pronounced can be quantified.

CER(Character Error Rate) and MER(Mora Error Rate),PER(Phonome Error Rate)

## これは何?(Japanese)
これは、主にTTSが正しく音声を発音できたか。あるいはボイスチャンジャーがどの程度元の発音を保てているかを数値化するためのものです。

TTS/Voice Changerが作成した音声データーをFasterWhisperツール等で音声認識させます。
この作成されたテキストと、正しいテキストを比べることで、どの程度正しく音声が、発音されているかを数値化します。

特徴としては、Whisperからのカナ変換の難しさに対応するべく、多数のカナ変換校を呼び出し、一番似ているのを採用しています。

## 結果の見方
ja005_2799_recitation_total-324_cer-kanji-0.160_kana-0.065_mer-0.019_per-0.016_spk_single

- ja005 - modelの名前
- 2799 - checkpointのepoch
- recitation - 出力したtranscript名
- total-324 - 324行ありました
- cer-kanji - 漢字のCER
- kana-cer - カナに変換してのCER
- mer - Mora-Error-Rate (モーラーと呼ばれるカナに近い形式・Ka,Ki,Ku,Ke,Ko)
- per - Phonome-Error-Rate (母音と子音単位・K a K i K u K e K o)
- pk_single - singleだと単独話者モデル・マルチスピーカーだと話者番号

中身

```
index,kanji_cer,kana_cer,mora_er,phonome_er,transcript_kanji,transcript_kana,detected_kanji,detected_kana,best_kana,transcript_mora,detected_mora,diff_mora
001,0.417,0.133,0.103,0.091,女の子がキッキッ嬉しそう,オンナノコガキッキッウレシソー,女の子がきっきぐれしそう,オンナノコガキッキグレシソー,オンナノコガキッキグレシソー,o N na no ko ga ki cl ki cl u re shi so o,o N na no ko ga ki cl ki gu re shi so o,o N na no ko ga ki cl ki -gu +cl +u re shi so o
002,0.444,0.364,0.235,0.154,ツァツォに旅行した,ツァツォニリョコーシタ,さつおに旅行した,サッオニリョコーシタ,サツオニリョコーシタ,tsa tso ni ryo ko o shi ta,sa tsu o ni ryo ko o shi ta,-sa +tsa +tso -tsu -o ni ryo ko o shi ta
```

- 注目すべきはMER
- CERはいらないと思ってますが、互換性のため載せます。
- エラーレートの高さ 漢字 > カナ > モーラ > 音素
- 漢字CERは、ほとんど無意味かも。（音声認識で漢字になるか、平仮名になるかは運次第)
- カナとモーラ - カナの表記の違いはある程度、モーラで同じになります。
- PER - 大抵子音と母音のどちらか片方が違うことが多いので、MERに比べてPERは低くなります。逆に大差ない場合、文字が増えてることが多い
- PERはボーダーラインとして使える - 多少 PERあっても、曖昧母音・子音がぶれただけのことが多いので、ラベルの正確さには大差さはない
- diff_mora - 分析に役立つかもしれない

## 計算方法
Matcha-TTS-Japaneseのモデルの性能評価は、ITA-Recitaionというコーパスの324文をTTS出力して、それをWhisperで読み込み、どこまで正しく認識できるかで評価しています。

テストが圧倒的に足りない。

### CERの計算
```
def get_cer(transcript, detect):
    if detect == "":
        return 0
    d = edit_distance(transcript, detect)
    cer = float(d) / max(len(transcript), len(detect))  
    return cer
```

### MERの計算
最終的には、CERで計算してますが、その過程で、各モーラごとに、１文字の記号に変換しています。
```
ryo ko o shi ta
ryo ko u shi te

上記を以下に変換。変換した文字をCER

ABCDE
ABFDG
```

### PERの計算
最終的には、CERで計算してますが、その過程で、各モーラごとに、２文字の記号に変換しています。（モーラのままだと、文字数の違いでErrorレートが変わるため)
```
ryo ko o shi ta
ryo ko u shi te

上記を以下に変換。変換した文字をCER

Ao Bo oo Ci Da
Ao Bo uu Ci De
```