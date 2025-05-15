import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=500):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.pe = pe.unsqueeze(0)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)].to(x.device)

class PoseFormer(nn.Module):
    def __init__(self, input_size=132, d_model=128, num_classes=419, nhead=4, num_layers=4):
        super().__init__()
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model))
        self.input_proj = nn.Sequential(
            nn.Linear(input_size, d_model),
            nn.LayerNorm(d_model)
        )
        self.pos_enc = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=256,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, num_classes)

    def forward(self, x):
        B = x.size(0)
        x = self.input_proj(x)
        cls_tokens = self.cls_token.expand(B, 1, -1)  # (B, 1, d_model)
        x = torch.cat((cls_tokens, x), dim=1)         # (B, 31, d_model)
        x = self.pos_enc(x)
        x = self.transformer(x)
        return self.fc(x[:, 0])  # Use CLS token
