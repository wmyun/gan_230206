from models.base import BaseModel, combine
import torch


class GAN(BaseModel):
    """
    There is a lot of patterned noise and other failures when using lightning
    """
    def __init__(self, hparams, train_loader, test_loader, checkpoints):
        BaseModel.__init__(self, hparams, train_loader, test_loader, checkpoints)

    @staticmethod
    def add_model_specific_args(parent_parser):
        return parent_parser

    def test_method(self, net_g, img):
        self.oriX = img[0]
        self.imgX0 = net_g(self.oriX)[0]
        return self.imgX0

    def generation(self):
        img = self.batch['img']
        self.oriX = img[0]
        self.oriY = img[1]
        self.imgX0 = self.net_g(self.oriX)[0]
        if self.hparams.cmb is not False:
            self.imgX0 = combine(self.imgX0, self.oriX, method=self.hparams.cmb)

    def backward_g(self, inputs):
        # ADV(X0, Y)+
        loss_g = 0
        loss_g += self.add_loss_adv(a=self.imgX0, net_d=self.net_d, coeff=1, truth=True, stacked=False)

        # L1(X0, Y)
        loss_g += self.add_loss_l1(a=self.imgX0, b=self.oriY, coeff=self.hparams.lamb)

        return {'sum': loss_g, 'loss_g': loss_g}

    def backward_d(self, inputs):
        loss_d = 0
        # ADV(X0, Y)-
        loss_d += self.add_loss_adv(a=self.imgX0, net_d=self.net_d, coeff=0.5, truth=False, stacked=False)

        # ADV(X, Y)+
        loss_d += self.add_loss_adv(a=self.oriY, net_d=self.net_d, coeff=0.5, truth=True, stacked=False)

        return {'sum': loss_d, 'loss_d': loss_d}



# CUDA_VISIBLE_DEVICES=1 python train.py --dataset FlyZ -b 16 --prj WpOp/sb256 --direction xyweak_xyorisb --resize 256 --engine pix2pixNS


# CUDA_VISIBLE_DEVICES=0 python train.py --dataset womac3 -b 16 --prj NS/GattNoL1 --direction aregis1_b --cropsize 256 --engine pix2pixNS --lamb 0 --netG attgan
# CUDA_VISIBLE_DEVICES=1 python train.py --dataset womac3 -b 16 --prj seg/NS_Gatt --direction amask_bmask --cropsize 256 --engine pix2pixNS --netG attgan

# CUDA_VISIBLE_DEVICES=1 python train.py --dataset kl3 -b 16 --prj NS/0 --direction badKL3afterreg_gooodKL3reg --cropsize 256 --engine pix2pixNS

# CUDA_VISIBLE_DEVICES=0 python train.py --dataset kl3 -b 16 --prj seg/res6L10 --direction badseg_goodseg --resize 384 --cropsize 256 --engine pix2pixNS --netG resnet_6blocks --lamb 0

# Residual
# CUDA_VISIBLE_DEVICES=0 python train.py --dataset womac3 -b 16 --prj N01/Unet32Res --direction aregis1_b --cropsize 256 --engine pix2pixNS --netG unet_32 --res --n01 --final sigmoid

# CUDA_VISIBLE_DEVICES=0,1,2 python train.py --jsn womac3 --prj NS/Gres6 --engine NS --direction areg_b --index --gray --netG resnet_6blocks --cmb mul --final sigmoid