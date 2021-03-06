import abc

import torchvision.transforms as T
import numpy as np

import albumentations as A
import albumentations.pytorch.transforms as AT


class AlbumentationTransforms:
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img):
        img = np.array(img)

        return self.transforms(image=img)["image"]


class AugmentationFactoryBase(abc.ABC):
    def build_transforms(self, train):
        return self.build_train() if train else self.build_test()

    @abc.abstractmethod
    def build_train(self):
        pass

    @abc.abstractmethod
    def build_test(self):
        pass


class MNISTTransforms(AugmentationFactoryBase):
    def build_train(self):
        return T.Compose([T.ToTensor(), T.Normalize((0.1307,), (0.3081,))])

    def build_test(self):
        return T.Compose([T.ToTensor(), T.Normalize((0.1307,), (0.3081,))])


class CIFAR10Transforms(AugmentationFactoryBase):
    def build_train(self):
        return T.Compose(
            [
                T.RandomCrop(32, padding=4),
                T.RandomHorizontalFlip(),
                T.ToTensor(),
                T.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
            ]
        )

    def build_test(self):
        return T.Compose(
            [
                T.ToTensor(),
                T.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
            ]
        )


class CIFAR10Albumentations(AugmentationFactoryBase):

    mean = (0.4914, 0.4822, 0.4465)
    std = (0.2023, 0.1994, 0.2010)

    def build_train(self):
        train_transforms = A.Compose(
            [
                A.PadIfNeeded(min_height=36, min_width=36),
                A.RandomCrop(height=32, width=32),
                A.HorizontalFlip(),
                A.Normalize(mean=self.mean, std=self.std),
                A.Cutout(num_holes=4),
                AT.ToTensor(),
            ]
        )

        return AlbumentationTransforms(train_transforms)

    def build_test(self):
        test_transforms = A.Compose(
            [A.Normalize(mean=self.mean, std=self.std), AT.ToTensor()]
        )

        return AlbumentationTransforms(test_transforms)


class TinyImageNetAlbumentations(AugmentationFactoryBase):

    mean = [0.4802, 0.4481, 0.3975]
    std = [0.2302, 0.2265, 0.2262]

    def build_train(self):
        train_transforms = A.Compose(
            [
                A.RandomCrop(64, 64),
                A.Rotate((-30.0, 30.0)),
                A.HorizontalFlip(),
                A.Normalize(mean=self.mean, std=self.std),
                A.Cutout(num_holes=4),
                AT.ToTensor(),
            ]
        )

        return AlbumentationTransforms(train_transforms)

    def build_test(self):
        test_transforms = A.Compose(
            [A.Normalize(mean=self.mean, std=self.std), AT.ToTensor()]
        )

        return AlbumentationTransforms(test_transforms)


class UnNormalize:
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, tensor):
        """
        UnNormalizes an image given its mean and standard deviation

        Args:
            tensor (Tensor): Tensor image of size (C, H, W) to be normalized.
        Returns:
            Tensor: Normalized image.
        """
        for t, m, s in zip(tensor, self.mean, self.std):
            t.mul_(s).add_(m)
            # The normalize code -> t.sub_(m).div_(s)
        return tensor
