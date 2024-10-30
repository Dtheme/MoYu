import os
from openai import OpenAI

class GomokuAI_v2:
    def __init__(self):
        # 初始化百炼 API 客户端
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def get_best_move(self, board, player):
        # 使用百炼API的AI逻辑来计算最佳落子位置
        messages = [
            {'role': 'system', 'content': 'You are a Gomoku playing assistant.'},
            {'role': 'user', 'content': f'当前棋局: {self.format_board(board)} 玩家: {player}，请给出最佳落子位置。'}
        ]
        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=messages
            )
            response = completion.choices[0].message["content"]
            # 假设百炼返回格式为 "row,col"，需要解析为元组
            row, col = map(int, response.strip().split(','))
            return row, col
        except Exception as e:
            print("Error calling BaiLian AI:", e)
            return None, None

    def format_board(self, board):
        # 格式化棋盘为字符串形式，以便传递给API
        return '|'.join([''.join(map(str, row)) for row in board])
