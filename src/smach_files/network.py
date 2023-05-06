#coding:utf-8
import sys
sys.path.append('..')  # 親ディレクトリのファイルをインポートするための設定
import numpy as np
import torch
import torch.nn as nn

# deviceの設定(GPUを使う場合)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class Encoder(nn.Module):
    def __init__(self, vocab_size=10000, wordvec_size=100, hidden_size=100, dropout_ratio=0.5, vocab=None):
        super(Encoder, self).__init__()
        V, D, H = vocab_size, wordvec_size, hidden_size

        # レイヤの生成
        self.embed = nn.Embedding(V, D, padding_idx=vocab.stoi['<pad>'])
        self.lstm = nn.LSTM(D, H, num_layers=1, bias=True, batch_first=True, dropout=dropout_ratio)
        #self.affine = nn.Linear(H, V, bias=True)
        self.dropout = nn.Dropout(dropout_ratio)

        # 重みの初期化
        nn.init.normal_(self.embed.weight, std=0.01)
        nn.init.normal_(self.lstm.weight_ih_l0, std=1/np.sqrt(D))
        nn.init.normal_(self.lstm.weight_hh_l0, std=1/np.sqrt(H))
        nn.init.zeros_(self.lstm.bias_ih_l0)
        nn.init.zeros_(self.lstm.bias_hh_l0)
        #self.affine.weight = self.embed.weight      # 重みの共有
        #nn.init.zeros_(self.affine.bias)


    def forward(self, xs):
        xs = self.embed(xs)
        xs, h = self.lstm(xs)
        #score = self.affine(xs)
        return xs, h


class AttentionDecoder(nn.Module):
    def __init__(self, vocab_size=10000, wordvec_size=100, hidden_size=100, dropout_ratio=0.5, batch_size=100, vocab=None):
        super(AttentionDecoder, self).__init__()
        V, D, H = vocab_size, wordvec_size, hidden_size
        self.H = H
        self.batch_size = batch_size

        # レイヤの生成
        self.embed = nn.Embedding(V, D, padding_idx=vocab.stoi['<pad>'])
        self.lstm = nn.LSTM(D, H, num_layers=1, bias=True, batch_first=True, dropout=dropout_ratio)
        self.affine = nn.Linear(H * 2, V, bias=True)        # H * 2 : 各系列のLSTMの隠れ層とAttention層で計算したコンテキストベクトルをtorch.catでつなぎ合わせることで長さが２倍になるため
        self.dropout = nn.Dropout(dropout_ratio)
        self.softmax = nn.Softmax(dim=1)                    #列方向

        # 重みの初期化
        nn.init.normal_(self.embed.weight, std=0.01)
        nn.init.normal_(self.lstm.weight_ih_l0, std=1/np.sqrt(D))
        nn.init.normal_(self.lstm.weight_hh_l0, std=1/np.sqrt(H))
        nn.init.zeros_(self.lstm.bias_ih_l0)
        nn.init.zeros_(self.lstm.bias_hh_l0)
        nn.init.normal_(self.affine.weight, std=1/np.sqrt(H))
        nn.init.zeros_(self.affine.bias)


    def forward(self, xs, hs, h):
        xs = self.embed(xs)
        output, state = self.lstm(xs, h)
        # Attention層
        # hs.size() = ([100, 29, 128])
        # output.size() = ([100, 10, 128])
        t_output = torch.transpose(output, 1, 2)    # t_output.size() = ([100, 128, 10])

        # bmm(batch marix * matrix)でバッチも考慮してまとめて行列計算
        s = torch.bmm(hs, t_output) # s.size() = ([100, 29, 10])

        # 列方向(dim=1)でsoftmaxをとって確率表現に変換
        # この値を後のAttentionの可視化などにも使うため、returnで返しておく
        attention_weight = self.softmax(s) # attention_weight.size() = ([100, 29, 10])
        #print('a_weight : ', attention_weight.size(0))
        # コンテキストベクトルをまとめるために入れ物を用意
        c = torch.zeros(self.batch_size, 1, self.H, device=device) # c.size() = ([100, 1, 128])
        #c = torch.zeros(attention_weight.size(0), 1, self.H, device=device) # c.size() = ([100, 1, 128])

        # 各DecoderのLSTM層に対するコンテキストベクトルをまとめて計算する方法がわからなかったので、
        # 各層（Decoder側のGRU層は生成文字列が10文字なので10個ある）におけるattention weightを取り出してforループ内でコンテキストベクトルを１つずつ作成する
        # バッチ方向はまとめて計算できたのでバッチはそのまま
        for i in range(attention_weight.size()[2]): # 10回ループ

            # attention_weight[:,:,i].size() = ([100, 29])
            # i番目のGRU層に対するattention weightを取り出すが、テンソルのサイズをhsと揃えるためにunsqueezeする
            unsq_weight = attention_weight[:,:,i].unsqueeze(2) # unsq_weight.size() = ([100, 29, 1])

            # hsの各ベクトルをattention weightで重み付けする
            weighted_hs = hs * unsq_weight # weighted_hs.size() = ([100, 29, 128])

            # attention weightで重み付けされた各hsのベクトルをすべて足し合わせてコンテキストベクトルを作成
            weight_sum = torch.sum(weighted_hs, axis=1).unsqueeze(1) # weight_sum.size() = ([100, 1, 128])

            #print('c : ', c.size())
            #print('weight_sum : ', weight_sum.size())
            c = torch.cat([c, weight_sum], dim=1) # c.size() = ([100, i, 128])

        # 箱として用意したzero要素が残っているのでスライスして削除
        c = c[:,1:,:]

        output = torch.cat([output, c], dim=2) # output.size() = ([100, 10, 256])
        output = self.affine(output)
        return output, state, attention_weight





