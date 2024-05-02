import random
import tkinter as tk
from tkinter import *
import time

# Robot sınıfı, robotun hareketini ve ziyaret ettiği hücreleri takip eder
class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.history = []    # Robotun hareket geçmişini saklar
        self.visited = set()  # Ziyaret edilen hücreleri takip etmek için küme ekle

    def move_up(self):
        self.y -= 1

    def move_down(self):
        self.y += 1

    def move_right(self):
        self.x += 1

    def move_left(self):
        self.x -= 1

    # Robotun hareket edebileceği hücreleri döndürür
    def get_possible_moves(self, grid):
        moves = []
        if self.y > 0 and not grid.is_wall(self.x, self.y - 1):
            moves.append("up")
        if self.y < grid.height - 1 and not grid.is_wall(self.x, self.y + 1):
            moves.append("down")
        if self.x > 0 and not grid.is_wall(self.x - 1, self.y):
            moves.append("left")
        if self.x < grid.width - 1 and not grid.is_wall(self.x + 1, self.y):
            moves.append("right")
        return moves

    # Robotun bir sonraki hareketini belirler
    def get_next_move(self, grid):
        moves = self.get_possible_moves(grid)
        unvisited_moves = [move for move in moves if (
        self.x + (move == "right") - (move == "left"), self.y + (move == "down") - (move == "up")) not in self.visited]

        if unvisited_moves:  # Daha önce ziyaret edilmemiş hücrelere öncelik ver
            move = random.choice(unvisited_moves)
        elif moves:
            move = random.choice(moves)
        else:
            move = None

        return move



class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[False for _ in range(height)] for _ in range(width)]
        # Izgara Duvarları True,Boş Hücreleri False olarak tutuyor

    # Belirtilen koordinattaki hücreye duvar yerleştirir
    def place_wall(self, x, y):
        self.grid[x][y] = True

    # Belirtilen koordinattaki hücrenin duvar olup olmadığını kontrol eder
    def is_wall(self, x, y):
        return self.grid[x][y]

    def reset(self):
        self.grid = [[False for _ in range(self.height)] for _ in range(self.width)]



class Maze:
    #Grid sınıfını kullanarak bir labirent oluşturur
    # generate_random_walls() yöntemi, belirtilen sayıda duvarı rastgele hücrelere yerleştirir ve labirentin başlangıç ve bitiş noktaları arasında geçerli bir yol olup olmadığını kontrol eder.
    def __init__(self, grid):
        self.grid = grid

    def generate_random_walls(self, num_walls):
        while True:
            for _ in range(num_walls):
                x = random.randint(0, self.grid.width - 1)
                y = random.randint(0, self.grid.height - 1)
                self.grid.place_wall(x, y)

            if len(find_shortest_path(self.grid, (0, 0), (self.grid.width - 1, self.grid.height - 1))) > 0:
                break

            self.grid.reset()

#find_shortest_path() yöntemi bir başlangıç ve bitiş noktası verilen labirentin en kısa yolunu bulur.BFS algoritmasını kullanır.
# Başlangıç noktasıyla başlayarak, robotun mevcut konumundan hareket edebileceği hücreler arasında dolaşır.BFS algoritması, bitiş noktasına ulaşıldığında en kısa yolu döndürür.
def find_shortest_path(grid, start, end):
    queue = [start]
    visited = set()
    parent = {}

    while queue:
        current = queue.pop(0)
        if current == end:
            path = []
            while current != start:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            return path
        for move in Robot(current[0], current[1]).get_possible_moves(grid):
            if move == "up":
                neighbor = (current[0], current[1] - 1)
            elif move == "down":
                neighbor = (current[0], current[1] + 1)
            elif move == "left":
                neighbor = (current[0] - 1, current[1])
            elif move == "right":
                neighbor = (current[0] + 1, current[1])
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return []


