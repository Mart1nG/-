import turtle
import json
import os
import copy
import time
import random
from datetime import datetime

# ===================== 全局配置 =====================
BOARD_SIZE = 15
CELL_SIZE = 40
screen = turtle.Screen()
screen.setup(width=1.0, height=1.0)
WINDOW_WIDTH = screen.window_width()
WINDOW_HEIGHT = screen.window_height()
BLACK = "black"
WHITE = "white"
BOARD_COLOR = "#F0DCB4"
current_player = "black"
board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
game_over = False
user_info = {"username": "", "logged_in": False}
save_file = "gobang_save.json"
menu_running = True
game_mode = ""
ai_thinking = False
player_first = True  # 玩家是否先手（True:玩家黑棋先手，False:AI黑棋先手）

# ===================== AI 相关类定义 =====================
class Point:
    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __hash__(self):
        return hash((self.X, self.Y))

    def __eq__(self, other):
        return self.X == other.X and self.Y == other.Y

class Node:
    ScoreByNumArount = [0, 5, 15, 30, 50, 70]

    def __init__(self, game_map, ope, depth, alpha, beta, force_score, player_first):
        self.GameMap = [row[:] for row in game_map]
        self.Ope = ope
        self.Depth = depth
        self.Alpha = alpha
        self.Beta = beta
        self.ForceScore = force_score
        self.PlayerFirst = player_first
        self.Score = 0

    def JudgeRes(self):
        # 1 横向五子
        for x in range(11):
            for y in range(15):
                if all(self.GameMap[x+i][y] == 1 for i in range(5)):
                    return 1
                if all(self.GameMap[x+i][y] == 2 for i in range(5)):
                    return 2
        # 2 纵向五子
        for x in range(15):
            for y in range(11):
                if all(self.GameMap[x][y+i] == 1 for i in range(5)):
                    return 1
                if all(self.GameMap[x][y+i] == 2 for i in range(5)):
                    return 2
        # 3 斜向五子（主对角线）
        for x in range(11):
            for y in range(11):
                if all(self.GameMap[x+i][y+i] == 1 for i in range(5)):
                    return 1
                if all(self.GameMap[x+i][y+i] == 2 for i in range(5)):
                    return 2
        # 4 斜向五子（副对角线）
        for x in range(11):
            for y in range(11):
                if all(self.GameMap[x+4-i][y+i] == 1 for i in range(5)):
                    return 1
                if all(self.GameMap[x+4-i][y+i] == 2 for i in range(5)):
                    return 2
        return 0

    def Judge4(self):
        ai_4_num = 0
        player_4_num = 0
        # 横向
        for x in range(11):
            for y in range(15):
                player_cnt = sum(1 for i in range(5) if self.GameMap[x+i][y] == 1)
                ai_cnt = sum(1 for i in range(5) if self.GameMap[x+i][y] == 2)
                if player_cnt == 4 and ai_cnt == 0:
                    player_4_num += 1
                if ai_cnt == 4 and player_cnt == 0:
                    ai_4_num += 1
        # 纵向
        for x in range(15):
            for y in range(11):
                player_cnt = sum(1 for i in range(5) if self.GameMap[x][y+i] == 1)
                ai_cnt = sum(1 for i in range(5) if self.GameMap[x][y+i] == 2)
                if player_cnt == 4 and ai_cnt == 0:
                    player_4_num += 1
                if ai_cnt == 4 and player_cnt == 0:
                    ai_4_num += 1
        # 主对角线
        for x in range(11):
            for y in range(11):
                player_cnt = sum(1 for i in range(5) if self.GameMap[x+i][y+i] == 1)
                ai_cnt = sum(1 for i in range(5) if self.GameMap[x+i][y+i] == 2)
                if player_cnt == 4 and ai_cnt == 0:
                    player_4_num += 1
                if ai_cnt == 4 and player_cnt == 0:
                    ai_4_num += 1
        # 副对角线
        for x in range(11):
            for y in range(11):
                player_cnt = sum(1 for i in range(5) if self.GameMap[x+4-i][y+i] == 1)
                ai_cnt = sum(1 for i in range(5) if self.GameMap[x+4-i][y+i] == 2)
                if player_cnt == 4 and ai_cnt == 0:
                    player_4_num += 1
                if ai_cnt == 4 and player_cnt == 0:
                    ai_4_num += 1
        return ai_4_num, player_4_num

    def Judge3D(self):
        ai_3d_num = 0
        player_3d_num = 0
        # 横向 xooox
        for x in range(11):
            for y in range(15):
                if self.GameMap[x][y] == 0 and all(self.GameMap[x+i][y] == 1 for i in range(1,4)) and self.GameMap[x+4][y] == 0:
                    player_3d_num += 1
                if self.GameMap[x][y] == 0 and all(self.GameMap[x+i][y] == 2 for i in range(1,4)) and self.GameMap[x+4][y] == 0:
                    ai_3d_num += 1
        # 纵向 xooox
        for x in range(15):
            for y in range(11):
                if self.GameMap[x][y] == 0 and all(self.GameMap[x][y+i] == 1 for i in range(1,4)) and self.GameMap[x][y+4] == 0:
                    player_3d_num += 1
                if self.GameMap[x][y] == 0 and all(self.GameMap[x][y+i] == 2 for i in range(1,4)) and self.GameMap[x][y+4] == 0:
                    ai_3d_num += 1
        # 主对角线 xooox
        for x in range(11):
            for y in range(11):
                if self.GameMap[x][y] == 0 and all(self.GameMap[x+i][y+i] == 1 for i in range(1,4)) and self.GameMap[x+4][y+4] == 0:
                    player_3d_num += 1
                if self.GameMap[x][y] == 0 and all(self.GameMap[x+i][y+i] == 2 for i in range(1,4)) and self.GameMap[x+4][y+4] == 0:
                    ai_3d_num += 1
        # 副对角线 xooox
        for x in range(11):
            for y in range(11):
                if self.GameMap[x+4][y] == 0 and all(self.GameMap[x+4-i][y+i] == 1 for i in range(1,4)) and self.GameMap[x][y+4] == 0:
                    player_3d_num += 1
                if self.GameMap[x+4][y] == 0 and all(self.GameMap[x+4-i][y+i] == 2 for i in range(1,4)) and self.GameMap[x][y+4] == 0:
                    ai_3d_num += 1

        # 横向跳三
        for x in range(10):
            for y in range(15):
                if self.GameMap[x][y] == 0 and self.GameMap[x+1][y] == 1 and ((self.GameMap[x+2][y] == 1) ^ (self.GameMap[x+3][y] == 1)) and self.GameMap[x+4][y] == 1 and self.GameMap[x+5][y] == 0:
                    player_3d_num += 1
                if self.GameMap[x][y] == 0 and self.GameMap[x+1][y] == 2 and ((self.GameMap[x+2][y] == 2) ^ (self.GameMap[x+3][y] == 2)) and self.GameMap[x+4][y] == 2 and self.GameMap[x+5][y] == 0:
                    ai_3d_num += 1
        # 纵向跳三
        for x in range(15):
            for y in range(10):
                if self.GameMap[x][y] == 0 and self.GameMap[x][y+1] == 1 and ((self.GameMap[x][y+2] == 1) ^ (self.GameMap[x][y+3] == 1)) and self.GameMap[x][y+4] == 1 and self.GameMap[x][y+5] == 0:
                    player_3d_num += 1
                if self.GameMap[x][y] == 0 and self.GameMap[x][y+1] == 2 and ((self.GameMap[x][y+2] == 2) ^ (self.GameMap[x][y+3] == 2)) and self.GameMap[x][y+4] == 2 and self.GameMap[x][y+5] == 0:
                    ai_3d_num += 1
        # 主对角线跳三
        for x in range(10):
            for y in range(10):
                if self.GameMap[x][y] == 0 and self.GameMap[x+1][y+1] == 1 and ((self.GameMap[x+2][y+2] == 1) ^ (self.GameMap[x+3][y+3] == 1)) and self.GameMap[x+4][y+4] == 1 and self.GameMap[x+5][y+5] == 0:
                    player_3d_num += 1
                if self.GameMap[x][y] == 0 and self.GameMap[x+1][y+1] == 2 and ((self.GameMap[x+2][y+2] == 2) ^ (self.GameMap[x+3][y+3] == 2)) and self.GameMap[x+4][y+4] == 2 and self.GameMap[x+5][y+5] == 0:
                    ai_3d_num += 1
        # 副对角线跳三
        for x in range(10):
            for y in range(10):
                if self.GameMap[x+5][y] == 0 and self.GameMap[x+4][y+1] == 1 and ((self.GameMap[x+3][y+2] == 1) ^ (self.GameMap[x+2][y+3] == 1)) and self.GameMap[x+1][y+4] == 1 and self.GameMap[x][y+5] == 0:
                    player_3d_num += 1
                if self.GameMap[x+5][y] == 0 and self.GameMap[x+4][y+1] == 2 and ((self.GameMap[x+3][y+2] == 2) ^ (self.GameMap[x+2][y+3] == 2)) and self.GameMap[x+1][y+4] == 2 and self.GameMap[x][y+5] == 0:
                    ai_3d_num += 1
        return ai_3d_num, player_3d_num

    def CalcScore(self):
        INF = 10**9
        res = self.JudgeRes()
        if res == 2:
            return 100000  # AI胜利
        if res == 1:
            return -100000  # 玩家胜利

        ai_4_num, player_4_num = self.Judge4()

        # 双四或活四
        if self.PlayerFirst:
            if self.Depth % 2 == 0:
                if player_4_num >= 2:
                    return -90000
                if ai_4_num >= 2 and player_4_num == 0:
                    return 90000
            else:
                if ai_4_num >= 2:
                    return 90000
                if player_4_num >= 2 and ai_4_num == 0:
                    return -90000
        else:
            if self.Depth % 2 == 0:
                if ai_4_num >= 2:
                    return 90000
                if player_4_num >= 2 and ai_4_num == 0:
                    return -90000
            else:
                if player_4_num >= 2:
                    return -90000
                if ai_4_num >= 2 and player_4_num == 0:
                    return 90000

        if not self.ForceScore:
            if self.PlayerFirst:
                if self.Depth % 2 == 0:
                    return INF
                else:
                    return -INF
            else:
                if self.Depth % 2 == 0:
                    return -INF
                else:
                    return INF

        ai_3d_num, player_3d_num = self.Judge3D()

        # 四三
        if self.PlayerFirst:
            if self.Depth % 2 == 0:
                if player_4_num and player_3d_num:
                    return -8000
                if ai_4_num and ai_3d_num:
                    return 8000
            else:
                if ai_4_num and ai_3d_num:
                    return 8000
                if player_4_num and player_3d_num:
                    return -8000
        else:
            if self.Depth % 2 == 0:
                if ai_4_num and ai_3d_num:
                    return 8000
                if player_4_num and player_3d_num:
                    return -8000
            else:
                if ai_4_num and ai_3d_num:
                    return 8000
                if player_4_num and player_3d_num:
                    return -8000

        # 单四
        if self.PlayerFirst:
            if self.Depth % 2 == 0:
                if player_4_num:
                    return -7000
                if ai_4_num:
                    return 7000
            else:
                if ai_4_num:
                    return 7000
                if player_4_num:
                    return -7000
        else:
            if self.Depth % 2 == 0:
                if ai_4_num:
                    return 7000
                if player_4_num:
                    return -7000
            else:
                if ai_4_num:
                    return 7000
                if player_4_num:
                    return -7000

        # 双三
        if self.PlayerFirst:
            if self.Depth % 2 == 0:
                if player_3d_num >= 2:
                    return -6000
                if ai_3d_num >= 2:
                    return 6000
            else:
                if ai_3d_num >= 2:
                    return 6000
                if player_3d_num >= 2:
                    return -6000
        else:
            if self.Depth % 2 == 0:
                if ai_3d_num >= 2:
                    return 6000
                if player_3d_num >= 2:
                    return -6000
            else:
                if ai_3d_num >= 2:
                    return 6000
                if player_3d_num >= 2:
                    return -6000

        # 单活三
        if self.PlayerFirst:
            if self.Depth % 2 == 0:
                if player_3d_num:
                    return -500
                if ai_3d_num:
                    return 500
            else:
                if ai_3d_num:
                    return 500
                if player_3d_num:
                    return -500
        else:
            if self.Depth % 2 == 0:
                if ai_3d_num:
                    return 500
                if player_3d_num:
                    return -500
            else:
                if ai_3d_num:
                    return 500
                if player_3d_num:
                    return -500

        # 基础评分
        player_score_num = 0
        ai_score_num = 0
        player_piece_cnt = 0
        ai_piece_cnt = 0
        for x in range(15):
            for y in range(15):
                if self.GameMap[x][y] == 1:
                    around_cnt = 0
                    for x0 in range(max(0, x-1), min(15, x+2)):
                        for y0 in range(max(0, y-1), min(15, y+2)):
                            if self.GameMap[x0][y0] != 0:
                                around_cnt += 1
                    player_score_num += self.ScoreByNumArount[around_cnt] - abs(x-7) - abs(y-7)
                    player_piece_cnt += 1
                elif self.GameMap[x][y] == 2:
                    around_cnt = 0
                    for x0 in range(max(0, x-1), min(15, x+2)):
                        for y0 in range(max(0, y-1), min(15, y+2)):
                            if self.GameMap[x0][y0] != 0:
                                around_cnt += 1
                    ai_score_num += self.ScoreByNumArount[around_cnt] - abs(x-7) - abs(y-7)
                    ai_piece_cnt += 1
        if ai_piece_cnt == 0 or player_piece_cnt == 0:
            return 0
        return ai_score_num / ai_piece_cnt - player_score_num / player_piece_cnt

    def GetOpeList(self):
        ope_set = set()
        for x in range(15):
            for y in range(15):
                if self.GameMap[x][y] != 0:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x+dx, y+dy
                            if 0 <= nx < 15 and 0 <= ny < 15 and self.GameMap[nx][ny] == 0:
                                ope_set.add(Point(nx, ny))
        # 如果没有相邻点，返回中心点
        if len(ope_set) == 0:
            ope_set.add(Point(7, 7))
        return ope_set

