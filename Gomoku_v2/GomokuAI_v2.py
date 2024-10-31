import os
import requests
import json

class GomokuAI_v2:
    def __init__(self):
        # 获取 API Key，若环境变量未设置则使用默认值 传入你的api-key到"your_api_key_here"，或者配置到环境变量“DASHSCOPE_API_KEY中
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "your_sk-751c5c38f1d54c93839ba8674ff89acaapi_key_here")

        # 输出当前使用的 API Key（仅用于调试，请勿在生产环境中使用）
        print(f"Current API Key: {self.api_key}")

        # 检查是否成功获取 API Key
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError("API Key 未正确设置。请设置环境变量 DASHSCOPE_API_KEY 或直接在代码中提供。")

        # 初始化API URL
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def get_best_move(self, board, player):

        # 提示内容更新：在提示中加入条件性说明，以防 AI 选择非空位置
        def generate_messages(invalid_move=None):
            board_str = self.format_board(board)
            base_content = f'''The Gomoku board is represented as a 15x15 grid below, where:
                - "0" represents an empty cell
                - "1" represents player 1's stone
                - "2" represents player 2's stone

                Current Board:
                {board_str}

                It's currently player {player}'s turn. 

                Summary of Gomoku Rules: Gomoku is a two-player strategic board game on a 15x15 grid. 
                Players take turns placing one piece at a time on any unoccupied cell. 
                The goal is to be the first to form an unbroken line of five of one's own pieces horizontally, vertically, or diagonally in the Board matrix.
                 
                suggestions:
                - you can analyze board based on pruning algorithm, such as:
                    - Minimax
                    - TSS, Threat Space Search
                    - Monte Carlo Tree Search
                    - Limited Depth First Search or Local Depth First Search
                - or use other algorithms to find the best move.
                **Important:** 
                Please return only the best move coordinates in the format `row, col`. 
                Ensure that:
                - The cell at `row, col` is empty (represented by "0") on the current board.
        '''
            # 打印 base_content 内容
            print("prompt:", base_content+'\n'+'='*50)
            if invalid_move:
                base_content += f'\n\nThe coordinates you previously provided, `{invalid_move}`, were not an empty cell. Please provide an alternative empty cell.'

            return [
                {'role': 'system', 'content': 'You are a Gomoku playing assistant, tasked with helping the user find the best move in the current game board state.'},
                {'role': 'user', 'content': base_content}
            ]

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        data = {
            'model': 'qwen-plus',
            'max_tokens': 100,
            'temperature': 0.9,
            'top_p': 0.9
        }


        try:
            for attempt in range(3):
                # 第一次尝试不传递 invalid_move 参数，后续尝试会传递
                messages = generate_messages(invalid_move=None if attempt == 0 else invalid_move)
                data['messages'] = messages
                response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        # 检查是否为指定格式 row,col
                        if ',' in content:
                            try:
                                row, col = map(int, content.strip().split(','))
                                # 验证返回的坐标是否为空位
                                if 0 <= row < len(board) and 0 <= col < len(board[0]) and board[row][col] == 0:
                                    print("Best Move Coordinates:", row, col)
                                    return row, col
                                else:
                                    invalid_move = f"{row}, {col}"  # 存储无效坐标
                                    print(f"Attempt {attempt + 1}: Selected cell ({row}, {col}) is not empty. Retrying...")
                            except ValueError:
                                print("Unexpected response format:", content)
                        else:
                            print("Unexpected response format:", content)
                    else:
                        print("Unexpected response structure:", result)
                else:
                    print(f"Error calling Qwen API: Status code {response.status_code}, Response: {response.text}")
            print("Failed to find a valid move after multiple attempts. Using fallback move.")
            # 如果 AI 连续3次尝试均未找到空位，则执行备用逻辑
            return self.find_fallback_move(board, player)
        except Exception as e:
            print("Error calling Qwen API:", e)
            return None, None

    def find_fallback_move(self, board, player):
        opponent = 3 - player  # 对手的标志
        best_length = 0
        best_move = None

        # 遍历棋盘，寻找对手最长的连续线段
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == opponent:
                    for dr, dc in directions:
                        length = self.count_consecutive(board, row, col, dr, dc, opponent)
                        if length > best_length:
                            # 检查该线段的两端，确保端点是空位
                            end_row, end_col = row + length * dr, col + length * dc
                            if 0 <= end_row < len(board) and 0 <= end_col < len(board[0]) and board[end_row][end_col] == 0:
                                best_length = length
                                best_move = (end_row, end_col)

        # 如果找到对手的最长连续线段顶点为空位，返回该坐标作为备用
        if best_move:
            print("Fallback Move Coordinates:", best_move)
            return best_move
        else:
            print("No suitable fallback move found.")
            return None, None

    def count_consecutive(self, board, row, col, dr, dc, player):
        count = 0
        while 0 <= row < len(board) and 0 <= col < len(board[0]) and board[row][col] == player:
            count += 1
            row += dr
            col += dc
        return count

    def format_board(self, board):
        # 格式化棋盘为字符串形式，以便传递给API
        return '\n'.join([' '.join(map(str, row)) for row in board])