# Uygulama arayüzünü tanımlayan sınıf
class Application(tk.Frame):
    def __init__(self, master=None, width=10, height=10, num_walls=20):
        # Uygulamanın başlatılması ve labirentin boyutlarının belirlenmesi.
        super().__init__(master)
        self.master = master
        self.grid = Grid(width, height)
        self.maze = Maze(self.grid)
        self.set_start_and_end()
        self.maze.generate_random_walls(num_walls)
        self.robot = Robot(*self.start)
        self.num_walls = num_walls
        self.exit_x, self.exit_y = self.end
        self.cell_size = 50
        self.canvas = tk.Canvas(self, width=width * self.cell_size, height=height * self.cell_size, bg="white")
        self.canvas.pack()
        self.obstacles = {}
        self.create_grid()
        self.result_label = tk.Label(self, text="", font=("Helvetica", 16))
        self.result_label.pack()
        self.show_button = tk.Button(self, text="Sonuç Göster", command=self.show)
        self.show_button.pack()

        self.show_shortest_path_button = tk.Button(self, text="En Kısa Yolu Göster", command=self.show_shortest_path)
        self.show_shortest_path_button.pack()

        self.change_maze_button = tk.Button(self, text="Labirent Değiştir", command=self.change_maze)
        self.change_maze_button.pack()


        self.run_button = tk.Button(self, text="Çalıştır", command=self.run)
        self.run_button.pack()


    def run(self):
        self.start_time = time.time()  # Süreyi ölçmeye başlar
        self.canvas.delete("all")
        self.create_grid()
        self.robot = Robot(*self.start)
        self.robot.history = []
        self.master.after(100, self.animate_robot)

    # Mevcut konumdan yapılabilecek olası hareketleri bulan ve rastgele bir hareket seçen yöntem
    def get_next_move(self, grid):
        moves = self.get_possible_moves(grid)
        unvisited_moves = [move for move in moves if (
        self.x + (move == "right") - (move == "left"), self.y + (move == "down") - (move == "up")) not in self.visited]

        if unvisited_moves:  # Daha önce ziyaret edilmemiş hücrelere öncelik ver
            move = random.choice(unvisited_moves)
        elif moves:
            move = random.choice(moves)
        else:
            move = None

        return move

    # Robotun etrafındaki bulutları kaldırır
    def remove_adjacent_clouds(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if 0 <= x + dx < self.grid.width and 0 <= y + dy < self.grid.height:
                    self.remove_cloud(x + dx, y + dy)

    # Robotun hareketlerini animasyonla gösteren fonksiyon
    def animate_robot(self):
        if (self.robot.x, self.robot.y) != (self.exit_x, self.exit_y):
            move = self.robot.get_next_move(self.grid)
            if move:
                self.robot.history.append((self.robot.x, self.robot.y))
                self.robot.visited.add((self.robot.x, self.robot.y))  # Ziyaret edilen hücreleri güncelle
                self.canvas.create_rectangle(self.robot.x * self.cell_size, self.robot.y * self.cell_size,
                                             (self.robot.x + 1) * self.cell_size, (self.robot.y + 1) * self.cell_size,
                                             fill="blue", tags="visited")


                if move == "up":
                    self.robot.move_up()
                elif move == "down":
                    self.robot.move_down()
                elif move == "right":
                    self.robot.move_right()
                elif move == "left":
                    self.robot.move_left()

                # Robotun etrafındaki bulutları temizler
                self.remove_adjacent_clouds(self.robot.x, self.robot.y)

            elif self.robot.history:
                self.robot.x, self.robot.y = self.robot.history.pop()
            else:
                return
            self.canvas.create_rectangle(self.robot.x * self.cell_size, self.robot.y * self.cell_size,
                                         (self.robot.x + 1) * self.cell_size, (self.robot.y + 1) * self.cell_size,
                                         fill="red", tags="robot")
            self.master.after(100, self.animate_robot)
        else:
            self.show_shortest_path()

            elapsed_time = time.time() - self.start_time  # Süreyi ölçer
            self.result_label.config(text=f"Robot Hedefe Ulaştı! Geçen süre: {elapsed_time:.2f} saniye")

            self.remove_all_clouds()

    # Labirentin üzerindeki tüm bulutları kaldıran yöntem.
    def remove_all_clouds(self):
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                self.remove_cloud(x, y)

    # Labirenti oluşturur
    def create_grid(self):
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                if self.grid.is_wall(x, y):
                    self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size,
                                                 (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                                 fill="black", tags=f"cell-{x}-{y}")
                else:
                    self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size,
                                                 (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                                 fill="white", tags=f"cell-{x}-{y}")

                self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size,
                                             (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                             fill="gray", tags=f"cloud-{x}-{y}")

        # Robotun başlangıç rengini kırmızı yapar
        robot_color = "red"
        self.canvas.create_rectangle(self.robot.x * self.cell_size, self.robot.y * self.cell_size,
                                     (self.robot.x + 1) * self.cell_size, (self.robot.y + 1) * self.cell_size,
                                     fill=robot_color, tags="robot")

        self.remove_cloud(self.robot.x, self.robot.y)

    # Belirli bir hücredeki bulutları kaldıran yöntem.
    def remove_cloud(self, x, y):
        self.canvas.delete(f"cloud-{x}-{y}")

    # Başlangıç ve bitiş noktalarını belirleyen fonksiyon
    def set_start_and_end(self):
        diagonal_choice = random.choice([0, 1])
        if diagonal_choice == 0:
            self.start = (0, 0)
            self.end = (self.grid.width - 1, self.grid.height - 1)
        else:
            self.start = (self.grid.width - 1, 0)
            self.end = (0, self.grid.height - 1)
        self.robot = Robot(*self.start)  # Update the robot position
        self.exit_x, self.exit_y = self.end

    # Robotun hareketlerini gösteren ve çıktıyı 'robot_output.txt' dosyasına yazan yöntem.
    def show(self):
        self.canvas.delete("all")
        self.create_grid()
        self.robot = Robot(*self.start)
        self.robot.history = []
        visited_cells = []
        while (self.robot.x, self.robot.y) != (self.exit_x, self.exit_y):
            moves = self.robot.get_possible_moves(self.grid)
            if moves:
                move = random.choice(moves)
                self.robot.history.append((self.robot.x, self.robot.y))
                visited_cells.append((self.robot.x, self.robot.y))
                self.canvas.create_rectangle(self.robot.x * self.cell_size, self.robot.y * self.cell_size,
                                             (self.robot.x + 1) * self.cell_size, (self.robot.y + 1) * self.cell_size,
                                             fill="red")
                if move == "up":
                    self.robot.move_up()
                elif move == "down":
                    self.robot.move_down()
                elif move == "right":
                    self.robot.move_right()
                elif move == "left":
                    self.robot.move_left()
            elif self.robot.history:
                self.robot.x, self.robot.y = self.robot.history.pop()
            else:
                break

        self.show_shortest_path()
        self.result_label.config(text="Robot Hedefe Ulaştı!")
        self.remove_all_clouds()
        # Sırasıyla gezdiği kareler ve bulduğu en kısa yolun kaydedilmesi

        shortest_path = find_shortest_path(self.grid, self.start, self.end)
        with open("robot_output.txt", "w") as f:

            f.write("\nRobotun Bulduğu En Kısa Yol:\n")
            for cell in shortest_path:
                f.write(f"{cell}\n")

        self.result_label.config(text="Robot Hedefe Ulaştı! Sonuçlar 'robot_output.txt' dosyasına kaydedildi.")

    # En kısa yolu gösteren fonksiyon
    def show_shortest_path(self):
        path = find_shortest_path(self.grid, self.start, self.end)

        for x, y in path:
            self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size,
                                         (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                         fill="green")
        self.result_label.config(text="Robot En Kısa Şekilde Hedefe Ulaştı!")
        self.remove_all_clouds()

    # Labirenti değiştiren fonksiyon
    def change_maze(self):
        self.canvas.delete("all")
        self.grid = Grid(self.grid.width, self.grid.height)
        self.maze = Maze(self.grid)
        self.set_start_and_end()
        self.maze.generate_random_walls(self.num_walls)
        self.robot = Robot(*self.start)
        self.create_grid()
        self.result_label.config(text="")

if __name__ == "__main__":
    # Uygulamanın başlatıldığı ana kısım.
    root = tk.Tk()
    root.title("Gezgin Robot")
    app = Application(root, width=10, height=10, num_walls=95)
    app.pack()
    root.mainloop()