class AI1Step:
    def __init__(self, max_node_num=50000):
        self.MaxNodeNum = max_node_num
        self.MethodTree = []
        self.NextNodeList = []

    def Search(self, cur_node_dx, max_depth):
        cur_node = self.MethodTree[cur_node_dx]
        ope_list = cur_node.GetOpeList()
        
        # 限制候选位置数量以提高速度
        if len(ope_list) > 30:
            scored_opes = []
            for cell in ope_list:
                score = -abs(cell.X-7) - abs(cell.Y-7)
                scored_opes.append((score, cell))
            scored_opes.sort(reverse=True)
            ope_list = [cell for _, cell in scored_opes[:30]]

        for cell in ope_list:
            new_map = [row[:] for row in cur_node.GameMap]
            if cur_node.PlayerFirst:
                if cur_node.Depth % 2 == 0:
                    new_map[cell.X][cell.Y] = 1
                else:
                    new_map[cell.X][cell.Y] = 2
            else:
                if cur_node.Depth % 2 == 0:
                    new_map[cell.X][cell.Y] = 2
                else:
                    new_map[cell.X][cell.Y] = 1

            force_score = not (max_depth >= 2 and len(ope_list) >= 2)
            new_node = Node(new_map, cell, cur_node.Depth+1, cur_node.Alpha, cur_node.Beta, force_score, cur_node.PlayerFirst)
            new_node.Score = new_node.CalcScore()
            new_node_dx = len(self.MethodTree)
            self.MethodTree.append(new_node)
            self.NextNodeList.append(-1)

            if len(self.MethodTree) >= self.MaxNodeNum:
                return

            if -100000 < new_node.Score < 100000:
                if cur_node.PlayerFirst:
                    if cur_node.Depth % 2 == 0:
                        if new_node.Score < cur_node.Score:
                            cur_node.Score = new_node.Score
                            cur_node.Beta = new_node.Score
                            self.NextNodeList[cur_node_dx] = new_node_dx
                    else:
                        if new_node.Score > cur_node.Score:
                            cur_node.Score = new_node.Score
                            cur_node.Alpha = new_node.Score
                            self.NextNodeList[cur_node_dx] = new_node_dx
                else:
                    if cur_node.Depth % 2 == 0:
                        if new_node.Score > cur_node.Score:
                            cur_node.Score = new_node.Score
                            cur_node.Alpha = new_node.Score
                            self.NextNodeList[cur_node_dx] = new_node_dx
                    else:
                        if new_node.Score < cur_node.Score:
                            cur_node.Score = new_node.Score
                            cur_node.Beta = new_node.Score
                            self.NextNodeList[cur_node_dx] = new_node_dx
            else:
                if max_depth >= 1:
                    self.Search(new_node_dx, max_depth-1)
                
                if cur_node.PlayerFirst:
                    if cur_node.Depth % 2 == 0:
                        if new_node.Score < cur_node.Score:
                            cur_node.Score = new_node.Score
                            cur_node.Beta = new_node.Score
                            self.NextNodeList[cur_node_dx] = new_node_dx
                    else:
                        if new_node.Score > cur_node.Score:
                            cur_node.Score = new_node.Score
                            cur_node.Alpha = new_node.Score
                            self.NextNodeList[cur_node_dx] = new_node_dx
                else:
                    if cur_node.Depth % 2 == 0:
                        if new_node.Score > cur_node.Score:
                            cur_node.Score = new_node.Score
                            cur_node.Alpha = new_node.Score
                            self.NextNodeList[cur_node_dx] = new_node_dx
                    else:
                        if new_node.Score < cur_node.Score:
                            cur_node.Score = new_node.Score
                            cur_node.Beta = new_node.Score
                            self.NextNodeList[cur_node_dx] = new_node_dx

                if cur_node.Alpha > cur_node.Beta:
                    return

    def GetFinalRes(self):
        if self.NextNodeList[0] == -1:
            return None
        return self.MethodTree[self.NextNodeList[0]].Ope

