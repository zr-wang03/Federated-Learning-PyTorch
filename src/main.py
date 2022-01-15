#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python version: 3.8.10


import copy
import time
import pickle
import numpy as np
from tqdm import tqdm

import torch
from tensorboardX import SummaryWriter

from options import args_parser
from update import LocalUpdate, test_inference
from models import MLP, CNNMnist, CNNFashion_Mnist, CNNCifar, LeNet5
from utils import get_datasets_splits, average_weights, exp_details


if __name__ == '__main__':
    # Start timer
    start_time = time.time() # TODO: time training only

    # Initialize logger
    logger = SummaryWriter('../logs')

    # Parse arguments
    args = args_parser()

    # Set device
    if args.gpu is not None:
        torch.cuda.set_device(args.gpu) # TODO: remove, usage is dicouraged
    device = 'cuda' if args.gpu is not None else 'cpu'

    # Load datasets and client splits
    train_dataset, test_dataset, train_splits, test_splits = get_datasets_splits(args)

    # Fake test splits. TODO: remove after implementation of real ones
    test_splits = {}
    for i in range(args.num_users):
        N = int(len(test_dataset)/args.num_users)
        test_splits[i] = list(range(i*N, (i+1)*N))

    # Load model to device
    if args.model == 'cnn':
        # Convolutional neural netork
        if args.dataset == 'mnist':
            global_model = CNNMnist(args=args)
        elif args.dataset == 'fmnist':
            global_model = CNNFashion_Mnist(args=args)
        elif args.dataset == 'cifar10':
            global_model = CNNCifar(args=args)
    elif args.model == 'mlp':
        # Multi-layer preceptron
        img_size = train_dataset[0][0].shape
        len_in = 1
        for x in img_size:
            len_in *= x
            global_model = MLP(dim_in=len_in, dim_hidden=64, dim_out=args.num_classes)
    elif args.model == 'lenet5':
        global_model = LeNet5()
    else:
        exit('Error: unrecognized model')
    global_model.to(device)

    # Print experimental details
    exp_details(args, global_model)

    # copy weights
    global_weights = global_model.state_dict()

    # Training
    train_loss = []
    print_every = 1

    if args.fedvc_nvc > 0:
        p = p = np.array([len(train_splits[user]) for user in train_splits])
        p = p / p.sum()
        print('p = %s' % p)

    for epoch in tqdm(range(args.epochs)):
        local_weights, local_losses, n_k = [], [], []
        #print(f'\n | Global Training Round : {epoch+1} |\n')

        global_model.train()
        m = max(int(args.frac * args.num_users), 1)
        if args.fedvc_nvc > 0:
            idxs_users = np.random.choice(range(args.num_users), m, replace=False, p=p)
        else:
            idxs_users = np.random.choice(range(args.num_users), m, replace=False)

        for idx in idxs_users:
            local_model = LocalUpdate(args=args, dataset=train_dataset, idxs=train_splits[idx], logger=logger)
            w, loss = local_model.update_weights(model=copy.deepcopy(global_model), global_round=epoch)

            if w is not None:
                local_weights.append(copy.deepcopy(w))
                local_losses.append(copy.deepcopy(loss))
                n_k.append(len(train_splits[idx]))

        if len(local_weights) > 0:
            # update global weights
            #n_k = [len(train_splits[idx_user]) for idx_user in idxs_users]
            global_weights = average_weights(local_weights, n_k)

            # update global weights
            #global_model.load_state_dict(global_weights)
            if epoch == 0:
                v = copy.deepcopy(global_model.state_dict())
                for key in v.keys():
                    v[key] -= global_weights[key]
            else:
                for key in v.keys():
                    v[key] = args.fedavgm_momentum * v[key] + global_model.state_dict()[key] - global_weights[key]
                    global_model.state_dict()[key] -= args.server_lr * v[key]

        loss_avg = sum(local_losses) / len(local_losses)
        train_loss.append(loss_avg)

        # Calculate avg training accuracy over all users at every epoch
        #list_acc, list_loss = [], []
        #global_model.eval()
        #for c in range(args.num_users):
        #    local_model = LocalUpdate(args=args, dataset=train_dataset,
        #                              idxs=train_splits[idx], logger=logger)
        #    acc, loss = local_model.inference(model=global_model)
        #    list_acc.append(acc)
        #    list_loss.append(loss)
        #train_accuracy.append(sum(list_acc)/len(list_acc))

        # print global training loss after every 'i' rounds
        if (epoch+1) % print_every == 0:
            print(f' \nAvg Training Stats after {epoch+1} global rounds:')
            print(f'Training Loss : {np.mean(np.array(train_loss))}')
            #print('Train Accuracy: {:.2f}% \n'.format(100*train_accuracy[-1]))

    # Test inference after completion of training
    test_acc, test_loss, test_avg_acc, test_avg_loss = test_inference(args, global_model, test_dataset, test_splits)

    print(f' \n Results after {args.epochs} global rounds of training:')
    #print("|---- Avg Train Accuracy: {:.2f}%".format(100*train_accuracy[-1]))
    print("|---- Test Accuracy: {:.2f}%".format(100*test_acc))
    print("|---- Test Loss: {:.6f}".format(test_loss))
    print("|---- Average Test Accuracy: {:.2f}%".format(100*test_avg_acc))
    print("|---- Average Test Loss: {:.6f}".format(test_avg_loss))

    # Saving the objects train_loss and train_accuracy:
    file_name = '../save/objects/{}_{}_{}_C[{}]_iid[{}]_E[{}]_B[{}].pkl'.\
        format(args.dataset, args.model, args.epochs, args.frac, args.iid,
               args.local_ep, args.local_bs)

    with open(file_name, 'wb') as f:
        #pickle.dump([train_loss, train_accuracy], f)
        pickle.dump([train_loss], f)

    print('\n Total Run Time: {0:0.4f}'.format(time.time()-start_time))

    # PLOTTING (optional)
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('Agg')

    # Plot Loss curve
    plt.figure()
    plt.title('Training Loss vs Communication rounds')
    plt.plot(range(len(train_loss)), train_loss, color='r')
    plt.ylabel('Training loss')
    plt.xlabel('Communication Rounds')
    plt.savefig('../save/fed_{}_{}_{}_C[{}]_iid[{}]_E[{}]_B[{}]_loss.png'.
                format(args.dataset, args.model, args.epochs, args.frac,
                       args.iid, args.local_ep, args.local_bs))

    # Plot Average Accuracy vs Communication rounds
    #plt.figure()
    #plt.title('Average Accuracy vs Communication rounds')
    #plt.plot(range(len(train_accuracy)), train_accuracy, color='k')
    #plt.ylabel('Average Accuracy')
    #plt.xlabel('Communication Rounds')
    #plt.savefig('../save/fed_{}_{}_{}_C[{}]_iid[{}]_E[{}]_B[{}]_acc.png'.
    #            format(args.dataset, args.model, args.epochs, args.frac,
    #                   args.iid, args.local_ep, args.local_bs))
