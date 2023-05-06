# coding:utf-8
import warnings
warnings.filterwarnings('ignore')           # 警告文の無視
import sys
import os
import re
import torch
import torch.nn as nn
from smach_files import network ,lists, dicts


# ルール外の問題文が出た例外処理
class CommandAnalyzer():
    def __init__(self) -> None:
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # パラメータ設定
        self.sen_length = 30
        self.output_len = 20
        self.batch_size = 2
        self.wordvec_size = 300
        self.hidden_size = 650
        self.dropout = 0.5
        self.learning_rate = 0.001
        self.momentum=0
        self.max_grad = 0.25
        self.eval_interval = 20

        # モデルのパス
        self.model_num = 13
        self.dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
        self.encoder_path = "{}/model/encoder_epoch{}.pth".format(self.dir_path, self.model_num)
        self.decoder_path = "{}/model/decoder_epoch{}.pth".format(self.dir_path, self.model_num)
        self.text_vocab_path = "{}/model/text_vocab.pth".format(self.dir_path)
        self.label_vocab_path = "{}/model/label_vocab.pth".format(self.dir_path)

        #辞書ベクトルの読み込み
        self.text_vocab = torch.load(self.text_vocab_path)
        self.label_vocab = torch.load(self.label_vocab_path)
        self.vocab_size = len(self.text_vocab.itos)
        self.label_size = len(self.label_vocab.itos)


        # モデルの生成
        self.encoder = network.Encoder(self.vocab_size, self.wordvec_size, self.hidden_size, self.dropout, self.text_vocab)
        self.decoder = network.AttentionDecoder(self.label_size, self.wordvec_size, self.hidden_size, self.dropout, self.batch_size, self.label_vocab)
        self.encoder.load_state_dict(torch.load(self.encoder_path))
        self.decoder.load_state_dict(torch.load(self.decoder_path))
        self.encoder.to(self.device)                                    # GPUを使う場合
        self.decoder.to(self.device)                                    # GPUを使う場合
        self.criterion = nn.CrossEntropyLoss()                          # 損失の計算
        self.softmax = nn.Softmax(dim=1)


    def tokenize(self, s: str) -> list:
        s = s.lower()
        for p in lists.remove_words:
            s = s.replace(p, '')
        for p in dicts.replace_phrases.keys():
            s = s.replace(p, dicts.replace_phrases[p])
        s = s.replace("'s", "")
        s = re.sub(r" +", r" ", s).strip()
        return s.split()

    def preprocessing(self, s: str) -> str:
        if s in dicts.replace_words.keys():
            return dicts.replace_words[s]
        else:
            return s

    def get_max_index(self, decoder_output):
        results = []
        for h in decoder_output:
            results.append(torch.argmax(h))
        return torch.tensor(results, device=self.device).view(self.batch_size, 1)

    def predict(self, cmd_sen):
        with torch.no_grad():
            # モデルを評価モードへ
            self.encoder.eval()
            self.decoder.eval()
            sentence = ['<pad>' for i in range(self.sen_length)]
            cmd_sen = self.tokenize(self.preprocessing(cmd_sen))
            sentence[self.sen_length-len(cmd_sen):] = cmd_sen
            try:
                x = [self.text_vocab.stoi[w] for w in sentence]
            except Exception as e:
                print("error", e)
                return False
            x = torch.tensor(x*self.batch_size).view(self.batch_size, -1).to(self.device)
            hs, encoder_state = self.encoder(x)

            # Decoderにはまず文字列生成開始を表す"_"をインプットにするので、"_"のtensorをバッチサイズ分作成
            start_char_batch = [[self.label_vocab.stoi["_"]] for _ in range(self.batch_size)]
            decoder_input_tensor = torch.tensor(start_char_batch, device=self.device)

            # 変数名変換
            decoder_hidden = encoder_state

            # バッチ毎の結果を結合するための入れ物を定義
            batch_tmp = torch.zeros(self.batch_size, 1, dtype=torch.long, device=self.device)
            #print(batch_tmp.size())
            # (100,1)

            for _ in range(self.output_len - 1):
                #tqdm.write('hs : {}'.format(hs.size()))
                decoder_output, decoder_hidden, _ = self.decoder(decoder_input_tensor, hs, decoder_hidden)
                # 予測文字を取得しつつ、そのまま次のdecoderのインプットとなる
                decoder_input_tensor = self.get_max_index(decoder_output.squeeze())
                #tqdm.write('dec_in_tsr : {}'.format(decoder_input_tensor.size()))
                # バッチ毎の結果を予測順に結合
                batch_tmp = torch.cat([batch_tmp, decoder_input_tensor], dim=1)

            # 最初のbatch_tmpの0要素が先頭に残ってしまっているのでスライスして削除
            predict_list = [self.label_vocab.itos[idx.item()] for idx in batch_tmp[:,1:][1]]
            #print(p)
            result = dicts.result_dict

            for res, pre in zip(result.keys(), predict_list):
                result[res] = pre
            return result


# この部分は「$ python predict.py」の時には実行される
if __name__ == "__main__":
    command_analyzer = CommandAnalyzer()
    # print('Evaluating......')
    while True:
        try:
            input_str = input("please input command >>")
            result =command_analyzer.predict(input_str)
            print(result)
        except KeyboardInterrupt:
            break