# ===================== 初始化绘图 =====================
screen.title("五子棋游戏")
screen.bgcolor(BOARD_COLOR)
screen.tracer(0)

pen = turtle.Turtle()
pen.speed(0)
pen.hideturtle()
pen.penup()

# ===================== 工具函数 =====================
def get_board_center():
    board_total_width = (BOARD_SIZE - 1) * CELL_SIZE
    board_total_height = (BOARD_SIZE - 1) * CELL_SIZE
    center_x = (WINDOW_WIDTH - board_total_width) / 2 - WINDOW_WIDTH / 2
    center_y = (WINDOW_HEIGHT - board_total_height) / 2 - WINDOW_HEIGHT / 2
    return (center_x, center_y)

def get_coords(x, y):
    center_x, center_y = get_board_center()
    col = round((x - center_x) / CELL_SIZE)
    row = round((y - center_y) / CELL_SIZE)
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return (row, col)
    return None

def draw_board():
    pen.clear()
    pen.color(BLACK)
    center_x, center_y = get_board_center()

    for i in range(BOARD_SIZE):
        pen.goto(center_x, center_y + i * CELL_SIZE)
        pen.pendown()
        pen.goto(center_x + (BOARD_SIZE - 1) * CELL_SIZE, center_y + i * CELL_SIZE)
        pen.penup()

    for i in range(BOARD_SIZE):
        pen.goto(center_x + i * CELL_SIZE, center_y)
        pen.pendown()
        pen.goto(center_x + i * CELL_SIZE, center_y + (BOARD_SIZE - 1) * CELL_SIZE)
        pen.penup()

    star_positions = [(7,7), (3,3), (3,11), (11,3), (11,11)]
    for (row, col) in star_positions:
        x = center_x + col * CELL_SIZE
        y = center_y + row * CELL_SIZE
        pen.goto(x, y)
        pen.pendown()
        pen.begin_fill()
        pen.circle(6)
        pen.end_fill()
        pen.penup()
    screen.update()

