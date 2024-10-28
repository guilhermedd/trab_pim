import pickle
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt
from voxel import Voxel

class Segmentation:
    def __init__(self):
        self._model_path        = "volume_TAC"
        self._data              = self.get_data()
        self._proliferativas    = 0 # Células com valor 255
        self._quiescentes       = 0 # Células com valor 200
        self._necroticas        = 0 # Células com valor 140
        self._all_data          = []
        self.visited_cells      = []
        self._pro_group         = []
        self._qui_group         = []
        self._nec_group         = []
        self.get_cells()


    def get_data(self):
        # Carrega os dados da tomografia simulada (matriz numpy 3D) a partir de um arquivo pickle
        with open(self._model_path, "rb") as f:
            return pickle.load(f)


    def get_cells(self):
        # Processa os dados tridimensionais e armazena as informações de cada voxel
        for z in range(len(self._data)):
            y_group = []
            for y in range(len(self._data[z])):
                x_group = []
                for x in range(len(self._data[z][y])):
                    value = self._data[z][y][x]
                    x_group.append(Voxel(x, y, z, value))
                    if value == 255:
                        self._proliferativas += 1
                    elif value == 200:
                        self._quiescentes += 1
                    elif value == 140:
                        self._necroticas += 1
                y_group.append(x_group)
            self.visited_cells.append(y_group)
        self.connect_6()
        self.get_groups()

    def plot_3d(self):
        # Visualização de uma fatia do volume tomográfico
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
        # Animação da visualização das fatias do volume tomográfico
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

    def save_highest(self):
        # Salva os maiores agrupamentos de cada tipo de célula com visualização de conexões
        for group, filename, color, cell_type in [
            (self._pro_group, "max_proliferativas.png", 'r', "Células Proliferativas"),
            (self._qui_group, "max_quiescentes.png", 'g', "Células Quiescentes"),
            (self._nec_group, "max_necroticas.png", 'b', "Células Necróticas")
        ]:
            largest_group = max(group, key=len)
            x, y, z = [], [], []
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            # Plotar os pontos individuais
            for cell in largest_group:
                x.append(cell.x)
                y.append(cell.y)
                z.append(cell.z)
            ax.scatter(x, y, z, c=color, marker='o')

            # Adicionar as conexões entre os pontos
            for cell in largest_group:
                for neighbor in cell.neighbors:
                    if neighbor in largest_group:  # Apenas conectar se ambos os voxels estiverem no grupo
                        x_line = [cell.x, neighbor.x]
                        y_line = [cell.y, neighbor.y]
                        z_line = [cell.z, neighbor.z]
                        ax.plot(x_line, y_line, z_line, color=color, alpha=0.5)

            ax.set_title(f'{cell_type} - Maior Agrupamento')
            ax.set_xlabel('Eixo X')
            ax.set_ylabel('Eixo Y')
            ax.set_zlabel('Eixo Z')
            plt.savefig(filename)

    def connect_6(self):
        # Define a vizinhança 3D usando conectividade-6
        neighbors = [
            (1, 0, 0),      # Direita
            (-1, 0, 0),     # Esquerda
            (0, 1, 0),      # Cima
            (0, -1, 0),     # Baixo
            (0, 0, 1),      # Frente
            (0, 0, -1)      # Trás
        ]
        for z in self.visited_cells:
            for y in z:
                for cell in y:
                    for neighbor in neighbors:
                        new_x, new_y, new_z = cell.x + neighbor[0], cell.y + neighbor[1], cell.z + neighbor[2]
                        try:
                            cell.neighbors.append(self.visited_cells[new_z][new_y][new_x])
                        except:
                            pass


    def get_groups(self):
        # Identifica os agrupamentos de células
        for z in self.visited_cells:
            for y in z:
                for cell in y:
                    if not cell.was_visited and cell.value > 0:
                        group_size = []
                        cell.get_group(group_size)
                        if cell.value == 255:
                            self._pro_group.append(group_size)
                        elif cell.value == 200:
                            self._qui_group.append(group_size)
                        else:
                            self._nec_group.append(group_size)
                        cell.was_visited = True

    def __str__(self):
        # Retorna um resumo dos dados processados
        return (f"Proliferativas: {self._proliferativas}, "
                f"com {len(self._pro_group)} grupos: {[len(x) for x in self._pro_group]}\n"
                f"Quiescentes: {self._quiescentes}, "
                f"com {len(self._qui_group)} grupos: {[len(x) for x in self._qui_group]}\n"
                f"Necroticas: {self._necroticas}, "
                f"com {len(self._nec_group)} grupos: {[len(x) for x in self._nec_group]}")
