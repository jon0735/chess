import numpy as np
import nn_util


class NeuralNet:
    def __init__(self, W=None, b=None):
        if W is None: 
            self.W = []
        if b is None:
            self.b = []
        self.depth = len(self.b)

    def init_net(self, input_size=0, output_size=0, hidden_size=0, number_of_hidden=0):
        # print("\n\n")
        # print("Init called with inputsize = ", input_size, ", outputsize = ", output_size, ", hiddensize = ", hidden_size, ", number")
        if not (input_size and output_size and hidden_size and number_of_hidden):
            raise ValueError("Default values not handled. You need to set them manually")
        if number_of_hidden < 1:
            raise ValueError("NN not implemented for no hidden layers")

        w1 = np.random.normal(0, np.sqrt(2 / input_size), size=(input_size, hidden_size))
        self.W.append(w1)
        b1 = np.zeros(hidden_size)
        self.b.append(b1)

        for i in range(number_of_hidden - 1):
            wi = np.random.normal(0, np.sqrt(2 / hidden_size), size=(hidden_size, hidden_size))
            self.W.append(wi)
            bi = np.zeros(hidden_size)
            self.b.append(bi)

        wL = np.random.normal(0, np.sqrt(2 / hidden_size), size=(hidden_size, output_size))
        self.W.append(wL)
        bL = np.zeros(output_size)
        self.b.append(bL)
        self.depth = number_of_hidden + 2

    def predict(self, x):
        # print("\n\n")
        # print(x)
        # print("\n\n")
        a = x
        for i in range(self.depth - 2):
            z = np.dot(a, self.W[i]) + self.b[i]
            a = nn_util.relu(z)
        z = np.dot(a, self.W[-1]) + self.b[-1]
        a = nn_util.tanh(z)
        return a

    def forward_pass(self, x):
        a = [x]
        z = [x]
        for i in range(self.depth - 2):
            z_i = np.dot(a[-1], self.W[i]) + self.b[i]
            a_i = nn_util.relu(z_i)
            z.append(z_i)
            a.append(a_i)
        zL = np.dot(a[-1], self.W[-1]) + self.b[-1]
        aL = nn_util.tanh(zL)
        z.append(zL)
        a.append(aL)
        return z, a

    def cost_grad(self, x, real):
        z, a = self.forward_pass(x)
        cost = nn_util.mse(real, a[-1])
        output_error = np.multiply(nn_util.d_mse(real, a[-1]), nn_util.d_tanh(z[-1]))
        errors = [output_error]
        d_w = [np.outer(a[-2], output_error)]
        for i in range(len(self.b) - 1):
            error_weight_dot = np.dot(self.W[-(i + 1)], errors[-1])
            d_z = nn_util.d_relu(z[-(i + 2)])
            error_i = np.multiply(error_weight_dot, d_z)
            dw_i = np.outer(a[-(i + 3)], error_i)
            errors.append(error_i)
            d_w.append(dw_i)
        d_w.reverse()
        errors.reverse()

        return cost, {'dw': d_w, 'db': errors, 'out': a[-1]}

    def update_from_gradients(self, db, dw, lr=0.1):
        W = self.W
        b = self.b
        for i in range(len(W)):
            W[i] = W[i] + dw[i] * lr
            b[i] = b[i] + db[i] * lr