def draw_piece(row, col, color):
    center_x, center_y = get_board_center()
    x = center_x + col * CELL_SIZE
    y = center_y + row * CELL_SIZE

    piece = turtle.Turtle()
    piece.speed(0)
    piece.hideturtle()
    piece.penup()
    piece.goto(x, y - 18)
    piece.color(color)
    piece.fillcolor(color)
    piece.pendown()
    piece.begin_fill()
    piece.circle(18)
    piece.end_fill()
    screen.update()

def check_win(row, col):
    color = board[row][col]
    directions = [(0,1), (1,0), (1,1), (1,-1)]
    for dr, dc in directions:
        count = 1
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
            count += 1
            r += dr
            c += dc
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == color:
            count += 1
            r -= dr
            c -= dc
        if count >= 5:
            return True
    return False

def is_forbidden_move(r, c, color):
    if color != "black":
        return False

    def check_three_three():
        three_count = 0
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            empty1 = 0
            empty2 = 0

            tr, tc = r + dr, c + dc
            while 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] == color:
                count += 1
                tr += dr
                tc += dc
            if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] is None:
                empty1 = 1
                tr += dr
                tc += dc
                if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] is None:
                    empty1 = 2

            tr, tc = r - dr, c - dc
            while 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] == color:
                count += 1
                tr -= dr
                tc -= dc
            if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] is None:
                empty2 = 1
                tr -= dr
                tc -= dc
                if 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] is None:
                    empty2 = 2

            if count == 3 and empty1 + empty2 >= 2:
                three_count += 1

        return three_count >= 2

    def check_four_four():
        four_count = 0
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            block1 = 0
            block2 = 0

            tr, tc = r + dr, c + dc
            while 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] == color:
                count += 1
                tr += dr
                tc += dc
            if not (0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE) or board[tr][tc] is not None:
                block1 = 1

            tr, tc = r - dr, c - dc
            while 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] == color:
                count += 1
                tr -= dr
                tc -= dc
            if not (0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE) or board[tr][tc] is not None:
                block2 = 1

            if count == 4 and (block1 + block2) <= 1:
                four_count += 1

        return four_count >= 2

    def check_long_line():
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            tr, tc = r + dr, c + dc
            while 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] == color:
                count += 1
                tr += dr
                tc += dc
            tr, tc = r - dr, c - dc
            while 0 <= tr < BOARD_SIZE and 0 <= tc < BOARD_SIZE and board[tr][tc] == color:
                count += 1
                tr -= dr
                tc -= dc
            if count >= 6:
                return True
        return False

    return check_three_three() or check_four_four() or check_long_line()

