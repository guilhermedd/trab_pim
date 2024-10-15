import pickle
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt
from voxel import Voxel

class Segmentation:
    def __init__(self):
        self._model_path        = "volume_TAC"
        self._data              = self.get_data()
        self._proliferativas    = 0 # 255
        self._quiescentes       = 0 # 200
        self._necroticas        = 0 # 140
        self._all_data          = []
        self.visited_cells      = []
        self._pro_group         = []
        self._qui_group         = []
        self._nec_group         = []
        self.get_cells()


    def get_data(self):
        with open(self._model_path, "rb") as f:
            return pickle.load(f)


    def get_cells(self):
        # Supondo que os dados são tridimensionais (por exemplo, 101x101x101)
        for z in range(len(self._data)):
            for y in range(len(self._data[z])):
                for x in range(len(self._data[z][y])):
                    value = self._data[z][y][x]
                    self.visited_cells.append(Voxel(x, y, z, value))
                    if value == 255:
                        self._proliferativas += 1
                    elif value == 200:
                        self._quiescentes += 1
                    elif value == 140:
                        self._necroticas += 1

        self.connect_6()


    def plot_3d(self):
        # Definir a fatia no eixo z
        z_index = 50
        slice_data = self._data[z_index, :, :]

        # Criar a grade para x e y
        x = np.arange(slice_data.shape[0])
        y = np.arange(slice_data.shape[1])
        X, Y = np.meshgrid(x, y)

        # Criar o gráfico wireframe
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(X, Y, slice_data)

        # Configurar os rótulos dos eixos
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Valores')

        plt.show()


    def slice_plot(self, pause_time=500):
        # Verificar o formato dos dados
        if self._data.ndim != 3:
            raise ValueError("Os dados não têm a forma esperada de um volume 3D")

        num_slices = self._data.shape[0]

        fig, ax = plt.subplots()
        c = ax.pcolormesh(np.arange(self._data.shape[1]), np.arange(self._data.shape[2]), self._data[0])
        ax.axis('off')  # Ocultar os eixos

        # Configurar a barra de cores
        fig.colorbar(c, ax=ax)

        # Atualizar a função de animação
        def update(frame):
            ax.clear()  # Limpar os eixos
            c = ax.pcolormesh(np.arange(self._data.shape[1]), np.arange(self._data.shape[2]), self._data[frame])
            ax.axis('off')  # Ocultar os eixos
            ax.set_title(f'Fatia {frame + 1} de {num_slices}')  # Título
            return c,

        # Criar a animação
        ani = FuncAnimation(fig, update, frames=num_slices, interval=pause_time)

        plt.show()  # Exibir a figura


    def save_slice(self, count, title, filename, X, Y):
        fig, ax = plt.subplots()
        c = ax.pcolormesh(np.arange(X), np.arange(Y), count[1])
        ax.axis('off')
        fig.colorbar(c, ax=ax)
        plt.title(title)
        plt.savefig(filename)
        plt.close(fig)


    def save_highest(self):
        highest_counts = {
            'proliferativas': (0, None),  # (count, slice)
            'quiescentes': (0, None),
            'necroticas': (0, None)
        }

        X = self._data.shape[1]  # Largura da fatia
        Y = self._data.shape[2]  # Altura da fatia

        for z in self._data:
            proliferativas = np.sum(z == 255)
            quiescentes = np.sum(z == 200)
            necroticas = np.sum(z == 140)

            if proliferativas > highest_counts['proliferativas'][0]:
                highest_counts['proliferativas'] = (proliferativas, z)

            if quiescentes > highest_counts['quiescentes'][0]:
                highest_counts['quiescentes'] = (quiescentes, z)

            if necroticas > highest_counts['necroticas'][0]:
                highest_counts['necroticas'] = (necroticas, z)

        if highest_counts['proliferativas'][1] is not None:
            self.save_slice(highest_counts['proliferativas'], f'Fatia com mais células proliferativas: {highest_counts['proliferativas'][0]}', 'results/proliferativas.png', X, Y)
        if highest_counts['quiescentes'][1] is not None:
            self.save_slice(highest_counts['quiescentes'], f'Fatia com mais células quiescentes: {highest_counts['quiescentes'][0]}', 'results/quiescentes.png', X, Y)
        if highest_counts['necroticas'][1] is not None:
            self.save_slice(highest_counts['necroticas'], f'Fatia com mais células necróticas: {highest_counts['necroticas'][0]}', 'results/necroticas.png', X, Y)


    def connect_6(self):
        neighbors = [
            (1, 0, 0),      # Direita
            (-1, 0, 0),     # Esquerda
            (0, 1, 0),      # Cima
            (0, -1, 0),     # Baixo
            (0, 0, 1),      # Frente
            (0, 0, -1)      # Trás
        ]
        for cell in self.visited_cells:
            for neighbor in neighbors:
                new_x, new_y, new_z = cell.x + neighbor[0], cell.y + neighbor[1], cell.z + neighbor[2]
                try:
                    cell[0].neighbors.append(self.visited_cells[new_z][new_y][new_x])
                except:
                    pass

    def get_groups(self):
        for cell in self.visited_cells:
            if not cell.was_visited and cell.value > 0:
                group_size = cell.get_group()
                if cell.value == 255:
                    self._pro_group.append(group_size)
                elif cell.value == 200:
                    self._qui_group.append(group_size)
                else:
                    self._nec_group.append(group_size)

    def __str__(self):
        return f"Proliferativas: {self._proliferativas}\nQuiescentes: {self._quiescentes}\nNecroticas: {self._necroticas}"