# Federated Visual Classification (PyTorch): FedSGD, FedAvg, FedAvgM, FedIR, FedVC, FedProx
PyTorch implementation of Federated Learning algorithms FedSGD, FedAvg, FedAvgM, FedIR, FedVC and FedProx, applied to visual classification

## References
* [1] [Communication-Efficient Learning of Deep Networks from Decentralized Data](https://arxiv.org/abs/1602.05629): FedSGD, FedAvg
* [2] [Measuring the Effects of Non-Identical Data Distribution for Federated Visual Classification](https://arxiv.org/abs/1909.06335): FedAvgM, Synthetic Non-Identical Client Data
* [3] [Federated Visual Classification with Real-World Data Distribution](https://arxiv.org/abs/2003.08082): FedIR, FedVC
* [4] [Federated Optimization in Heterogeneous Networks](https://arxiv.org/abs/1812.06127): FedProx
* [5] [GhostNet: More Features from Cheap Operations](https://arxiv.org/pdf/1911.11907.pdf): GhostModule
* [6] [TensorFlow Convolutional Neural Network Tutorial (2016)](https://github.com/tensorflow/models/blob/86ecc9730d751c1f72e3bfecac958166390f4125/tutorials/image/cifar10/cifar10.py): LeNet5

## Requirements
* python 3.8.10
* matplotlib 3.4.3
* numpy 1.17.4
* torch 1.10.0
* torchinfo 1.6.3
* torchvision 0.11.1

## Usage
```python main.py [ARGUMENTS]```

### Federated setting arguments:
* ```--dataset {cifar10,fmnist,mnist}```:                                                                         dataset, place yours in datasets.py (default: ```cifar10```)
* ```--no_augment```:                                                                                             don't augment dataset (default: ```False```)
* ```--iid IID```:                                                                                                identicalness of client distributions, 'inf' for IID (default: ```inf```)
* ```--balance BALANCE```:                                                                                        balance of client distributions, 'inf' for balanced (default: ```inf```)
* ```--no_replace```:                                                                                             try to split the dataset among clients without replacement (default: ```False```)
* ```--hetero HETERO```:                                                                                          system heterogeneity (default: ```0```)

### Algorithm arguments:
* ```--rounds ROUNDS```:                                                                                          communication rounds (default: ```200```)
* ```--iters ITERS```:                                                                                            total iterations, overrides --rounds (default: ```None```)
* ```--num_clients NUM_CLIENTS, -K NUM_CLIENTS```:                                                                number of clients (default: ```100```)
* ```--frac_clients FRAC_CLIENTS, -C FRAC_CLIENTS```:                                                             fraction of clients selected at each round (default: ```0.1```)
* ```--epochs EPOCHS, -E EPOCHS```:                                                                               number of local epochs (or global epochs when --centralized) (default: ```5```)
* ```--train_bs TRAIN_BS, -B TRAIN_BS```:                                                                         training batch size (default: ```50```)
* ```--test_bs TEST_BS```:                                                                                        test and validation batch size (default: ```256```)
* ```--centralized```:                                                                                            use centralized algorithm (default: ```False```)
* ```--server_momentum SERVER_MOMENTUM```:                                                                        server momentum for FedAvgM algorithm, 0 for no FedAvgM (default: ```0```)
* ```--fedir```:                                                                                                  use FedIR algorithm (default: ```False```)
* ```--fedvc_nvc FEDVC_NVC```:                                                                                    virtual client size for FedVC, 0 for no FedVC (default: ```0```)
* ```--fedprox_mu FEDPROX_MU```:                                                                                  mu parameter for FedProx algorithm, 0 for no FedProx (default: ```0```)
* ```--drop_stragglers```:                                                                                        drop stragglers when --hetero > 0 (default: ```False```)
* ```--fedsgd```:                                                                                                 use FedSGD algorithm (default: ```False```)
* ```--server_lr SERVER_LR```:                                                                                    server learning rate (default: ```1```)

### Optimizer and scheduler arguments:
* ```--optim {adam,sgd}```:                                                                                       optimizer, place yours in optimizers.py (default: ```sgd```)
* ```--optim_args OPTIM_ARGS```:                                                                                  optimizer arguments (default: ```lr=0.01,momentum=0,weight_decay=4e-4```)
* ```--sched {const,fixed,plateau_loss,plateau_loss_avg,step}```:                                                 scheduler, place yours in schedulers.py (default: ```fixed```)
* ```--sched_args SCHED_ARGS```:                                                                                  scheduler arguments (default: ```None```)

### Model arguments:
* ```--model {cnn_cifar10,cnn_mnist,efficientnet,ghostnet,lenet5,lenet5_orig,mlp_mnist,mnasnet,mobilenet_v3}```:  model, place yours in models.py (default: ```lenet5```)
* ```--model_args MODEL_ARGS```:                                                                                  model arguments (default: ```ghost=True,norm=None```)
* ```--device {cuda:0,cpu}```:                                                                                    device to train, validate and test with (default: ```cuda:0```)

### Output arguments:
* ```--quiet, -q```:                                                                                              less verbose output (default: ```False```)
* ```--loss_every LOSS_EVERY```:                                                                                  print and log average loss every specified number of batches (default: ```0```)
* ```--acc_every ACC_EVERY```:                                                                                    print and log training, validation and test accuracies every specified number of batches (default: ```0```)
* ```--dir DIR```:                                                                                                custom tensorboard log directory (default: ```None```)
* ```--no_log```:                                                                                                 no tensorboard logs (default: ```False```)

### Other arguments:
* ```--help, -h```:                                                                                               show this help message and exit (default: ```False```)
* ```--seed SEED```:                                                                                              random seed (default: ```0```)
* ```--frac_valid FRAC_VALID```:                                                                                  fraction of the training set to use for validation (default: ```0```)

## Experiments