# ===================== AI落子逻辑 =====================
def convert_board_for_ai():
    """将turtle棋盘格式转换为AI需要的格式（0空,1黑棋,2白棋）"""
    ai_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == "black":
                ai_board[r][c] = 1  # 黑棋
            elif board[r][c] == "white":
                ai_board[r][c] = 2  # 白棋
    return ai_board

def get_quick_move():
    """快速获取AI落子位置（根据AI的颜色）"""
    # 确定AI的颜色
    ai_color = "black" if not player_first else "white"
    player_color = "white" if not player_first else "black"
    
    # 首先检查AI能否直接获胜
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] is None:
                board[r][c] = ai_color
                if check_win(r, c):
                    board[r][c] = None
                    return (r, c, ai_color)
                board[r][c] = None
    
    # 检查玩家是否有获胜位置（防守）
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] is None:
                board[r][c] = player_color
                if check_win(r, c):
                    board[r][c] = None
                    return (r, c, ai_color)
                board[r][c] = None
    
    return None

def fallback_move():
    """备用落子方案"""
    global game_over
    
    # 确定AI的颜色
    ai_color = "black" if not player_first else "white"
    
    # 优先中心区域
    for r in range(max(0, 7-2), min(15, 7+3)):
        for c in range(max(0, 7-2), min(15, 7+3)):
            if board[r][c] is None:
                board[r][c] = ai_color
                draw_piece(r, c, ai_color)
                if check_win(r, c):
                    game_over = True
                    winner = "AI（黑棋）" if ai_color == "black" else "AI（白棋）"
                    turtle.textinput("游戏结束", f"{winner}获胜！")
                    reset_game()
                return
    
    # 随机落子
    empty_cells = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] is None]
    if empty_cells:
        row, col = random.choice(empty_cells)
        board[row][col] = ai_color
        draw_piece(row, col, ai_color)
        if check_win(row, col):
            game_over = True
            winner = "AI（黑棋）" if ai_color == "black" else "AI（白棋）"
            turtle.textinput("游戏结束", f"{winner}获胜！")
            reset_game()

