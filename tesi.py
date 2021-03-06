# -*- coding: utf-8 -*-
"""Tesi.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1i757L_cQY_4v_FRhSzI7hc6nKxhd3baI
"""

import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from timeit import default_timer as timer
from torch.utils.data import Subset
import os
import sys
import random
import copy
from torch.backends import cudnn

# associo cuda per lavorare ulla gpu
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# Assuming that we are on a CUDA machine, this should print a CUDA device:

print(device)

transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=transform)
# trovo gli indici e salvo una lista per ciascuno
airplane_indices, automobile_indices = [], []
bird_indices, other_indices = [], []
cat_indices, deer_indices = [], []

airplane_idx = trainset.class_to_idx['airplane']
automobile_idx = trainset.class_to_idx['automobile']
bird_idx = trainset.class_to_idx['bird']
cat_idx = trainset.class_to_idx['cat']
deer_idx = trainset.class_to_idx['deer']


def train_split(trainset):
    for i in range(len(trainset)):
        current_class = trainset[i][1]
        if current_class == automobile_idx:
            automobile_indices.append(i)
        elif current_class == deer_idx:
            deer_indices.append(i)
        elif current_class == airplane_idx:
            airplane_indices.append(i)
        elif current_class == bird_idx:
            bird_indices.append(i)
        elif current_class == cat_idx:
            cat_indices.append(i)
        else:
            other_indices.append(i)
    new_trainset1 = Subset(trainset, airplane_indices + automobile_indices  + cat_indices + deer_indices + bird_indices)
    new_trainset2 = Subset(trainset, other_indices)
    return new_trainset1, new_trainset2


trainset1, trainset2 = train_split(trainset)
#random.shuffle(trainset1)
#random.shuffle(trainset2)

trainloaderA = torch.utils.data.DataLoader(trainset1, batch_size=128,
                                           shuffle=True, num_workers=0)
trainloaderB = torch.utils.data.DataLoader(trainset2, batch_size=128,
                                           shuffle=True, num_workers=0)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=128,
                                          shuffle=True, num_workers=0)

testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=128,
                                         shuffle=True, num_workers=0)

classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')


def imshow(img):
    img = img / 2 + 0.5  # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 5)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


"""
class Net1(nn.Module):
    def __init__(self):
        super(Net1, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 5)
        self.fc4 =nn.Linear (5,5)
        self.fc4.bias.data=torch.zeros(fc4.bias.size())
        self.fc4.weight.data=torch.randn(m.weight.size())*.01


    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x
"""
net = Net().to(device)

print("Allocated:", round(torch.cuda.memory_allocated(0) / 10243, 1), "GB")
print("rete creata")


# metodo per eseguire il test
def train(trainloader,optimizer,criterion,net):
    for epoch in range(20):  # loop over the dataset multiple times
        start = timer()
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data[0].to(device), data[1].to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            if i % 2000 == 1999:  # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0
        end = timer()
        print("Tempo di una epoca: ", (end - start), "sec")
    print('Finished Training')


# metodo per eseguire il test
def test(testloader,net):
    # accuracy dell'intero network
    correct = 0
    total = 0
    with torch.no_grad():
        for data in testloader:
            images, labels = data[0].to(device), data[1].to(device)
            outputs = net(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print('Accuracy of the network on the 10000 test images: %d %%' % (
            100 * correct / total))

    # quale classe ha la migliore performance
    class_correct = list(0. for i in range(10))
    class_total = list(0. for i in range(10))
    with torch.no_grad():
        for data in testloader:
            images, labels = data[0].to(device), data[1].to(device)
            outputs = net(images)
            _, predicted = torch.max(outputs, 1)
            c = (predicted == labels).squeeze()
            for i in range(4):
                label = labels[i]
                class_correct[label] += c[i].item()
                class_total[label] += 1

    for i in range(10):
        print('Accuracy of %5s : %2d %%' % (
            classes[i], 100 * class_correct[i] / class_total[i]))


criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
cudnn.benchmark = True

# eseguo train
train(trainloaderA,optimizer,criterion,net)

test(testloader,net)

PATH = './cifar_net.pth'
torch.save(net.state_dict(),PATH )
#torch.save(optimizer.state_dict(), PATH)

#fc4.weight.data=torch.randn(fc4.weight.size())*.01 #Random weight initialisation
#fc4.bias.data=torch.zeros(fc4.bias.size())
net.load_state_dict(torch.load(PATH), strict=False)
#optimizer.load_state_dict(torch.load(PATH))
net.eval()
"""
# net = Net()
net_dict = net.state_dict()
net1 = Net()
net1.to(device)
net1_dict = net1.state_dict()
pretrained_dict = net_dict
model_dict = net1_dict
# 1. filter out unnecessary keys
pretrained_dict = {k: v for k, v in net_dict.items() if k in model_dict}
# 2. overwrite entries in the existing state dict
model_dict.update(net_dict)
# 3. load the new state dict
net1.load_state_dict(model_dict)
net1 = net1.eval()
"""

#for param in net.parameters():
#   param.requires_grad = False


# Parameters of newly constructed modules have requires_grad=True by default

#net1.fc4.weight.data=torch.randn(net1.fc4.weight.size())*.01 #Random weight initialisation
#net1.fc3.bias.data=torch.zeros(net1.fc3.bias.size())

net.fc3 = nn.Linear(84,10)
net.add_module("fc4",nn.Linear(84,10))  
net.fc4.weight.data = torch.randn(net.fc4.weight.size())*.01
net = net.to(device)

# Observe that only parameters of final layer are being optimized as
# opposed to before.
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
criterion = nn.CrossEntropyLoss()

train(trainloaderB,optimizer,criterion, net)

# eseguo test
test(testloader,net)