def ai_move_advanced():
    """使用高级AI逻辑进行落子（根据AI的颜色）"""
    global game_over, current_player, ai_thinking
    
    ai_thinking = True
    
    # 显示AI思考提示
    thinking_turtle = turtle.Turtle()
    thinking_turtle.hideturtle()
    thinking_turtle.penup()
    thinking_turtle.goto(-300, 300)
    thinking_turtle.color("red")
    thinking_turtle.write("AI 思考中...", font=("Arial", 16, "bold"))
    screen.update()
    
    try:
        # 首先检查快速获胜/防守
        quick_result = get_quick_move()
        if quick_result:
            row, col, ai_color = quick_result
            if board[row][col] is None:
                board[row][col] = ai_color
                draw_piece(row, col, ai_color)
                if check_win(row, col):
                    game_over = True
                    winner = "AI（黑棋）" if ai_color == "black" else "AI（白棋）"
                    turtle.textinput("游戏结束", f"{winner}获胜！")
                    reset_game()
                thinking_turtle.clear()
                ai_thinking = False
                return
        
        # 转换棋盘格式
        ai_board = convert_board_for_ai()
        
        # 计算已下棋子数，动态调整搜索深度
        piece_count = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] is not None)
        
        if piece_count < 10:
            search_depth = 1
            max_nodes = 10000
        elif piece_count < 30:
            search_depth = 2
            max_nodes = 20000
        else:
            search_depth = 2
            max_nodes = 30000
        
        # 创建根节点
        root = Node(ai_board, Point(7, 7), 0, -10**9, 10**9, True, True)
        root.Score = 0
        
        # 创建AI搜索对象
        ai_searcher = AI1Step(max_node_num=max_nodes)
        ai_searcher.MethodTree.append(root)
        ai_searcher.NextNodeList.append(-1)
        
        # 执行搜索
        ai_searcher.Search(0, search_depth)
        
        # 获取最佳落子位置
        best_move = ai_searcher.GetFinalRes()
        
        if best_move:
            row, col = best_move.X, best_move.Y
            ai_color = "black" if not player_first else "white"
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row][col] is None:
                board[row][col] = ai_color
                draw_piece(row, col, ai_color)
                if check_win(row, col):
                    game_over = True
                    winner = "AI（黑棋）" if ai_color == "black" else "AI（白棋）"
                    turtle.textinput("游戏结束", f"{winner}获胜！")
                    reset_game()
            else:
                fallback_move()
        else:
            fallback_move()
    
    except Exception as e:
        print(f"AI错误: {e}")
        fallback_move()
    finally:
        thinking_turtle.clear()
        ai_thinking = False

def ai_move():
    """统一的AI落子入口（非阻塞）"""
    global current_player, ai_thinking
    
    if game_over or game_mode != "human_vs_ai":
        return
    
    # 确定当前应该是谁走棋
    expected_current = "black" if not player_first else "white"
    
    if current_player != expected_current or ai_thinking:
        return
    
    screen.ontimer(lambda: execute_ai_move(), 10)

def execute_ai_move():
    """执行AI移动"""
    global current_player, game_over
    
    if game_over or game_mode != "human_vs_ai":
        return
    
    ai_move_advanced()
    
    if not game_over:
        # 切换到玩家
        current_player = "white" if not player_first else "black"
        screen.listen()

# ===================== 游戏核心逻辑 =====================
def click_handler(x, y):
    global game_over, current_player, ai_thinking
    
    # 检查是否可以进行落子
    if game_over or not user_info["logged_in"] or menu_running:
        return
    
    # 人机模式下，AI思考时玩家不能落子
    if game_mode == "human_vs_ai" and (ai_thinking):
        return
    
    # 确定玩家应该是什么颜色
    player_color = "black" if player_first else "white"
    
    # 人机模式下，检查是否轮到玩家
    if game_mode == "human_vs_ai" and current_player != player_color:
        return

    coords = get_coords(x, y)
    if not coords:
        return
    row, col = coords

    if board[row][col] is None:
        # 禁手检查（只有黑棋需要检查）
        if current_player == "black" and is_forbidden_move(row, col, "black"):
            turtle.textinput("提示", "该位置是禁手，不能落子！")
            screen.listen()
            return

        # 玩家落子
        board[row][col] = current_player
        draw_piece(row, col, current_player)

        if check_win(row, col):
            game_over = True
            if game_mode == "human_vs_human":
                winner_text = "黑棋" if current_player == "black" else "白棋"
                winner_text += "获胜！"
            else:
                if current_player == "black":
                    winner_text = "你（黑棋）获胜！" if player_first else "AI（黑棋）获胜！"
                else:
                    winner_text = "你（白棋）获胜！" if not player_first else "AI（白棋）获胜！"
            turtle.textinput("游戏结束", winner_text)
            reset_game()
            screen.listen()
            return

        # 切换玩家
        if game_mode == "human_vs_human":
            current_player = "white" if current_player == "black" else "black"
        else:
            # 人机模式，切换到AI
            current_player = "black" if not player_first else "white"
            screen.update()
            ai_move()

def reset_game():
    global board, current_player, game_over, ai_thinking, player_first
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    # 根据先手设置重置当前玩家
    if game_mode == "human_vs_ai":
        if player_first:
            # 玩家先手：玩家黑棋，AI白棋
            current_player = "black"
        else:
            # AI先手：AI黑棋，玩家白棋
            current_player = "black"  # AI先手，所以当前玩家是黑棋（AI）
            # 延迟执行AI移动
            if not game_over:
                screen.ontimer(lambda: execute_ai_move(), 100)
    else:
        current_player = "black"
    
    game_over = False
    ai_thinking = False
    
    # 清除所有棋子
    for turtle_obj in screen.turtles():
        if turtle_obj != pen:
            turtle_obj.clear()
            turtle_obj.hideturtle()
    draw_board()
    screen.update()

def logout_user():
    global user_info, menu_running, game_mode, ai_thinking
    user_info["username"] = ""
    user_info["logged_in"] = False
    game_mode = ""
    menu_running = True
    ai_thinking = False
    reset_game()
    turtle.textinput("提示", "已成功登出！")
    screen.listen()
    main_menu()

def choose_game_mode():
    global game_mode
    while True:
        mode_choice = turtle.textinput(
            "选择游戏模式",
            "1. 双人对战\n2. 人机对战\n请选择（1/2）："
        )
        if not mode_choice:
            continue
        if mode_choice == "1":
            game_mode = "human_vs_human"
            turtle.textinput("提示", "已选择双人对战模式！")
            screen.listen()
            break
        elif mode_choice == "2":
            choose_first_move()
            break
        else:
            turtle.textinput("提示", "输入无效，请选择1或2！")
            screen.listen()

def choose_first_move():
    """选择人机对战的先手后手"""
    global player_first, game_mode
    
    while True:
        choice = turtle.textinput(
            "选择先手后手",
            "请选择：\n1. 玩家先手（玩家黑棋，AI白棋）\n2. AI先手（AI黑棋，玩家白棋）\n请选择（1/2）："
        )
        if not choice:
            continue
        if choice == "1":
            player_first = True
            game_mode = "human_vs_ai"
            turtle.textinput("提示", "已选择人机对战模式，玩家先手（玩家黑棋，AI白棋）！")
            break
        elif choice == "2":
            player_first = False
            game_mode = "human_vs_ai"
            turtle.textinput("提示", "已选择人机对战模式，AI先手（AI黑棋，玩家白棋）！")
            break
        else:
            turtle.textinput("提示", "输入无效，请选择1或2！")
            screen.listen()
    
    screen.listen()

def register_user():
    username = turtle.textinput("用户注册", "请输入用户名：")
    if not username:
        screen.listen()
        return
    password = turtle.textinput("用户注册", "请输入密码：")
    if not password:
        screen.listen()
        return
    users = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    if username in users:
        turtle.textinput("提示", "用户名已存在！")
    else:
        users[username] = password
        with open("users.json", "w") as f:
            json.dump(users, f)
        turtle.textinput("提示", "注册成功！")
    screen.listen()

def login_user():
    username = turtle.textinput("用户登录", "请输入用户名：")
    if not username:
        screen.listen()
        return
    password = turtle.textinput("用户登录", "请输入密码：")
    if not password:
        screen.listen()
        return
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
        if username in users and users[username] == password:
            user_info["username"] = username
            user_info["logged_in"] = True
            turtle.textinput("提示", "登录成功！")
            draw_board()
        else:
            turtle.textinput("提示", "用户名或密码错误！")
    else:
        turtle.textinput("提示", "暂无存档，请先注册！")
    screen.listen()

def save_game():
    if not user_info["logged_in"] or game_over:
        turtle.textinput("提示", "无法保存（未登录/游戏结束）！")
        screen.listen()
        return
    save_data = {
        "username": user_info["username"],
        "board": board,
        "current_player": current_player,
        "game_mode": game_mode,
        "player_first": player_first,
        "save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(save_file, "w") as f:
        json.dump(save_data, f)
    turtle.textinput("提示", "存档成功！")
    screen.listen()

def load_game():
    if not user_info["logged_in"]:
        turtle.textinput("提示", "请先登录！")
        screen.listen()
        return
    if os.path.exists(save_file):
        with open(save_file, "r") as f:
            save_data = json.load(f)
        if save_data["username"] != user_info["username"]:
            turtle.textinput("提示", "该存档不属于当前用户！")
            screen.listen()
            return
        global board, current_player, game_over, game_mode, player_first
        board = save_data["board"]
        current_player = save_data["current_player"]
        game_mode = save_data["game_mode"]
        player_first = save_data.get("player_first", True)
        game_over = False
        for turtle_obj in screen.turtles():
            if turtle_obj != pen:
                turtle_obj.clear()
                turtle_obj.hideturtle()
        draw_board()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == "black":
                    draw_piece(r, c, BLACK)
                elif board[r][c] == "white":
                    draw_piece(r, c, WHITE)
        mode_text = "双人对战" if game_mode == "human_vs_human" else "人机对战"
        first_text = ""
        if game_mode == "human_vs_ai":
            first_text = f"，{'玩家先手（玩家黑棋）' if player_first else 'AI先手（AI黑棋）'}"
        turtle.textinput("提示", f"读档成功！当前模式：{mode_text}{first_text}")
    else:
        turtle.textinput("提示", "暂无存档！")
    screen.listen()

def game_menu():
    global menu_running, game_over
    
    if menu_running:
        menu_running = False
        screen.onkeypress(game_menu, "Escape")
        screen.listen()
        return
    
    menu_running = True
    screen.onkeypress(None, "Escape")
    
    choice = turtle.textinput(
        "五子棋游戏 - 游戏菜单",
        f"当前登录：{user_info['username']}\n请选择操作：\n"
        "1. 切换游戏模式\n2. 重新开始游戏\n"
        "3. 保存存档\n4. 读取存档\n"
        "5. 用户登录/切换账号\n6. 登出账号\n"
        "7. 退出游戏\n8. 返回游戏"
    )
    
    if not choice:
        choice = "8"
    
    if choice == "1":
        if user_info["logged_in"]:
            choose_game_mode()
            reset_game()
        else:
            turtle.textinput("提示", "请先登录！")
    elif choice == "2":
        reset_game()
        turtle.textinput("提示", "游戏已重新开始！")
    elif choice == "3":
        save_game()
    elif choice == "4":
        load_game()
    elif choice == "5":
        login_user()
    elif choice == "6":
        logout_user()
        menu_running = False
        screen.onkeypress(main_menu, "Escape")
        screen.listen()
        return
    elif choice == "7":
        screen.bye()
        exit()
    elif choice == "8":
        pass
    else:
        turtle.textinput("提示", "输入无效，请选择1-8！")
    
    menu_running = False
    screen.onkeypress(game_menu, "Escape")
    screen.listen()

def main_menu():
    global menu_running
    screen.onkeypress(lambda: screen.bye(), "Escape")

    while menu_running:
        choice = turtle.textinput(
            "五子棋游戏 - 主菜单",
            "请选择操作：\n1. 用户注册\n2. 用户登录")
        if not choice:
            continue
        if choice == "1":
            register_user()
        elif choice == "2":
            login_user()
            if user_info["logged_in"]:
                secondary_menu()
        else:
            turtle.textinput("提示", "输入无效，请选择1或2！")
            screen.listen()

def secondary_menu():
    global menu_running
    
    while menu_running:
        choice = turtle.textinput(
            "五子棋游戏 - 主菜单",
            "请选择操作：\n1. 选择游戏模式并开始\n2. 退出游戏")
        if not choice:
            continue
        if choice == "1":
            choose_game_mode()
            menu_running = False
            reset_game()
            screen.onkeypress(game_menu, "Escape")
            screen.listen()
        elif choice == "2":
            screen.bye()
            exit()

# ===================== 程序入口 =====================
if __name__ == "__main__":
    screen.onclick(click_handler)
    main_menu()
    screen.mainloop()